<template>
  <svg class="svg-icon" :class="[$attrs.class, spin && 'svg-icon-spin']" :style="getStyle" aria-hidden="true">
    <use :xlink:href="`#${icon}`"></use>
  </svg>
</template>

<script lang="ts" setup>
interface Props {
  icon: string;
  color: string;
  spin: boolean;
  size?: number | string;
}

const props = withDefaults(defineProps<Props>(), {
  size: 16
});

const getStyle = computed(() => {
  const { size, color } = props;
  let s = `${size}`;
  s = `${s.replace('px', '')}px`;
  return {
    color,
    width: s,
    height: s
  };
});
</script>

<style lang="less" scoped>
.svg-icon {
  display: inline-block;
  overflow: hidden;
  vertical-align: -0.15em;
  fill: currentColor;
}
.svg-icon-spin {
  animation: loadingCircle 1s infinite linear;
}
</style>
