<template>
  <BasicModal
    v-bind="attrs"
    width="500px"
    :min-height="300"
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
          <AButton @click="toggleRecording">
            <template #icon>
              <icon-record v-if="!recording" size="22" />
              <icon-record-stop v-if="recording" size="22" style="color: #f53f3f" />
            </template>
            {{ recording ? '停止识别' : '开始录音' }}
          </AButton>
        </AFormItem>

        <AFormItem v-if="resData.txt" label="识别结果">
          <div>
            <AImage :src="resData.user.avatar" width="30px" />
            <span>{{ resData.user.name }}</span>
            <div>{{ runningText || '等待开始识别' }}</div>
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
const getTitle = computed(() => '声纹鉴定');
const basRes = { user: {} as any, txt: '' };
const resData = ref(basRes);
const errorMsg = ref('');
const wsHost = import.meta.env.VITE_API_PY_WS_HOST || 'ws://localhost:8210';

console.log( 'wsHost', wsHost);

// IME 聚合：确认句子列表 + 当前partial
const finalSentences: string[] = [];
const partialText = ref('');
const runningText = computed(() => {
  const confirmed = finalSentences.filter(Boolean).join(' ');
  if (confirmed && partialText.value) return confirmed + ' ' + partialText.value;
  return confirmed || partialText.value;
});

const baseData = {
  id: 0,
  userId: '',
  userName: ''
};
const formData = ref<any>(baseData);

const [registerModal, { closeModal }] = useModalInner(async data => {
  formRef.value?.resetFields();
});
const recorder = new window.RecorderManager('/RecorderManager/dist/');
recorder.onStart = () => {
  recording.value = true;
};
// 开始/停止录音
const toggleRecording = async () => {
  if (!recording.value) {
    conn();
    await recorder.start({
      sampleRate: 16000,
      frameSize: 1280
    });
  } else {
    stopRecording();
  }
};

function toBase64(buffer: any) {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}

let socket = {} as WebSocket;

recorder.onFrameRecorded = ({ isLastFrame, frameBuffer }) => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(
      JSON.stringify({
        data: {
          status: isLastFrame ? 2 : 1,
          format: 'audio/L16;rate=16000',
          encoding: 'raw',
          audio: toBase64(frameBuffer)
        }
      })
    );
  }
};

function stopRecording() {
  recording.value = false;
  recorder.stop();
  if (socket) {
    try {
      if (socket.readyState === WebSocket.OPEN) {
        // 告诉服务端结束，等待其发送最终结果
        socket.send(JSON.stringify({ type: 'end' }));
      }
    } catch {}
    // 延迟关闭，给服务端处理时间
    setTimeout(() => {
      try { socket.close(); } catch {}
    }, 200);
  }
}

function conn() {
  // 连接到服务器
  socket = new WebSocket(`${wsHost}/ws/recognize`);

  socket.onopen = () => {
    // 连接成功后的操作
    console.log('已连接到服务器');
    try { socket.send(JSON.stringify({ type: 'start' })); } catch {}
  };
  socket.onmessage = event => {
    const data = JSON.parse(event.data);

    console.log('收到消息:', data);
    // 接收到消息后的操作
    if (data.type == 'error') {
      stopRecording();
      errorMsg.value = data.message;
      return;
    }
    if (data.type === 'partial') {
      if (!recording.value) return;
      if (data.text && data.text.trim()) partialText.value = data.text;
      resData.value.txt = runningText.value;
    } else if (data.type === 'final') {
      const idx = typeof data.index === 'number' && data.index >= 0 ? data.index : finalSentences.length;
      if (data.text && data.text.trim()) finalSentences[idx] = data.text;
      partialText.value = '';
      resData.value.txt = runningText.value;
    } else if (data.type === 'session_end') {
      // 保持最终文本
      resData.value.txt = runningText.value;
    }
  };
  socket.onclose = () => {
    // 连接关闭后的操作
    console.log('WebSocket已关闭');
  };
  socket.onerror = error => {
    console.error('WebSocket error:', error);
    // 错误处理
  };
}
</script>

<style lang="less"></style>
