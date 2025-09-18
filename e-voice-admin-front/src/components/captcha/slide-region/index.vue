<template>
  <div :class="`go-captcha wrapper ${config.showTheme ? 'theme' : ''}`" :style="wrapperStyles">
    <div class="header header2">
      <span>请拖动滑块完成拼图</span>
    </div>
    <div ref="containerRef" class="body" :style="imageStyles">
      <img v-show="captchaData.image !== ''" class="picture" :style="imageStyles" :src="captchaData.image" alt="..." />
      <div
        ref="tileRef"
        class="tile"
        :style="thumbStyles"
        @mousedown="handler.dragEvent"
        @touchstart="handler.dragEvent"
      >
        <img v-show="captchaData.thumb !== ''" :src="captchaData.thumb" alt="..." />
      </div>
    </div>
    <div class="footer">
      <div class="iconBlock">
        <CloseIcon :width="22" :height="22" @click="handler.closeEvent" />
        <RefreshIcon :width="22" :height="22" @click="handler.refreshEvent" />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed, nextTick, onMounted, ref } from 'vue';
import type { CaptchaConfig, CaptchaData, CaptchaEvent } from '@/components/captcha/types';
import { defaultConfig } from '@/components/captcha/types';
import CloseIcon from '../icons/close-icon.vue';
import RefreshIcon from '../icons/refresh-icon.vue';
import { useHandler } from './hooks/handler';

const props = withDefaults(
  defineProps<{
    config?: CaptchaConfig;
    events?: CaptchaEvent;
    data?: CaptchaData;
  }>(),
  {
    config: defaultConfig,
    events: () => ({}) as CaptchaEvent,
    data: () => ({}) as CaptchaData
  }
);

const { config, data, events } = props;
const captchaData = computed(() => props.data);

const containerRef = ref<any>(null);
const tileRef = ref<any>(null);

const handler = useHandler(captchaData, events, containerRef, tileRef);

const hPadding = config.horizontalPadding || 0;
const vPadding = config.verticalPadding || 0;
const width = (config.width || 0) + vPadding * 2 + 2;

onMounted(async () => {
  await nextTick();
  if (tileRef.value) {
    tileRef.value.addEventListener('dragstart', (event: any) => event.preventDefault());
  }
});

const wrapperStyles = computed(() => {
  return {
    width: `${width}px`,
    paddingLeft: `${vPadding}px`,
    paddingRight: `${vPadding}px`,
    paddingTop: `${hPadding}px`,
    paddingBottom: `${hPadding}px`
  };
});

const thumbStyles = computed(() => {
  return {
    width: `${data.thumbWidth}px`,
    height: `${data.thumbHeight}px`,
    top: `${handler.state.y}px`,
    left: `${handler.state.x}px`
  };
});

const imageStyles = computed(() => {
  return {
    width: `${config.width}px`,
    height: `${config.height}px`
  };
});
</script>

<style lang="less">
.go-captcha {
  .header2 {
    text-align: center;
  }

  .tile {
    position: absolute;
    z-index: 2;
    cursor: pointer;

    img {
      display: block;
      cursor: pointer;
      width: 100%;
      height: 100%;
    }
  }
}
</style>
