<template>
  <div :class="`go-captcha wrapper ${config.showTheme ? 'theme' : ''}`" :style="wrapperStyles">
    <div class="header">
      <span>请拖动滑块完成拼图</span>
      <div class="iconBlock">
        <CloseIcon :width="22" :height="22" @click="handler.closeEvent" />
        <RefreshIcon :width="22" :height="22" @click="handler.refreshEvent" />
      </div>
    </div>
    <div class="body rotate-body" :style="imageStyles">
      <div class="picture rotate-picture" :style="imageStyles">
        <img v-show="captchaData.image !== ''" :src="captchaData.image" alt="..." />
        <div class="round" />
      </div>

      <div class="thumb rotate-thumb">
        <div class="rotate-thumbBlock" :style="thumbStyles">
          <img v-show="captchaData.thumb !== ''" :src="captchaData.thumb" alt="..." style="-webkit-user-drag: none" />
        </div>
      </div>
    </div>
    <div class="footer">
      <div ref="dragBarRef" class="dragSlideBar" @mousedown="handler.dragEvent">
        <div class="dragLine" />
        <div
          ref="dragBlockRef"
          class="dragBlock"
          :style="{ left: handler.state.dragLeft + 'px' }"
          @touchstart="handler.dragEvent"
        >
          <ArrowsIcon />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed, ref } from 'vue';
import type { CaptchaConfig, CaptchaData, CaptchaEvent } from '@/components/captcha/types';
import { defaultConfig } from '@/components/captcha/types';
import CloseIcon from '..//icons/close-icon.vue';
import RefreshIcon from '../icons/refresh-icon.vue';
import ArrowsIcon from '../icons/arrows-icon.vue';
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

const { config, events } = props;
const captchaData = computed(() => props.data);
const dragBarRef = ref<any>(null);
const dragBlockRef = ref<any>(null);

const handler = useHandler(captchaData, events, dragBlockRef, dragBarRef);

const wrapperStyles = computed(() => {
  const hPadding = config.horizontalPadding || 0;
  const vPadding = config.verticalPadding || 0;
  const width = (config.width || 0) + vPadding * 2 + 2;

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
    transform: `rotate(${handler.state.thumbAngle}deg)`
  };
});

const imageStyles = computed(() => {
  return {
    width: `${config.rotateSize}px`,
    height: `${config.rotateSize}px`
  };
});
</script>

<style lang="less">
.go-captcha {
  .rotate-body {
    background: transparent !important;
    display: flex;
    display: -webkit-box;
    display: -moz-box;
    display: -ms-flexbox;
    display: -webkit-flex;
    justify-content: center;
    align-items: center;
    margin: 10px auto 0;
  }

  .rotate-picture {
    position: relative;
    max-width: 100%;
    max-height: 100%;
    z-index: 2;
    border-radius: 100%;
    overflow: hidden;
    display: -webkit-box;
    display: -moz-box;
    display: -ms-flexbox;
    display: -webkit-flex;
    display: flex;
    justify-content: center;
    align-items: center;

    img {
      max-width: 100%;
      max-height: 100%;
    }

    .round {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      border-radius: 100%;
      z-index: 2;
      border: 6px solid #e0e0e0;
    }
  }

  .rotate-thumb {
    position: absolute;
    z-index: 2;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;

    img {
      max-width: 100%;
      max-height: 100%;
    }
  }

  .rotate-thumbBlock {
    width: 100%;
    height: 100%;
    display: -webkit-box;
    display: -moz-box;
    display: -ms-flexbox;
    display: -webkit-flex;
    display: flex;
    justify-content: center;
    align-items: center;
  }
}
</style>
