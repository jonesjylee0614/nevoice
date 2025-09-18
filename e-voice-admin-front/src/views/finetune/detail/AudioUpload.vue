<template>
  <AUpload
    ref="uploadRef"
    v-model:file-list="fileList"
    action="/"
    :custom-request="customRequest"
    :accept="acceptAudios.join(',')"
    :auto-upload="false"
    @change="onChange"
  >
    <template #upload-button>
      <ASpace>
        <AButton>选择文件</AButton>
      </ASpace>
    </template>
  </AUpload>
</template>

<script setup lang="ts">
import type { RequestOption } from '@arco-design/web-vue/es/upload/interfaces';
import { Message } from '@arco-design/web-vue';
import { useUploadApi } from '@/api/common';
import { Api } from '@/views/finetune/detail/api';

const props = defineProps<{
  params: object;
}>();

const apiHost = import.meta.env.VITE_API_HOST;

const uploadRef = ref();
const acceptAudios = [
  'audio/mpeg',
  'audio/ogg',
  'audio/wav',
  'audio/m4a',
  'audio/aac',
  'audio/flac',
  'audio/webm',
  'audio/midi',
  'audio/x-midi',
  'audio/mp3',
  'audio/mp4',
  'audio/wma',
  'audio/x-wma',
  'audio/x-ms-wma'
];
const emit = defineEmits(['change', 'update:modelValue', 'success']);
const fileList = ref<any[]>([]);

// 上传附件改变
const onChange = (fl: any, file: any) => {
  // 检查音频大小，只能上传小于1M的音频，5-10秒
  if (file.size > 1024 * 1024) {
    Message.error('音频文件过大，请上传小于1M的音频');
    fileList.value = [];
    return;
  }

  // 获取音频时长
  const audio = new Audio();
  audio.src = URL.createObjectURL(file.file);
  audio.addEventListener('loadedmetadata', () => {
    const duration = audio.duration;
    if (duration > 10 || duration < 1) {
      Message.error('音频时长过长，请上传1-10秒的音频');
      fileList.value = [];
    }
  });

  fileList.value = fl;
  emit('change', file);
};

watch(
  () => props.params,
  (params: any) => {
    fileList.value = [];
    if (params && params.audioPath) {
      fileList.value.push({
        url: `${apiHost}/meeting_voice/${params.id}/${params.audioPath}`,
        name: `${params.audioPath}`
      } as any);
    }
  }
);

// 上传附件
const customRequest = (options: RequestOption) => {
  // docs: https://axios-http.com/docs/cancellation
  const controller = new AbortController();
  (async function requestWrap() {
    const { onProgress, onSuccess, onError, fileItem } = options;

    onProgress(1);
    const onUploadProgress = (event: ProgressEvent) => {
      let percent;
      if (event.total > 0) {
        percent = (event.loaded / event.total) * 100;
      }
      onProgress(Number.parseInt(String(percent), 10), event);
    };
    try {
      // 开始手动上传
      const filename = fileItem?.name || '';
      const res = await useUploadApi(
        `${Api.uploadAdd}`,
        {
          name: 'audio',
          file: fileItem.file as Blob,
          filename,
          data: { ...props.params }
        },
        onUploadProgress
      );
      if (res) {
        emit('update:modelValue', res);
        emit('success', res);
        fileList.value = [];
        onSuccess();
      }
    } catch (error) {
      onError(error);
    }
  })();
  return {
    abort() {
      controller.abort();
    }
  };
};

const submit = async () => {
  await uploadRef.value.submit();
};

defineExpose({ submit });
</script>

<style scoped lang="less"></style>
