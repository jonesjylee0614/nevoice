<template>
  <div class="data-link-preview" data-element="ui">
    <ATooltip :content="openTitle">
      <a class="data-icon data-icon-link data-link-preview-open" :href="href" target="_blank" rel="noopener noreferrer">
        {{ href }}
      </a>
    </ATooltip>
    <div v-if="!readonly" class="data-link-op">
      <ATooltip v-if="!isMobile" :content="editTitle">
        <a class="data-icon data-icon-edit" @click="onEdit" />
      </ATooltip>
      <a v-if="isMobile" class="data-icon data-icon-edit" @click="onEdit" />
      <ATooltip v-if="!isMobile" :content="removeTitle">
        <a class="data-icon data-icon-unlink" @click="onRemove" />
      </ATooltip>
      <a v-if="isMobile" class="data-icon data-icon-unlink" @click="onRemove" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import type { LanguageInterface } from '@/components/gfeditor/emain';
import { isMobile } from '@/components/gfeditor/emain';

interface Props {
  language: LanguageInterface;
  readonly: boolean;
  href: string;
  onEdit: (event: MouseEvent) => void;
  onRemove: (event: MouseEvent) => void;
  onLoad: () => void;
}
const props = defineProps<Props>();
const openTitle = props.language.get<string>('link', 'link_open');
const editTitle = props.language.get<string>('link', 'link_edit');
const removeTitle = props.language.get<string>('link', 'link_remove');

onMounted(() => {
  if (props.onLoad) props.onLoad();
});
</script>
