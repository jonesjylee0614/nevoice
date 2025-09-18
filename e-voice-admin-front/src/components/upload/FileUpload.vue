<template>
  <ASpace>
    <AUpload :accept="accept" :show-file-list="false" :custom-request="customUpFile" />
    <AButton v-if="modelValue && !progressing" @click="() => emit('update:modelValue')">清空</AButton>
    <span v-if="modelValue && !progressing && modelValue.startsWith('http')">
      <a :href="modelValue" target="_blank" rel="noopener noreferrer">点击下载</a>
    </span>
  </ASpace>
  <AProgress v-if="progressing" :percent="percent" :style="{ width: '100%' }" />
  <a v-if="progressing" @click="abort()"><icon-close /></a>
</template>

<script lang="ts" setup>
import axios from 'axios';
import type { RequestOption } from '@arco-design/web-vue/es/upload/interfaces';
import { userUploadApi } from '@/api/common';

interface Props {
  accept: string;
  modelValue?: string;
}
defineProps<Props>();

const emit = defineEmits(['update:modelValue']);
const percent = ref<any>('');

const progressing = ref(false);
const cancelSource = ref();

const abort = () => {
  cancelSource.value.cancel('用户取消上传');
};
// 上传附件
const customUpFile = (options: RequestOption) => {
  const controller = new AbortController();
  (async function requestWrap() {
    const { onProgress, onError, onSuccess, fileItem } = options;
    onProgress(1);
    const onUploadProgress = (event: ProgressEvent) => {
      let p = 0;
      if (event.total > 0) {
        p = event.loaded / event.total;
        percent.value = p.toFixed(4);
      }
      progressing.value = true;
      onProgress(p, event);
    };
    try {
      cancelSource.value = axios.CancelToken.source();
      const cancelToken = cancelSource.value.token;
      // 开始手动上传
      const filename = fileItem?.name || '';
      const { data } = await userUploadApi(
        { name: 'file', file: fileItem.file as Blob, filename, data: { cid: 0 } },
        onUploadProgress,
        cancelToken
      );

      // 更新附件
      if (data) {
        onSuccess(data.url);
        emit('update:modelValue', data.url);
      }
      setTimeout(() => {
        progressing.value = false;
      }, 1000);
    } catch (e) {
      onError(e);
      progressing.value = false;
    }
  })();
  return {
    abort() {
      controller.abort();
    }
  };
};
</script>

<style lang="less" scoped>
.upfile {
  display: flex;
  .upbtn {
    padding-right: 10px;
  }
  .showfile {
    flex: 1;
    height: 32px;
    line-height: 32px;
    a {
      text-decoration: none;
    }
  }
}
</style>
