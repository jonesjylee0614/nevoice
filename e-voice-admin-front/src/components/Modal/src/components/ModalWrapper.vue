<template>
  <AScrollbar ref="wrapperRef" style="overflow: auto">
    <ASpin :loading="loading" :tip="loadingTip || '加载中'" style="width: 100%">
      <div ref="spinRef" :class="{ modelbody: isPadding }" :style="spinStyle">
        <slot></slot>
      </div>
    </ASpin>
  </AScrollbar>
</template>

<script lang="ts" setup>
import { useMutationObserver } from '@vueuse/core';
import { createModalContext } from '../hooks/useModalContext';

interface Props {
  loading: boolean;
  height: number;
  visible: boolean;
  fullScreen: boolean;
  loadingTip: string;
  useWrapper?: boolean;
  isPadding?: boolean;
  modalHeaderHeight?: number;
  modalFooterHeight?: number;
  minHeight?: number;
  footerOffset?: number;
}

const props = withDefaults(defineProps<Props>(), {
  useWrapper: true,
  isPadding: true,
  modalHeaderHeight: 48,
  modalFooterHeight: 53,
  minHeight: 200,
  footerOffset: 0
});

const emit = defineEmits(['height-change', 'ext-height']);
const wrapperRef = ref<ComponentRef>(null);
const spinRef = ref<ElRef>(null);
const realHeightRef = ref<any>(0);
const minRealHeightRef = ref(0);

let realHeight = 0;

const stopElResizeFn: Fn = () => {};

useMutationObserver(
  spinRef,
  () => {
    setModalHeight();
  },
  {
    attributes: true,
    subtree: true
  }
);

createModalContext({
  redoModalHeight: setModalHeight
});

const spinStyle = computed((): CSSProperties => {
  return {
    minHeight: `${props.minHeight}px`,
    [props.fullScreen ? 'height' : 'maxHeight']: `${unref(realHeightRef)}px`
  };
});

watchEffect(() => {
  props.useWrapper && setModalHeight();
});

watch(
  () => props.fullScreen,
  v => {
    setModalHeight();
    if (!v) {
      realHeightRef.value = minRealHeightRef.value;
    } else {
      minRealHeightRef.value = realHeightRef.value;
    }
  }
);

onMounted(() => {
  const { modalHeaderHeight, modalFooterHeight } = props;
  emit('ext-height', modalHeaderHeight + modalFooterHeight);
});

onUnmounted(() => {
  stopElResizeFn && stopElResizeFn();
});

async function setModalHeight() {
  // 解决在弹窗关闭的时候监听还存在,导致再次打开弹窗没有高度
  // 加上这个,就必须在使用的时候传递父级的visible
  if (!props.visible) return;
  const wrapperRefDom = unref(wrapperRef);
  if (!wrapperRefDom) return;

  const bodyDom = wrapperRefDom.$el.parentElement;
  if (!bodyDom) return;
  bodyDom.style.padding = '0';
  await nextTick();
  try {
    const modalDom = bodyDom.parentElement && bodyDom.parentElement.parentElement;
    if (!modalDom) return;

    const modalRect = getComputedStyle(modalDom as Element).top;
    const modalTop = Number.parseInt(modalRect, 10);
    let maxHeight =
      window.innerHeight -
      modalTop * 2 +
      (props.footerOffset! || 0) -
      props.modalFooterHeight -
      props.modalHeaderHeight;

    // 距离顶部过进会出现滚动条
    if (modalTop < 40) {
      maxHeight -= 26;
    }
    await nextTick();
    const spinEl = unref(spinRef);

    if (!spinEl) return;
    await nextTick();
    if (!realHeight) {
      realHeight = spinEl.scrollHeight;
    }
    if (props.fullScreen) {
      let minheigt = 0;
      if (props.modalFooterHeight == 0) {
        minheigt = 6;
      }
      realHeightRef.value = window.innerHeight - props.modalFooterHeight - props.modalHeaderHeight - minheigt;
    } else {
      realHeightRef.value = props.height ? props.height : props.minHeight;
    }
    emit('height-change', unref(realHeightRef));
  } catch (error) {
    console.log(error);
  }
}
</script>

<style scoped>
.modelbody {
  padding: 15px;
}
</style>
