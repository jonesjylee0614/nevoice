<template>
  <div :class="`go-captcha wrapper ${config.showTheme ? 'theme' : ''}`" :style="wrapperStyles">
    <div class="header">
      <span>请在下图依次点击：</span>
      <img v-show="captchaData.thumb !== ''" :style="thumbStyles" :src="captchaData.thumb" alt="..." />
    </div>
    <div class="body" :style="imageStyles">
      <img
        v-show="captchaData.image !== ''"
        :style="imageStyles"
        class="picture"
        :src="captchaData.image"
        alt="..."
        @click="handler.clickEvent"
      />
      <div class="dots">
        <div
          v-for="dot in dots.list"
          :key="`${dot.key + '-' + dot.index}`"
          class="dot"
          :style="{
            top: dot.y - 11 + 'px',
            left: dot.x - 11 + 'px'
          }"
        >
          {{ dot.index }}
        </div>
      </div>
    </div>
    <div class="footer">
      <div class="iconBlock iconBlock2">
        <CloseIcon :width="22" :height="22" @click="handler.closeEvent" />
        <RefreshIcon :width="22" :height="22" @click="handler.refreshEvent" />
      </div>
      <AButton type="primary" @click="handler.confirmEvent">确认</AButton>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue';
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
const handler = useHandler(data, events);
const captchaData = computed(() => props.data);

const hPadding = config.horizontalPadding || 0;
const vPadding = config.verticalPadding || 0;
const width = (config.width || 0) + vPadding * 2 + 2;
const dots = handler.dots;

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
    width: `${config.thumbWidth}px`,
    height: `${config.thumbHeight}px`
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
  .iconBlock2 {
    flex: 1;
  }

  .dots {
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
    bottom: 0;
    .dot {
      position: absolute;
      z-index: 2;
      width: 20px;
      height: 20px;
      color: #cedffe;
      background: #3e7cff;
      border: 2px solid #f7f9fb;
      display: -webkit-box;
      display: -webkit-flex;
      display: -ms-flexbox;
      display: flex;
      -webkit-box-align: center;
      -webkit-align-items: center;
      -ms-flex-align: center;
      align-items: center;
      justify-content: center;
      border-radius: 20px;
      cursor: default;
      font-weight: 600;
    }
  }
}
</style>
