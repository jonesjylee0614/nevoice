<template>
  <ACard class="audio-upload-card" title="📁 上传音频文件测试">
    <template #extra>
      <ATag :color="isStreaming ? 'green' : 'gray'">
        {{ isStreaming ? '发送中...' : '就绪' }}
      </ATag>
    </template>

    <!-- 文件拖放区 -->
    <div
      class="drop-zone"
      :class="{ dragover: isDragOver, 'has-file': audioBuffer }"
      @click="triggerFileInput"
      @dragover.prevent="isDragOver = true"
      @dragleave.prevent="isDragOver = false"
      @drop.prevent="handleDrop"
    >
      <div class="drop-icon">{{ audioBuffer ? '📄' : '📁' }}</div>
      <div class="drop-text">
        {{ audioBuffer ? fileName : '拖放音频文件到这里，或点击选择' }}
      </div>
      <div v-if="!audioBuffer" class="drop-hint">支持 WAV, MP3, M4A 等格式</div>
      <input ref="fileInputRef" type="file" accept="audio/*" style="display: none" @change="handleFileSelect" />
    </div>

    <!-- 文件信息 -->
    <div v-if="audioBuffer" class="file-info">
      <span>⏱️ {{ formatTime(fileDuration) }}</span>
      <span>📊 {{ fileSampleRate }} Hz</span>
      <span>📦 {{ (fileSize / 1024).toFixed(1) }} KB</span>
    </div>

    <!-- 进度条 -->
    <div v-if="isStreaming || progress > 0" class="progress-section">
      <AProgress :percent="Math.round(progress * 100)" :show-text="false" />
      <div class="progress-text">
        {{ formatTime(currentTime) }} / {{ formatTime(fileDuration) }} ({{ Math.round(progress * 100) }}%)
      </div>
    </div>

    <!-- 控制按钮 -->
    <div class="controls">
      <AButton type="primary" :disabled="!audioBuffer || isStreaming" status="success" @click="startStreaming">
        <template #icon><icon-play-arrow /></template>
        开始发送
      </AButton>
      <AButton status="danger" :disabled="!isStreaming" @click="stopStreaming">
        <template #icon><icon-record-stop /></template>
        停止
      </AButton>
      <AButton :disabled="isStreaming" @click="resetAll">
        <template #icon><icon-refresh /></template>
        重置
      </AButton>
    </div>

    <!-- 实时识别预览 -->
    <div v-if="liveText" class="live-preview">
      <div class="live-label">🎯 实时识别:</div>
      <div class="live-text">{{ liveText }}</div>
    </div>
  </ACard>
</template>

<script lang="ts" setup>
import { onBeforeUnmount, ref } from 'vue';
import { Message } from '@arco-design/web-vue';
import { saveDialog } from '../api';
import type { MeetingDialog, RecognizedStatus } from '../api/types';

const SAMPLE_RATE = 16000;
const CHUNK_SIZE = 960; // 60ms @ 16kHz

const props = defineProps<{
  meetingId: number;
}>();

const emit = defineEmits<{
  (e: 'dialog-received', dialog: Partial<MeetingDialog>): void;
}>();

// WebSocket 配置
const wsHost = (import.meta as any).env.VITE_API_PY_WS_HOST || 'ws://localhost:8210';

// Refs
const fileInputRef = ref<HTMLInputElement | null>(null);

// 状态
const isDragOver = ref(false);
const audioBuffer = ref<AudioBuffer | null>(null);
const pcmData = ref<ArrayBuffer | null>(null);
const fileName = ref('');
const fileDuration = ref(0);
const fileSampleRate = ref(0);
const fileSize = ref(0);

// 流式状态
const isStreaming = ref(false);
const progress = ref(0);
const currentTime = ref(0);
const liveText = ref('');

// WebSocket 和定时器
let websocket: WebSocket | null = null;
let streamingInterval: ReturnType<typeof setInterval> | null = null;
let audioContext: AudioContext | null = null;
let currentSeq = 0;

// 工具函数
function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// 文件处理
function triggerFileInput() {
  fileInputRef.value?.click();
}

function handleDrop(e: DragEvent) {
  isDragOver.value = false;
  const files = e.dataTransfer?.files;
  if (files && files.length > 0 && files[0].type.startsWith('audio/')) {
    loadAudioFile(files[0]);
  } else {
    Message.error('请拖放音频文件');
  }
}

function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0];
  if (file) {
    loadAudioFile(file);
  }
}

async function loadAudioFile(file: File) {
  try {
    if (!audioContext) {
      audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    }

    const buffer = await file.arrayBuffer();
    const decoded = await audioContext.decodeAudioData(buffer.slice(0));
    audioBuffer.value = decoded;
    pcmData.value = convertToPCM(decoded);

    fileName.value = file.name;
    fileDuration.value = decoded.duration;
    fileSampleRate.value = decoded.sampleRate;
    fileSize.value = pcmData.value.byteLength;

    Message.success(`音频加载完成: ${decoded.duration.toFixed(2)}s`);
  } catch (e: any) {
    Message.error(`加载失败: ${e.message}`);
  }
}

function convertToPCM(buffer: AudioBuffer): ArrayBuffer {
  let channelData = buffer.getChannelData(0);

  // 重采样到 16kHz
  if (buffer.sampleRate !== SAMPLE_RATE) {
    const ratio = SAMPLE_RATE / buffer.sampleRate;
    const newLength = Math.floor(channelData.length * ratio);
    const resampled = new Float32Array(newLength);

    for (let i = 0; i < newLength; i++) {
      const srcIndex = i / ratio;
      const srcIndexFloor = Math.floor(srcIndex);
      const srcIndexCeil = Math.min(srcIndexFloor + 1, channelData.length - 1);
      const t = srcIndex - srcIndexFloor;
      resampled[i] = channelData[srcIndexFloor] * (1 - t) + channelData[srcIndexCeil] * t;
    }
    channelData = resampled;
  }

  // 转换为 Int16
  const pcm = new Int16Array(channelData.length);
  for (let i = 0; i < channelData.length; i++) {
    const s = Math.max(-1, Math.min(1, channelData[i]));
    pcm[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }

  return pcm.buffer;
}

// WebSocket 流式发送
async function startStreaming() {
  if (!pcmData.value) {
    Message.error('请先选择音频文件');
    return;
  }

  if (isStreaming.value) return;

  const wsUrl = `${wsHost}/ws/recognize`;
  console.log('连接到:', wsUrl);

  try {
    websocket = new WebSocket(wsUrl);
    websocket.binaryType = 'arraybuffer';

    websocket.onopen = () => {
      console.log('WebSocket 连接成功');
      Message.success('连接成功，开始发送音频');
      beginStreaming();
    };

    websocket.onmessage = event => {
      handleMessage(JSON.parse(event.data));
    };

    websocket.onerror = () => {
      Message.error('WebSocket 连接错误');
    };

    websocket.onclose = () => {
      console.log('WebSocket 关闭');
      stopStreaming();
    };
  } catch (e: any) {
    Message.error(`连接失败: ${e.message}`);
  }
}

function beginStreaming() {
  isStreaming.value = true;
  liveText.value = '';

  // 发送配置
  const config = {
    chunk_size: [5, 10, 5],
    chunk_interval: 10,
    wav_name: `meeting_${props.meetingId}`,
    is_speaking: true,
    mode: '2pass',
    itn: true,
    sample_rate: SAMPLE_RATE
  };
  websocket?.send(JSON.stringify(config));

  // 开始流式发送
  const chunkBytes = CHUNK_SIZE * 2;
  const intervalMs = (CHUNK_SIZE / SAMPLE_RATE) * 1000; // 60ms

  const pcmArray = new Uint8Array(pcmData.value!);
  const totalChunks = Math.ceil(pcmArray.length / chunkBytes);
  let currentChunk = 0;

  console.log(`开始发送: ${totalChunks} 帧, 间隔 ${intervalMs.toFixed(1)}ms`);

  streamingInterval = setInterval(() => {
    if (!isStreaming.value || !websocket || websocket.readyState !== WebSocket.OPEN) {
      stopStreaming();
      return;
    }

    if (currentChunk >= totalChunks) {
      // 发送停止信号，通知后端所有音频已发送完毕
      websocket.send(JSON.stringify({ is_speaking: false, mode: '2pass' }));
      console.log('发送完成，等待最终识别结果...');
      Message.info('音频发送完成，等待最终识别结果...');

      if (streamingInterval) {
        clearInterval(streamingInterval);
        streamingInterval = null;
      }

      // 兜底机制：如果10秒后还没收到最终结果，强制关闭
      // 正常情况下会在 handleMessage 中收到 is_final=true 后关闭
      setTimeout(() => {
        if (websocket && websocket.readyState === WebSocket.OPEN) {
          console.log('兜底关闭：超时未收到最终结果');
          websocket.close(1000, 'timeout');
        }
        if (isStreaming.value) {
          stopStreaming();
        }
      }, 10000);
      return;
    }

    // 发送音频块
    const start = currentChunk * chunkBytes;
    const end = Math.min(start + chunkBytes, pcmArray.length);
    const chunk = pcmArray.slice(start, end);

    websocket.send(chunk.buffer);
    currentChunk++;

    // 更新进度
    progress.value = currentChunk / totalChunks;
    currentTime.value = (currentChunk * CHUNK_SIZE) / SAMPLE_RATE;
  }, intervalMs);
}

function stopStreaming() {
  isStreaming.value = false;

  if (streamingInterval) {
    clearInterval(streamingInterval);
    streamingInterval = null;
  }

  Message.info('发送结束');
}

async function handleMessage(data: any) {
  const mode = data.mode || '';
  const text = data.text || '';
  const isFinal = data.is_final || false;
  const startOffsetMs = data.start_offset_ms || 0;
  const endOffsetMs = data.end_offset_ms || 0;
  const durationMs = data.duration_ms || 0;
  const audioPath = data.audio_path || '';
  const speakerInfo = data.speaker_info || null;

  // 更新实时预览
  if (mode === '2pass-online' || mode === 'online') {
    liveText.value += text;
  } else if (mode === '2pass-offline' || mode === 'offline') {
    // 离线纠错结果 - 保存到会议记录
    liveText.value = '';

    if (text) {
      currentSeq++;

      // 构建完整的音频URL（如果有）
      const pyHost = (import.meta as any).env.VITE_API_PY_HOST || 'http://localhost:8210';
      const fullAudioPath = audioPath ? `${pyHost}${audioPath}` : '';

      // 处理声纹匹配结果
      let speakerId: number | null = null;
      let speakerName = '未知发言人';
      const speakerRole = '';
      let recognized: RecognizedStatus = 0;
      let recognitionNote = '等待声纹匹配';
      let recognitionScore: number | undefined;

      if (speakerInfo && speakerInfo.recognized) {
        speakerId = speakerInfo.speaker_id;
        speakerName = speakerInfo.speaker_name || '未知';
        recognized = 1 as RecognizedStatus; // 声纹自动识别
        recognitionNote = speakerInfo.recognition_note || '声纹匹配成功';
        recognitionScore = speakerInfo.recognition_score;
      } else if (speakerInfo) {
        recognitionNote = speakerInfo.recognition_note || '声纹未匹配';
      }

      const dialog: Partial<MeetingDialog> = {
        meetingId: props.meetingId,
        seq: currentSeq,
        speakerId,
        speakerName,
        speakerRole,
        recognized,
        recognitionNote,
        recognitionScore,
        speakTime: new Date().toISOString().replace('T', ' ').substring(0, 19),
        text,
        // 时间信息
        startOffset: startOffsetMs,
        endOffset: endOffsetMs,
        durationMs,
        // 音频路径
        audioPath: fullAudioPath
      };

      // 通知父组件
      emit('dialog-received', dialog);

      // 保存到后端
      try {
        await saveDialog(dialog);
      } catch (e) {
        console.error('保存对话失败:', e);
      }
    }

    // 如果是最终结果且流式发送已停止，可以安全关闭连接
    if (isFinal && progress.value >= 1) {
      console.log('收到最终结果，准备关闭连接');
      setTimeout(() => {
        if (websocket && websocket.readyState === WebSocket.OPEN) {
          websocket.close(1000, 'received final result');
        }
        stopStreaming();
      }, 500);
    }
  }
}

function resetAll() {
  stopStreaming();
  if (websocket) {
    websocket.close();
    websocket = null;
  }

  audioBuffer.value = null;
  pcmData.value = null;
  fileName.value = '';
  fileDuration.value = 0;
  fileSampleRate.value = 0;
  fileSize.value = 0;
  progress.value = 0;
  currentTime.value = 0;
  liveText.value = '';
  currentSeq = 0;

  Message.info('已重置');
}

// 清理
onBeforeUnmount(() => {
  stopStreaming();
  if (websocket) {
    websocket.close();
  }
});
</script>

<style scoped>
.audio-upload-card {
  margin-bottom: 16px;
}

.drop-zone {
  border: 2px dashed var(--color-border-2);
  border-radius: 12px;
  padding: 32px;
  text-align: center;
  background: var(--color-fill-1);
  transition: all 0.3s ease;
  cursor: pointer;
  margin-bottom: 16px;
}

.drop-zone:hover,
.drop-zone.dragover {
  border-color: rgb(var(--primary-6));
  background: rgb(var(--primary-1));
}

.drop-zone.has-file {
  border-color: rgb(var(--success-6));
  background: rgb(var(--success-1));
}

.drop-icon {
  font-size: 2.5rem;
  margin-bottom: 8px;
}

.drop-text {
  font-size: 1rem;
  color: var(--color-text-2);
}

.drop-hint {
  font-size: 0.8rem;
  color: var(--color-text-3);
  margin-top: 6px;
}

.file-info {
  display: flex;
  gap: 16px;
  font-size: 0.9rem;
  color: var(--color-text-2);
  margin-bottom: 16px;
  padding: 12px;
  background: var(--color-fill-2);
  border-radius: 8px;
}

.progress-section {
  margin-bottom: 16px;
}

.progress-text {
  font-size: 0.85rem;
  color: var(--color-text-2);
  margin-top: 8px;
  text-align: center;
}

.controls {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.live-preview {
  padding: 16px;
  border-radius: 8px;
  background: var(--color-success-light-1);
  border: 1px solid rgb(var(--success-6));
}

.live-label {
  font-size: 0.85rem;
  color: rgb(var(--success-6));
  font-weight: 500;
  margin-bottom: 8px;
}

.live-text {
  font-size: 1rem;
  color: var(--color-text-1);
  line-height: 1.6;
}
</style>
