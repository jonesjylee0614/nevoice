<template>
  <AModal v-model:visible="modalVisible" centered :closable="false" :footer="false" width="344px" class="captcha">
    <Transition name="none" mode="out-in" appear>
      <component :is="activeModule.component" :data="captchaData" :events="clickEvents" />
    </Transition>
  </AModal>
</template>

<script setup lang="ts">
import { type Component, computed, ref, watch } from 'vue';
import type { CaptchaData } from '@/components/captcha/types';
import { getLoginCaptcha } from './api/index';
import Click from './click/index.vue';
import Rotate from './rotate/index.vue';
import Slide from './slide/index.vue';
import SlideRegion from './slide-region/index.vue';

type Props = {
  visible: boolean;
};

const props = defineProps<Props>();

const captchaTypes = ['ClickBasic', 'SlideBasic'];
const getRandomCaptchaType = () => captchaTypes[Math.floor(Math.random() * captchaTypes.length)];
const captchaType = ref<string>(getRandomCaptchaType());
const captchaKey = ref<string>('');

interface Emits {
  (e: 'success', data: any): void;

  (e: 'update:visible', data: boolean): void;
}

const emit = defineEmits<Emits>();
const modalVisible = computed({
  get: () => props.visible,
  set: val => {
    emit('update:visible', val);
  }
});
const captchaData = ref<CaptchaData>();

const loadCaptcha = async () => {
  // 随机获取一个captchaType
  captchaType.value = getRandomCaptchaType();

  const data = await getLoginCaptcha({ type: captchaType.value });
  captchaType.value = data.type;
  captchaKey.value = data.captchaKey;
  const cd = {
    image: data.imageBase64,
    thumb: data.thumbBase64
  } as CaptchaData;
  captchaData.value = cd;
  if (data.type === 'SlideBasic' || data.type === 'SlideRegion') {
    const tile = data.tile!;
    captchaData.value = {
      ...cd,
      thumbX: tile.x,
      thumbY: tile.y,
      thumbWidth: tile.width,
      thumbHeight: tile.height
    };
  }
};

let clearFn = () => {};

const clickEvents = {
  confirm(res: any, clear: any): void {
    const resData = {
      ...res,
      type: captchaType.value,
      secret: captchaKey.value
    } as any;
    // 检查验证码正确性，否则刷新验证码
    emit('success', resData);
    clearFn = clear;
  },
  refresh(): void {
    loadCaptcha();
  },
  close(): void {
    modalVisible.value = false;
  }
};

const moduleMap = {
  ClickBasic: { component: Click },
  ClickShape: { component: Click },
  RotateBasic: { component: Rotate },
  SlideBasic: { component: Slide },
  SlideRegion: { component: SlideRegion }
} as Record<string, { component: Component }>;

const activeModule = computed(() => moduleMap[captchaType.value]);

watch(props, () => {
  modalVisible.value = props.visible;
  if (props.visible) {
    // 请求验证码
    clickEvents.refresh();
  }
});

defineExpose({
  reset() {
    loadCaptcha();
    typeof clearFn === 'function' && clearFn();
  }
});
</script>

<style>
@import 'gocaptcha.less';
.captcha {
  border-radius: 12px;
  .arco-modal-body {
    padding: 0;
    border-radius: 14px;
  }
}
</style>
