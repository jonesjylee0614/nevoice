<template>
  <AUpload
    ref="uploadRef"
    v-model:file-list="fileList"
    action="/"
    :custom-request="customRequest"
    :accept="acceptAudios.join(',')"
    :show-file-list="false"
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
import { Api } from '@/views/finetune/task/api';

const props = defineProps<{
  params: object;
}>();

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
const emit = defineEmits(['change', 'upload', 'success']);
const fileList = ref([]);

// 上传附件改变
const onChange = (fl: any) => {
  fileList.value = fl;
  emit('change', fileList);
};

// 上传附件
const customRequest = (options: RequestOption) => {
  // docs: https://axios-http.com/docs/cancellation
  const controller = new AbortController();
  (async function requestWrap() {
    const { onProgress, onSuccess, onError, fileItem } = options;
    // 限制上传文件大小 10m
    if (fileItem.file!.size > 10 * 1024 * 1024) {
      Message.error('上传文件过大，请上传小于10M的文件');
      onError();
      return;
    }

    onProgress(1);
    const onUploadProgress = (event: ProgressEvent) => {
      let percent;
      if (event.total > 0) {
        percent = (event.loaded / event.total) * 100;
      }
      onProgress(Number.parseInt(String(percent), 10), event);
    };
    try {
      emit('upload', fileItem);
      // 开始手动上传
      const filename = fileItem?.name || '';
      const res = await useUploadApi(
        `${Api.testModel}`,
        {
          name: 'audio',
          file: fileItem.file as Blob,
          filename,
          data: { ...props.params }
        },
        onUploadProgress
      );
      if (res) {
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
</script>

<style scoped lang="less"></style>
