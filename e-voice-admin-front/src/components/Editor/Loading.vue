<template>
  <ASpin class="loading" :tip="text" :loading="loading" :size="32">
    <slot></slot>
  </ASpin>
</template>

<script lang="ts">
export default defineComponent({
  name: 'AmLoading',
  components: {},
  props: {
    text: String,
    loading: Boolean
  }
});
</script>

<style css>
.loading {
  display: block;
}

.ant-spin-nested-loading {
  position: inherit;
}
.ant-spin-nested-loading .ant-spin-container {
  position: inherit;
}
</style>
