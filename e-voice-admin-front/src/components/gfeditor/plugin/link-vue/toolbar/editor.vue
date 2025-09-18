<template>
  <AConfigProvider :auto-insert-space-in-button="false">
    <div data-element="ui" class="data-link-editor" :class="[className]">
      <p>{{ textTitle }}</p>
      <p>
        <AInput v-model="text" class="data-link-input" :placeholder="textPlaceholder" />
      </p>
      <p>{{ linkTitle }}</p>
      <p>
        <AInput ref="linkRef" v-model="link" class="data-link-input" :placeholder="linkPlaceholder" />
      </p>
      <p>{{ juptTypeTitle }}</p>
      <p>
        <ARadioGroup v-model="juptType">
          <ARadio value="_self">此窗口打开</ARadio>
          <ARadio value="_blank">打开新页面</ARadio>
        </ARadioGroup>
      </p>
      <p>
        <AButton class="data-link-button" :disabled="link.trim() === ''" @click="onOk(text, link, juptType)">
          {{ buttonTitle }}
        </AButton>
      </p>
    </div>
  </AConfigProvider>
</template>

<script lang="ts" setup>
import type { LanguageInterface } from '@/components/gfeditor/emain';
interface Props {
  language: LanguageInterface;
  defaultText: string;
  defaultLink: string;
  defaultjuptType: string;
  className: string;
  onLoad: () => void;
  onOk: (text: string, link: string, juptType: string) => void;
}
const props = defineProps<Props>();

const text = ref(props.defaultText);
const link = ref(props.defaultLink);
const juptType = ref(props.defaultjuptType);
const linkRef = ref<HTMLElement | null>(null);
const textTitle = props.language.get<string>('link', 'text');
const textPlaceholder = props.language.get<string>('link', 'text_placeholder');

const linkTitle = props.language.get<string>('link', 'link');
const juptTypeTitle = props.language.get<string>('link', 'juptType');
const linkPlaceholder = props.language.get<string>('link', 'link_placeholder');

const buttonTitle = props.language.get<string>('link', 'ok_button');

onMounted(() => {
  if (linkRef.value) linkRef.value.focus();
  setTimeout(() => {
    if (props.onLoad) props.onLoad();
  }, 200);
});
</script>
