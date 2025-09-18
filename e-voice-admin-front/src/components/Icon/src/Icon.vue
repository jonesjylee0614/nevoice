<template>
  <SvgIcon v-if="isSvgIcon" :size="size" :icon="icon" :spin="spin" :color="color" />
  <component :is="getIconRef" v-else :spin="spin" :size="size" :style="getWrapStyle"></component>
</template>

<script lang="ts" setup>
import { isString } from '@/utils/is';
import SvgIcon from './SvgIcon.vue';

const SVG_END_WITH_FLAG = 'svg';

interface Props {
  icon: string;
  color?: string;
  spin?: boolean;
  size?: string | number;
  prefix?: string;
}

const props = withDefaults(defineProps<Props>(), {
  prefix: '',
  size: 18,
  color: '',
  spin: false
});

const isSvgIcon = computed(() => props.icon?.startsWith(SVG_END_WITH_FLAG));
const getIconRef = computed(() => `${props.prefix ? `${props.prefix}:` : ''}${props.icon}`);

const getWrapStyle = computed(() => {
  const { size, color } = props;
  let fs = size;
  if (isString(size)) {
    fs = Number.parseInt(size, 10);
  }
  return {
    fontSize: `${fs}px`,
    color,
    display: 'inline-flex'
  };
});
</script>

<style lang="less">
.app-iconify {
  display: inline-block;
  &-spin {
    svg {
      animation: loadingCircle 1s infinite linear;
    }
  }
}

span.iconify {
  display: block;
  min-width: 1em;
  min-height: 1em;
  border-radius: 100%;
}
</style>
