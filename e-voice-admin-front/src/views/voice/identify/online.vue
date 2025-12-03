<template>
  <div class="page-wrap">
    <ACard class="card">
      <template #title>
        <div class="card-title">
          <icon-sound style="color: #1677ff" />
          <span>在线语音识别（单次请求）</span>
        </div>
      </template>

      <div class="form-row">
        <label for="onlineFile" class="label">
          <icon-upload />
          选择音频文件
        </label>
        <input id="onlineFile" class="file" type="file" accept="audio/*" @change="onFileChange" />
      </div>

      <div class="form-row grid">
        <ASelect v-model="format" class="w">
          <AOption value="wav">WAV</AOption>
          <AOption value="mp3">MP3</AOption>
          <AOption value="m4a">M4A</AOption>
        </ASelect>
        <ASelect v-model="sampleRate" class="w">
          <AOption :value="16000">16000 Hz</AOption>
          <AOption :value="22050">22050 Hz</AOption>
          <AOption :value="44100">44100 Hz</AOption>
          <AOption :value="48000">48000 Hz</AOption>
        </ASelect>
        <AButton type="primary" :loading="loading" :disabled="!file" @click="submit">
          <template #icon><icon-send /></template>
          提交识别
        </AButton>
      </div>

      <ADivider />

      <div v-if="loading" class="tips">
        <icon-loading spin />
        提交中，请稍候...
      </div>

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
const format = ref('wav');
const sampleRate = ref<number>(16000);
const loading = ref(false);
const result = ref('');
const error = ref('');

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement;
  file.value = input.files && input.files[0] ? input.files[0] : null;
}

function fileToBase64(f: File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const res = String(reader.result || '');
      const base64 = res.includes(',') ? res.split(',')[1] : res;
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(f);
  });
}

async function submit() {
  if (!file.value) return;
  loading.value = true;
  error.value = '';
  result.value = '';
  try {
    const base64Data = await fileToBase64(file.value);
    // 优先走网关
    try {
      const data: any = await defHttp.post({
        url: '/voice/gateway/voiceRecognizeOnline',
        params: { audio_data: base64Data, format: format.value, sample_rate: sampleRate.value }
      });
      result.value = JSON.stringify(data, null, 2);
    } catch (e) {
      // 回退直连 Python 服务
      const res = await fetch(`${httpHost}/voice-recognize-online`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ audio_data: base64Data, format: format.value, sample_rate: sampleRate.value })
      });
      const data = await res.json();
      result.value = JSON.stringify(data, null, 2);
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
  background: linear-gradient(135deg, #f6ffed, #e6f7ff);
}
.card {
  max-width: 820px;
  width: 100%;
  border-radius: 14px;
}
.card-title {
  display: flex;
  gap: 10px;
  align-items: center;
  font-weight: 600;
}
.form-row {
  margin: 12px 0;
}
.form-row.grid {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 12px;
  align-items: center;
}
.label {
  display: flex;
  gap: 8px;
  color: #555;
  margin-bottom: 6px;
}
.file {
  width: 100%;
}
.w {
  width: 100%;
}
.tips {
  color: #888;
  margin: 10px 0;
}
.result pre {
  white-space: pre-wrap;
  word-break: break-word;
}
.err {
  color: #cf1322;
}
</style>
