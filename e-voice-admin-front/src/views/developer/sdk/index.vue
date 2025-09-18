<template>
  <div class="container">
    <Breadcrumb :items="[route.matched[0].meta.locale, route.meta.locale]" />
    <!-- AK/SK 区域 -->
    <ACard class="aksk-card" title="AK/SK 配置">
      <AForm :model="akskForm" layout="horizontal" label-align="left" :label-col-props="{ span: 4 }">
        <AFormItem label="Access Key">
          <AInput v-model="akskForm.ak" placeholder="自动生成的 AK" readonly />
        </AFormItem>
        <AFormItem label="Secret Key">
          <AInput v-model="akskForm.sk" placeholder="自动生成的 SK" readonly />
        </AFormItem>
        <AFormItem label="操作">
          <AButton type="primary" @click="generateKeys">生成 AK/SK</AButton>
        </AFormItem>
      </AForm>
    </ACard>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { generateRandomString } from '@/utils/string';
import CodeEditor from '@/components/CodeEditor/src/CodeEditor.vue';

const route = useRoute();

// AK/SK 表单
const akskForm = ref({
  ak: '',
  sk: ''
});

// 生成 AK/SK
const generateKeys = () => {
  akskForm.value.ak = `AK_${generateRandomString(16)}`;
  akskForm.value.sk = `SK_${generateRandomString(32)}`;
};

// 接口列表
const apiList = [
  { key: 'tts', title: '文本转语音' },
  { key: 'stt', title: '语音转文本' },
  { key: 'voiceprint', title: '声纹识别' }
];

const selectedApi = ref('tts');

// 语言列表
const langList = [
  { key: 'python', title: 'Python' },
  { key: 'nodejs', title: 'Node.js' },
  { key: 'curl', title: 'Curl' }
];

const selectedLang = ref('python');

// 示例代码（可替换为真实 API 调用示例）
const codeExamples = {
  tts: {
    python: `requests.post("https://api.example.com/tts", headers={"Authorization": "Bearer ${akskForm.value.ak}"}, json={"text": "你好世界"})`,
    nodejs: `axios.post("https://api.example.com/tts", { text: "你好世界" }, { headers: { Authorization: "Bearer ${akskForm.value.ak}" } })`,
    curl: `curl -X POST https://api.example.com/tts -H "Authorization: Bearer ${akskForm.value.ak}" -d '{"text": "你好世界"}'`
  },
  stt: {
    python: `# STT 示例代码`,
    nodejs: `// STT 示例代码`,
    curl: `curl -X POST https://api.example.com/stt ...`
  },
  voiceprint: {
    python: `# 声纹识别示例`,
    nodejs: `// 声纹识别 Node.js 示例`,
    curl: `curl -X POST https://api.example.com/voiceprint ...`
  }
};

const getCodeExample = (api: string, lang: string) => {
  return codeExamples[api]?.[lang] || '// 暂无示例';
};
</script>

<style scoped lang="less">
.container {
  padding: 0 20px 20px 20px;
  height: 100%;
}
</style>
