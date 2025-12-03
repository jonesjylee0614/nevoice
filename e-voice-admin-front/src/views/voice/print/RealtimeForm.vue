<template>
  <BasicModal
    v-bind="attrs"
    width="600px"
    :min-height="350"
    :title="getTitle"
    class="print-add-form"
    :footer="false"
    :esc-to-close="false"
    :mask-closable="false"
    @register="registerModal"
  >
    <AForm ref="formRef" :model="formData" auto-label-width>
      <ARow :gutter="16">
        <AFormItem>
          <ASpace>
            <AButton type="primary" :status="recording ? 'danger' : 'normal'" @click="toggleRecording">
              <template #icon>
                <icon-record v-if="!recording" size="22" />
                <icon-record-stop v-if="recording" size="22" />
              </template>
              {{ recording ? '停止识别' : '开始录音' }}
            </AButton>
            <span v-if="recording" style="color: #52c41a; font-size: 12px">● 录音中...</span>
          </ASpace>
        </AFormItem>

        <AFormItem label="识别结果">
          <div style="min-height: 80px; padding: 12px; background: #f5f5f5; border-radius: 6px">
            <div v-if="resData.user.avatar" style="margin-bottom: 8px">
              <AImage :src="resData.user.avatar" width="30px" />
              <span style="margin-left: 8px">{{ resData.user.name }}</span>
            </div>
            <div style="font-size: 16px; line-height: 1.6; color: #333">
              {{ runningText || '等待开始识别...' }}
            </div>
          </div>
        </AFormItem>

        <AFormItem v-if="errorMsg" label="错误信息">
          <div style="color: #fb4b4b">{{ errorMsg }}</div>
        </AFormItem>
      </ARow>
    </AForm>
  </BasicModal>
</template>

<script lang="ts" setup>
import type { FormInstance } from '@arco-design/web-vue';
import { BasicModal, useModalInner } from '@/components/Modal';

const attrs = useAttrs();
const emit = defineEmits(['success']);
const formRef = ref<FormInstance>();
const recording = ref(false);
const getTitle = computed(() => '实时语音识别');
const basRes = { user: {} as any, txt: '' };
const resData = ref(basRes);
const errorMsg = ref('');
// WebSocket 地址配置
// VITE_API_PY_WS_HOST: 主服务（Flask-Sock 同步）默认 8210 端口
// VITE_API_PY_WSS_HOST: 高性能异步服务（websockets）默认 10096 端口（支持 SSL）
const wsHostSync = import.meta.env.VITE_API_PY_WS_HOST || 'ws://localhost:8210';
const wsHostAsync = import.meta.env.VITE_API_PY_WSS_HOST || 'wss://localhost:10096';

// 优先使用异步服务（性能更好），如果没配置则回退到同步服务
const wsHost = wsHostAsync || wsHostSync;

console.log('wsHost', wsHost, '(async:', wsHostAsync, ', sync:', wsHostSync, ')');

// 音频配置 - 与 FunASR Demo 保持一致
const SAMPLE_RATE = 16000;
const CHUNK_SIZE = 960; // 60ms @ 16kHz, 与 FunASR Demo 一致
const CHUNK_INTERVAL = 10;

// IME 聚合：确认文本 + 当前候选
const committedText = ref('');
const liveText = ref('');
const runningText = computed(() => {
  if (committedText.value && liveText.value) {
    return `${committedText.value} ${liveText.value}`.trim();
  }
  return (committedText.value || liveText.value || '').trim();
});

const baseData = {
  id: 0,
  userId: '',
  userName: ''
};
const formData = ref<any>(baseData);

const [registerModal, { closeModal }] = useModalInner(async data => {
  formRef.value?.resetFields();
  // 重置状态
  committedText.value = '';
  liveText.value = '';
  resData.value = { ...basRes };
  errorMsg.value = '';
});

const recorder = new window.RecorderManager('/RecorderManager/dist/');
let socket: WebSocket | null = null;
let configSent = false;

recorder.onStart = () => {
  recording.value = true;
  configSent = false;
};

// 开始/停止录音
const toggleRecording = async () => {
  if (!recording.value) {
    // 先建立连接
    conn();
    // 等待连接就绪后再开始录音
    await new Promise<void>(resolve => {
      const checkInterval = setInterval(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
          clearInterval(checkInterval);
          resolve();
        }
      }, 50);
      // 超时保护
      setTimeout(() => {
        clearInterval(checkInterval);
        resolve();
      }, 3000);
    });

    // 使用 960 bytes 帧大小 (60ms @ 16kHz)
    await recorder.start({
      sampleRate: SAMPLE_RATE,
      frameSize: CHUNK_SIZE
    });
  } else {
    stopRecording();
  }
};

// 音频帧回调 - 直接发送二进制数据
recorder.onFrameRecorded = ({ isLastFrame, frameBuffer }: { isLastFrame: boolean; frameBuffer: ArrayBuffer }) => {
  if (!socket || socket.readyState !== WebSocket.OPEN) return;

  // 首次发送配置消息
  if (!configSent) {
    const config = {
      chunk_size: [5, 10, 5],
      chunk_interval: CHUNK_INTERVAL,
      wav_name: 'realtime',
      is_speaking: true,
      mode: '2pass',
      itn: true
    };
    socket.send(JSON.stringify(config));
    configSent = true;
    console.log('配置已发送:', config);
  }

  // 直接发送二进制音频数据 - 与 FunASR Demo 一致
  socket.send(frameBuffer);
};

function stopRecording() {
  recording.value = false;
  recorder.stop();

  if (socket && socket.readyState === WebSocket.OPEN) {
    try {
      // 发送停止标识
      const stopMsg = {
        chunk_size: [5, 10, 5],
        chunk_interval: CHUNK_INTERVAL,
        wav_name: 'realtime',
        is_speaking: false,
        mode: '2pass'
      };
      socket.send(JSON.stringify(stopMsg));
      console.log('停止信号已发送');
    } catch (e) {
      console.error('发送停止信号失败:', e);
    }

    // 延迟关闭，给服务端处理时间
    setTimeout(() => {
      if (socket) {
        try {
          socket.close();
        } catch {}
        socket = null;
      }
    }, 500);
  }
}

function conn() {
  // 连接到服务器
  socket = new WebSocket(`${wsHost}/ws/recognize`);

  // 设置二进制类型为 arraybuffer
  socket.binaryType = 'arraybuffer';

  socket.onopen = () => {
    console.log('WebSocket 已连接');
    // 重置状态
    committedText.value = '';
    liveText.value = '';
    resData.value.txt = '';
    errorMsg.value = '';
  };

  socket.onmessage = (event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data);
      console.log('收到消息:', data);

      if (data.type === 'error') {
        stopRecording();
        errorMsg.value = data.message;
        return;
      }

      // 处理 FunASR 风格的响应
      const mode = data.mode || '';
      const text = data.text || '';
      const isFinal = data.is_final === false; // FunASR: is_final=false 表示用户停止说话

      if (mode.includes('online') || data.type === 'partial') {
        // 在线流式结果
        if (!recording.value && !isFinal) return;

        const state = data.text_state || {};
        const confirmed = (state.confirmed_text || '').trim();
        const candidate = (state.candidate_text || text || '').trim();

        if (confirmed) {
          committedText.value = confirmed;
        }
        liveText.value = candidate;
        resData.value.txt = (state.full_text || runningText.value).trim();
      } else if (mode.includes('offline') || data.type === 'correction') {
        // 离线纠错结果（带标点和ITN）
        const state = data.text_state || {};
        const corrected = (text || state.confirmed_text || '').trim();

        if (corrected) {
          committedText.value = corrected;
          liveText.value = '';
          resData.value.txt = corrected;
          console.info('[correction]', mode, corrected);
        }
      } else if (data.type === 'final') {
        const state = data.text_state || {};
        const confirmed = (state.confirmed_text || text || '').trim();
        if (confirmed) {
          committedText.value = confirmed;
        }
        liveText.value = '';
        resData.value.txt = runningText.value;
      } else if (data.type === 'session_end') {
        liveText.value = '';
        resData.value.txt = runningText.value;
      }
    } catch (e) {
      console.error('解析消息失败:', e);
    }
  };

  socket.onclose = () => {
    console.log('WebSocket 已关闭');
    configSent = false;
  };

  socket.onerror = error => {
    console.error('WebSocket 错误:', error);
    errorMsg.value = '连接失败，请检查服务是否启动';
  };
}
</script>

<style lang="less"></style>
