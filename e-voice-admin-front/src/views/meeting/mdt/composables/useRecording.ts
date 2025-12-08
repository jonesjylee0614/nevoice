import { computed, ref } from 'vue';
import { Message } from '@arco-design/web-vue';
import { saveDialog } from '../api';
import type { MeetingDialog, RecognizedStatus } from '../api/types';

// 音频配置 - 与 FunASR Demo 保持一致
const DEMO_CHUNK_INTERVAL = 10; // 与 demo 一致：10 块触发一次在线 ASR
const DEMO_CHUNK_SIZE = [5, 10, 5]; // 与 demo 一致
const DEMO_PCM_SAMPLES = 960; // 每次发送 960 样本 (16kHz -> ~60ms)
const PROCESSOR_BUFFER_SIZE = 1024; // 浏览器要求 2 的幂回调尺寸

export interface RecordingOptions {
  meetingId: number;
  onDialogReceived?: (dialog: Partial<MeetingDialog>) => void;
}

export function useRecording(options: RecordingOptions) {
  const recording = ref(false);
  const connecting = ref(false);
  const paused = ref(false);  // 暂停状态
  const errorMsg = ref('');
  const currentSeq = ref(0);

  // IME 聚合：确认文本 + 当前候选
  const committedText = ref('');
  const liveText = ref('');
  const runningText = computed(() => {
    if (paused.value) {
      return '⏸️ 录音已暂停';
    }
    if (committedText.value && liveText.value) {
      return `${committedText.value} ${liveText.value}`.trim();
    }
    return (committedText.value || liveText.value || '').trim();
  });

  // WebSocket 地址配置
  // VITE_API_PY_WS_HOST: 主服务（Flask-Sock 同步）默认 8210 端口
  const wsHost = (import.meta as any).env.VITE_API_PY_WS_HOST || 'ws://localhost:8210';

  let socket: WebSocket | null = null;
  let audioContext: AudioContext | null = null;
  let scriptProcessor: ScriptProcessorNode | null = null;
  let mediaStream: MediaStream | null = null;
  let pendingPcm: number[] = [];
  let sentChunkCount = 0;

  // 建立WebSocket连接
  const connect = (): Promise<boolean> => {
    return new Promise((resolve) => {
      try {
        socket = new WebSocket(`${wsHost}/ws/recognize`);
        socket.binaryType = 'arraybuffer';

        socket.onopen = () => {
          console.log('WebSocket 已连接');
          connecting.value = false;
          committedText.value = '';
          liveText.value = '';
          errorMsg.value = '';
          resolve(true);
        };

        socket.onmessage = async (event: MessageEvent) => {
          try {
            const data = JSON.parse(event.data);

            if (data.type === 'error') {
              stopRecording();
              errorMsg.value = data.message;
              return;
            }

            // 处理识别结果
            handleWSMessage(data);
          } catch (e) {
            console.error('解析消息失败:', e);
          }
        };

        socket.onclose = () => {
          console.log('WebSocket 已关闭');
        };

        socket.onerror = (error) => {
          console.error('WebSocket 错误:', error);
          errorMsg.value = '连接失败，请检查服务是否启动';
          connecting.value = false;
          resolve(false);
        };

        // 超时处理
        setTimeout(() => {
          if (socket && socket.readyState !== WebSocket.OPEN) {
            resolve(false);
          }
        }, 5000);
      } catch (e) {
        console.error('连接失败:', e);
        resolve(false);
      }
    });
  };

  // 处理WebSocket消息
  const handleWSMessage = async (data: any) => {
    // 兼容官方 FunASR Demo 格式
    if (!data.type && data.mode) {
      if (data.mode.includes('online')) {
        data.type = 'partial';
      } else if (data.mode.includes('offline')) {
        data.type = 'correction';
      }
    }

    const mode = data.mode || '';
    const text = data.text || '';

    if (data.type === 'partial' || mode.includes('online')) {
      // 在线流式结果 - 使用 text 字段（FunASR 增量模式）
      const state = data.text_state || {};
      const confirmed = (state.confirmed_text || '').trim();
      // 优先使用 text 字段（增量文本），累加到 liveText
      const newText = (text || state.candidate_text || '').trim();

      if (confirmed) {
        committedText.value = confirmed;
      }
      // 累加显示增量文本
      if (newText) {
        liveText.value += newText;
      }
    } else if (data.type === 'correction' || mode.includes('offline')) {
      // 离线纠错结果（带标点和ITN）- 这是最终结果，需要保存
      const state = data.text_state || {};
      const corrected = (text || state.confirmed_text || '').trim();

      if (corrected) {
        committedText.value = corrected;
        liveText.value = '';

        // 获取时间偏移和音频路径
        const startOffsetMs = data.start_offset_ms || 0;
        const endOffsetMs = data.end_offset_ms || 0;
        const durationMs = data.duration_ms || 0;
        const audioPath = data.audio_path || '';
        const speakerInfo = data.speaker_info || null;
        
        // 构建完整的音频URL（如果有）
        const pyHost = (import.meta as any).env.VITE_API_PY_HOST || 'http://localhost:8210';
        const fullAudioPath = audioPath ? `${pyHost}${audioPath}` : '';
        
        // 处理声纹匹配结果
        let speakerId: number | null = null;
        let speakerName = '未知发言人';
        let speakerRole = '';
        let recognized: RecognizedStatus = 0;
        let recognitionNote = '等待声纹匹配';
        let recognitionScore: number | undefined = undefined;
        
        if (speakerInfo && speakerInfo.recognized) {
          speakerId = speakerInfo.speaker_id;
          speakerName = speakerInfo.speaker_name || '未知';
          recognized = 1 as RecognizedStatus; // 声纹自动识别
          recognitionNote = speakerInfo.recognition_note || '声纹匹配成功';
          recognitionScore = speakerInfo.recognition_score;
        } else if (speakerInfo) {
          recognitionNote = speakerInfo.recognition_note || '声纹未匹配';
        }

        // 保存对话到数据库
        currentSeq.value += 1;
        const dialog: Partial<MeetingDialog> = {
          meetingId: options.meetingId,
          seq: currentSeq.value,
          speakerId,
          speakerName,
          speakerRole,
          recognized,
          recognitionNote,
          recognitionScore,
          speakTime: new Date().toISOString().replace('T', ' ').substring(0, 19),
          text: corrected,
          // 时间信息
          startOffset: startOffsetMs,
          endOffset: endOffsetMs,
          durationMs: durationMs,
          // 音频路径
          audioPath: fullAudioPath
        };

        // 通知父组件
        options.onDialogReceived?.(dialog);

        // 保存到后端
        try {
          await saveDialog(dialog);
        } catch (e) {
          console.error('保存对话失败:', e);
        }
      }
    } else if (data.type === 'final') {
      const state = data.text_state || {};
      const confirmed = (state.confirmed_text || text || '').trim();
      if (confirmed) {
        committedText.value = confirmed;
      }
      liveText.value = '';
    }
  };

  // 发送FunASR配置
  const sendConfig = () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;

    const payload = {
      mode: '2pass',
      chunk_interval: DEMO_CHUNK_INTERVAL,
      chunk_size: DEMO_CHUNK_SIZE,
      encoder_chunk_look_back: DEMO_CHUNK_SIZE[0],
      decoder_chunk_look_back: DEMO_CHUNK_SIZE[2],
      is_speaking: true,
      itn: true,
      wav_name: `meeting_${options.meetingId}`
    };

    try {
      socket.send(JSON.stringify(payload));
      console.log('已发送配置:', payload);
    } catch (e) {
      console.error('配置下发失败:', e);
    }
  };

  // 开始录音 - 使用浏览器原生API
  const startRecording = async () => {
    if (recording.value) return;

    connecting.value = true;
    
    // 先连接WebSocket
    const connected = await connect();
    if (!connected) {
      connecting.value = false;
      Message.error('连接服务器失败');
      return;
    }

    try {
      // 发送配置
      sendConfig();

      // 获取麦克风权限 - 使用与 voice/identify 相同的配置
      mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: { ideal: 16000, min: 8000, max: 48000 },
          channelCount: { ideal: 1, min: 1, max: 2 },
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      // 创建音频上下文
      audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
      const source = audioContext.createMediaStreamSource(mediaStream);

      // 重置缓冲
      pendingPcm = [];
      sentChunkCount = 0;

      // 创建音频处理器
      scriptProcessor = audioContext.createScriptProcessor(PROCESSOR_BUFFER_SIZE, 1, 1);
      scriptProcessor.onaudioprocess = (event: AudioProcessingEvent) => {
        // 如果未录音、WebSocket未连接或已暂停，则跳过
        if (!recording.value || !socket || socket.readyState !== WebSocket.OPEN || paused.value) return;
        
        const input = event.inputBuffer.getChannelData(0);

        // 转换为16位PCM
        for (let i = 0; i < input.length; i++) {
          const sample = input[i];
          const pcmValue = Math.round(sample * (sample < 0 ? 32768 : 32767));
          pendingPcm.push(pcmValue);
        }

        // 按 960 样本切片发送，与 demo 对齐
        while (pendingPcm.length >= DEMO_PCM_SAMPLES) {
          const chunk = pendingPcm.slice(0, DEMO_PCM_SAMPLES);
          pendingPcm = pendingPcm.slice(DEMO_PCM_SAMPLES);

          sentChunkCount += 1;
          if (sentChunkCount === 1) {
            console.log(`首包已发送，长度=${DEMO_PCM_SAMPLES} 样本`);
          }

          try {
            socket.send(Int16Array.from(chunk).buffer);
          } catch (e) {
            console.error('发送失败:', e);
          }
        }
      };

      source.connect(scriptProcessor);
      scriptProcessor.connect(audioContext.destination);

      // 发送开始信号
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'start' }));
      }
      
      recording.value = true;
      connecting.value = false;
      Message.success('录音已开始');
    } catch (e: any) {
      console.error('启动录音失败:', e);
      connecting.value = false;
      cleanupAudio();
      
      if (e.name === 'NotFoundError') {
        Message.error('未找到麦克风设备');
        errorMsg.value = '未找到麦克风设备，请检查设备连接';
      } else if (e.name === 'NotAllowedError') {
        Message.error('麦克风权限被拒绝');
        errorMsg.value = '请允许浏览器使用麦克风';
      } else {
        Message.error(`启动录音失败: ${e.message || '未知错误'}`);
        errorMsg.value = e.message || '启动录音失败';
      }
    }
  };

  // 清理音频资源
  const cleanupAudio = () => {
    if (scriptProcessor) {
      try {
        scriptProcessor.disconnect();
      } catch {}
      scriptProcessor.onaudioprocess = null as any;
      scriptProcessor = null;
    }
    if (audioContext) {
      try {
        if (audioContext.state !== 'closed') audioContext.close();
      } catch {}
      audioContext = null;
    }
    if (mediaStream) {
      try {
        mediaStream.getTracks().forEach(t => t.stop());
      } catch {}
      mediaStream = null;
    }
    sentChunkCount = 0;
    pendingPcm = [];
  };

  // 停止录音
  const stopRecording = () => {
    if (!recording.value) return;
    
    recording.value = false;
    connecting.value = false;
    paused.value = false;  // 重置暂停状态

    if (socket && socket.readyState === WebSocket.OPEN) {
      try {
        // 发送停止信号
        socket.send(JSON.stringify({ is_speaking: false }));
        socket.send(JSON.stringify({ type: 'end' }));
      } catch (e) {
        console.error('发送停止信号失败:', e);
      }

      setTimeout(() => {
        if (socket) {
          try {
            socket.close();
          } catch {}
          socket = null;
        }
      }, 500);
    }

    cleanupAudio();
    Message.info('录音已停止');
  };

  // 切换录音状态
  const toggleRecording = async () => {
    if (recording.value) {
      stopRecording();
    } else {
      await startRecording();
    }
  };

  // 暂停/恢复录音
  const togglePause = () => {
    if (!recording.value) return;
    
    paused.value = !paused.value;
    
    if (paused.value) {
      // 暂停时发送暂停信号给后端
      if (socket && socket.readyState === WebSocket.OPEN) {
        try {
          socket.send(JSON.stringify({ type: 'pause', is_speaking: false }));
        } catch (e) {
          console.error('发送暂停信号失败:', e);
        }
      }
      Message.info('录音已暂停');
    } else {
      // 恢复时发送恢复信号
      if (socket && socket.readyState === WebSocket.OPEN) {
        try {
          socket.send(JSON.stringify({ type: 'resume', is_speaking: true }));
        } catch (e) {
          console.error('发送恢复信号失败:', e);
        }
      }
      Message.success('录音已恢复');
    }
  };

  // 清理
  const cleanup = () => {
    stopRecording();
  };

  // 重置序号（清空对话后调用）
  const resetSeq = () => {
    currentSeq.value = 0;
    committedText.value = '';
    liveText.value = '';
    paused.value = false;
  };

  return {
    recording,
    connecting,
    paused,
    errorMsg,
    runningText,
    currentSeq,
    startRecording,
    stopRecording,
    toggleRecording,
    togglePause,
    cleanup,
    resetSeq
  };
}
