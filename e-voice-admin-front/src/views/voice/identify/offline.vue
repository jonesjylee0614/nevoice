<template>
  <div class="page-wrap">
    <ACard class="card">
      <template #title>
        <div class="card-title">
          <icon-sound style="color:#52c41a" />
          <span>离线语音识别</span>
        </div>
      </template>

      <div class="form-row">
        <label for="offlineFile" class="label"><icon-upload /> 选择音频文件</label>
        <input id="offlineFile" class="file" type="file" accept="audio/*" @change="onFileChange" />
      </div>

      <div class="form-row grid">
        <ASelect v-model="language" class="w">
          <AOption value="zh-cn">中文 (zh-cn)</AOption>
          <AOption value="en-us">英文 (en-us)</AOption>
          <AOption value="auto">自动检测</AOption>
        </ASelect>
        <AButton type="primary" :loading="loading" :disabled="!file" @click="submit">
          <template #icon><icon-send /></template>
          提交识别
        </AButton>
      </div>

      <ADivider />

      <div v-if="loading" class="tips"><icon-loading spin /> 提交中，请稍候...</div>

      <ACard v-if="result" class="result" title="识别结果">
        <pre>{{ result }}</pre>
      </ACard>

      <AAlert v-if="error" type="error" show-icon>{{ error }}</AAlert>
    </ACard>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { defHttp } from '@/utils/http';

const wsHost = (import.meta as any).env.VITE_API_PY_WS_HOST || 'ws://localhost:8210';
const httpHost = wsHost.replace(/^wss:/, 'https:').replace(/^ws:/, 'http:');

const file = ref<File | null>(null);
const language = ref('zh-cn');
const loading = ref(false);
const result = ref('');
const error = ref('');

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement;
  file.value = input.files && input.files[0] ? input.files[0] : null;
}

async function submit() {
  if (!file.value) return;
  loading.value = true;
  error.value = '';
  result.value = '';
  try {
    // 优先走网关（通过系统通用上传方法）
    try {
      const resp: any = await defHttp.uploadFile({ url: '/voice/gateway/voiceRecognizeOffline' }, { file: file.value as File, name: 'audio', data: { language: language.value } });
      // resp 为网关标准返回 data，已在拦截器中解包
      result.value = typeof resp === 'string' ? resp : JSON.stringify(resp, null, 2);
    } catch (e) {
      // 回退直连 Python 服务
      const formData = new FormData();
      formData.append('audio', file.value);
      formData.append('language', language.value);
      const res = await fetch(`${httpHost}/voice-recognize-offline`, { method: 'POST', body: formData });
      const contentType = res.headers.get('content-type') || '';
      const data = contentType.includes('application/json') ? await res.json() : await res.text();
      result.value = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
      if (!res.ok) error.value = '识别失败';
    }
  } catch (e: any) {
    error.value = e?.message || String(e);
  } finally {
    loading.value = false;
  }
}
 </script>

<style scoped>
.page-wrap {
  min-height: calc(100vh - 120px);
  padding: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fff7e6, #e6fffb);
}
.card { max-width: 820px; width: 100%; border-radius: 14px; }
.card-title { display:flex; gap:10px; align-items:center; font-weight:600; }
.form-row { margin: 12px 0; }
.form-row.grid { display:grid; grid-template-columns: 1fr auto; gap:12px; align-items:center; }
.label { display:flex; gap:8px; color:#555; margin-bottom:6px; }
.file { width: 100%; }
.w { width: 100%; }
.tips { color:#888; margin:10px 0; }
.result pre { white-space: pre-wrap; word-break: break-word; }
.err { color:#cf1322; }
</style>


