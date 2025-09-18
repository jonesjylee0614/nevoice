<template>
  <!-- 接口文档 + 示例调用 -->
  <ACard ref="oneLineCardRef" class="general-card oneLineCard" style="height: calc(100% - 220px)">
    <ARow :gutter="16">
      <!-- 左侧接口列表 -->
      <ACol :span="6">
        <AList size="small" hoverable>
          <AListItem
            v-for="api in apiList"
            :key="api.key"
            style="cursor: pointer"
            :class="selectedApi === api.key ? 'current' : ''"
            @click="changeApi(api.key)"
          >
            {{ api.title }}
          </AListItem>
        </AList>
      </ACol>

      <!-- 右侧代码示例 -->
      <ACol :span="18">
        <ATabs v-model="selectedLang" type="card-gutter">
          <ATabPane v-for="lang in langList" :key="lang.key" :title="lang.title">
            <CodeEditor :value="getCodeExample(selectedApi, lang.key)" :mode="lang.key" />
          </ATabPane>
        </ATabs>
      </ACol>
    </ARow>
  </ACard>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { BasicInfoModel } from '@/api/user-center';
import CodeEditor from '@/components/CodeEditor/src/CodeEditor.vue';

const model = defineModel<BasicInfoModel>('formData', { required: true });

const selectedApi = ref('list');

// 接口列表
const apiList = [
  { key: 'list', title: '获取声纹注册用户列表' },
  { key: 'detail', title: '获取用户声纹列表' },
  { key: 'save', title: '保存用户声纹信息' },
  { key: 'del', title: '删除用户声纹' },
  { key: 'check', title: '声纹鉴定' },
  { key: 'check-flow', title: '声纹鉴定(流式)' }
];

// 语言列表
const langList = [
  { key: 'python', title: 'Python' },
  { key: 'nodejs', title: 'Node.js' },
  { key: 'curl', title: 'Curl' }
];

const selectedLang = ref('python');

// 示例代码（可替换为真实 API 调用示例）
const codeExamples = {
  list: {
    python: `requests.post("https://api.example.com/tts", headers={"Authorization": "Bearer ${model.value.appKey}"}, json={"text": "你好世界"})`,
    nodejs: `axios.post("https://api.example.com/tts", { text: "你好世界" }, { headers: { Authorization: "Bearer ${model.value.appKey}" } })`,
    curl: `curl -X POST https://api.example.com/tts -H "Authorization: Bearer ${model.value.appKey}" -d '{"text": "你好世界"}'`
  },
  detail: {
    python: `# STT 示例代码`,
    nodejs: `// STT 示例代码`,
    curl: `curl -X POST https://api.example.com/stt ...`
  },
  save: {
    python: `# 声纹识别示例 save`,
    nodejs: `// 声纹识别 Node.js 示例`,
    curl: `curl -X POST https://api.example.com/voiceprint ...`
  },
  del: {
    python: `# 声纹识别示例 del`,
    nodejs: `// 声纹识别 Node.js 示例`,
    curl: `curl -X POST https://api.example.com/voiceprint ...`
  },
  check: {
    python: `# 声纹识别示例 check`,
    nodejs: `// 声纹识别 Node.js 示例`,
    curl: `curl -X POST https://api.example.com/voiceprint ...`
  },
  'check-flow': {
    python: `# 声纹识别示例 check-flow`,
    nodejs: `// 声纹识别 Node.js 示例`,
    curl: `curl -X POST https://api.example.com/voiceprint ...`
  }
};

const changeApi = (api: string) => {
  selectedApi.value = api;
};

const getCodeExample = (api: string, lang: string) => {
  return codeExamples[api]?.[lang] || '// 暂无示例';
};
</script>

<style scoped lang="less">
.current {
  background-color: var(--color-fill-1);
}
</style>
