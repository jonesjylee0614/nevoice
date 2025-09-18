<template>
  <ASelect
    allow-search
    size="small"
    style="min-width: 128px"
    :default-value="defaultValue"
    :popup-container="getContainer"
    @change="hangSelect"
  >
    <AOption v-for="item in modeDatas" :key="item.value" :label="item.name" :value="item.value">
      {{ item.name }}
    </AOption>
  </ASelect>
</template>

<script lang="ts" setup>
interface Props {
  modeDatas: Array<{ value: string; syntax: string; name: string }>;
  defaultValue: string;
  getContainer: HTMLElement;
  onSelect: Function;
}
const props = defineProps<Props>();
const hangSelect = (value: any) => {
  if (props.onSelect) props.onSelect(value);
};
</script>
