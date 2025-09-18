<template>
  <AUpload action="/" :show-file-list="false" :custom-request="customRequest" @change="onChange">
    <template #upload-button>
      <div class="arco-upload-list-item">
        <div v-if="modelValue" class="arco-upload-list-picture custom-upload-avatar">
          <img :src="modelValue" alt="" />
          <div class="arco-upload-list-picture-mask">
            <IconEdit />
          </div>
        </div>
        <div v-else class="arco-upload-picture-card">
          <div class="arco-upload-picture-card-text">
            <IconPlus />
            <div style="margin-top: 10px; font-weight: 600">上传头像</div>
          </div>
        </div>
      </div>
    </template>
  </AUpload>
</template>

<script setup lang="ts">
import type { RequestOption } from '@arco-design/web-vue/es/upload/interfaces';
import { userUploadApi } from '@/api/common';

type Props = {
  modelValue: string;
};

defineProps<Props>();

const emit = defineEmits(['change', 'update:modelValue', 'success']);

// 上传附件改变
const onChange = (fileList: any) => {
  emit('change', fileList);
};
// 上传附件
const customRequest = (options: RequestOption) => {
  // docs: https://axios-http.com/docs/cancellation
  const controller = new AbortController();
  (async function requestWrap() {
    const { onProgress, onError, fileItem } = options;
    onProgress(20);
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
      const resdata = await userUploadApi(
        {
          name: 'file',
          file: fileItem.file as Blob,
          filename,
          data: { cid: 0 }
        },
        onUploadProgress
      );
      // 更新图片
      if (resdata && resdata.data) {
        emit('update:modelValue', resdata.data.url);
        emit('success', resdata.data.url);
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
