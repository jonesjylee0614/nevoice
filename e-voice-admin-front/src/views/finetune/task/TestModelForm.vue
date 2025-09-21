<template>
  <BasicModal
    v-bind="attrs"
    :loading="loading"
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
        <AFormItem field="userId" label="上传或录制">
          <ARadioGroup v-model="saveType">
            <ARadio :value="1">上传</ARadio>
            <ARadio :value="2">录制</ARadio>
          </ARadioGroup>
        </AFormItem>
        <AFormItem v-if="saveType === 1">
          <TestModelUpload :params="formData" @success="handleUploadSuccess" @upload="toggle" />
        </AFormItem>
        <AFormItem v-if="saveType === 2">
          <AButton @click="toggleRecording">
            <ASpace>
              <icon-record v-if="!recording" size="22" />
              <icon-record-stop v-if="recording" size="22" style="color: #f53f3f" />
              {{ recording ? '停止并提交' : '开始录音' }}
            </ASpace>
          </AButton>
        </AFormItem>

        <AFormItem label="鉴定结果">
          <icon-loading v-if="loading" />
          <div v-else>
            <AImage v-if="resData.avatar" :src="resData.avatar" width="30px" />
            <span>{{ resData.username }}</span>
            <div>{{ resData.txt }}</div>
          </div>
          <template #help>
            <div>测试模型会初始化加载模型实例，会消耗20-30秒不等，请耐心等待...</div>
          </template>
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
import { Message } from '@arco-design/web-vue';
import useLoading from '@/hooks/loading';
import { BasicModal, useModalInner } from '@/components/Modal';
import TestModelUpload from '@/views/finetune/task/TestModelUpload.vue';
import { testModel } from './api';

const attrs = useAttrs();
const emit = defineEmits(['success']);
const formRef = ref<FormInstance>();
const saveType = ref(2);
const recording = ref(false);
const parsing = ref(false);
const getTitle = computed(() => '测试模型');
const basRes = { username: '', avatar: '', txt: '' };
const resData = ref(basRes);
const errorMsg = ref('');
const doing = ref(false);

const baseData = {
  taskId: 0
};
const formData = ref<any>(baseData);
const { loading, toggle } = useLoading();

const [registerModal] = useModalInner(async data => {
  formData.value.taskId = data.record.id;
  formRef.value?.resetFields();
});

watch(saveType, () => {
  resData.value = basRes;
});

const audioChunks = ref<any[]>([]);
let mediaRecorder = null as any;
// 开始/停止录音
const toggleRecording = async () => {
  if (!recording.value) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true
        }
      });
      mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/wav'
      });

      mediaRecorder.ondataavailable = (event: any) => {
        if (event.data.size > 0) {
          audioChunks.value.push(event.data);
        }
      };

      mediaRecorder.start(10);
      recording.value = true;
    } catch (err) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = (event: any) => {
          if (event.data.size > 0) {
            audioChunks.value.push(event.data);
          }
        };
        mediaRecorder.start(100);
        recording.value = true;
      } catch (error) {
        console.error('录音失败:', error);
        Message.error('无法访问麦克风');
      }
    }
  } else {
    recording.value = false;
    parsing.value = true;
    mediaRecorder?.stop();
    mediaRecorder.stream.getTracks().forEach((track: any) => track.stop());

    const audioBlob = new Blob(audioChunks.value, { type: mediaRecorder.mimeType });
    const param = new FormData();
    param.append('audio', audioBlob, 'recording.wav');
    param.append('taskId', formData.value.taskId);
    toggle();
    Message.loading({ content: '解析中...', id: 'upStatus' });

    try {
      const res = await testModel(param);

      toggle();

      resData.value = {
        username: (res.data && res.data.length > 0 && res.data[0].username) || '',
        avatar: '',
        txt: res.txt
      };

      console.log(resData.value);
    } catch (error) {
      console.error('音频上传失败:', error);
      Message.error('音频上传失败');
    }
    // t1.close()
    audioChunks.value = [];
    parsing.value = false;
  }
};

const handleUploadSuccess = (data: any) => {
  toggle();
  console.log(data);
  resData.value = data.data;
  console.log(resData.value);
};
</script>

<style lang="less"></style>
