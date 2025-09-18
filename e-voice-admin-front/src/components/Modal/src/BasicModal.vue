<template>
  <AModal
    v-bind="getBindValue"
    :mask-closable="getProps.maskClosable"
    :fullscreen="fullscreenVal"
    :body-style="{ padding: 0 }"
    modal-class="self-modal"
    @cancel="handleCancel"
  >
    <template v-if="!$slots.title" #title>
      <ModalHeader
        :help-message="getProps.helpMessage"
        :title="getMergeProps.title"
        :can-fullscreen="getProps.canFullscreen"
        :fullscreen-val="fullscreenVal"
        @fullscreen="handleFullscreens"
        @fullexit="handleFullscreens"
        @dblclick="handleTitleDbClick"
      />
    </template>
    <!--滚动区-->
    <ModalWrapper
      ref="modalWrapperRef"
      :use-wrapper="getProps.useWrapper"
      :full-screen="fullscreenVal"
      :loading="getProps.loading"
      :loading-tip="getProps.loadingTip"
      :is-padding="getProps.isPadding"
      :min-height="getProps.minHeight"
      :height="getWrapperHeight"
      :visible="visibleRef"
      :modal-footer-height="footer !== undefined && !footer ? 0 : undefined"
      v-bind="omit(getProps.wrapperProps, 'visible', 'height', 'modalFooterHeight')"
      @ext-height="handleExtHeight"
      @height-change="handleHeightChange"
    >
      <slot></slot>
    </ModalWrapper>
    <template v-if="!$slots.footer" #footer>
      <ModalFooter v-bind="getBindValue" :loading="getProps.loading" @ok="handleOk" @cancel="handleCancel">
        <template v-for="item in Object.keys($slots)" #[item]="data">
          <slot :name="item" v-bind="data || {}"></slot>
        </template>
      </ModalFooter>
    </template>
  </AModal>
</template>

<script lang="ts" setup>
import { omit } from 'lodash-es';
import { useAttrs } from '@/hooks/core/useAttrs';
import { deepMerge } from '@/utils';
import { isFunction } from '@/utils/is';
import { useModalDragMove } from '@/components/Modal/src/hooks/useModalDrag';
import type { ModalMethods, ModalProps } from './typing';
import ModalWrapper from './components/ModalWrapper.vue';
import ModalFooter from './components/ModalFooter.vue';
import ModalHeader from './components/ModalHeader.vue';
import { basicProps } from './props';

const props = defineProps(basicProps);

const emit = defineEmits(['visible-change', 'height-change', 'cancel', 'ok', 'register', 'update:visible']);
const visibleRef = ref(false);
const propsRef = ref<Partial<ModalProps> | null>(null);
const modalWrapperRef = ref<any>(null);
const fullscreenVal = ref(false);

const { visible, draggable, destroyOnClose } = props;
const attrs = useAttrs();
useModalDragMove({
  visible,
  destroyOnClose,
  draggable
});

const onCancel = (e: Event) => {
  emit('cancel', e);
};

// modal   Bottom and top height
const extHeightRef = ref(0);
const modalMethods: ModalMethods = {
  setModalProps,
  emitVisible: undefined,
  redoModalHeight: () => {
    nextTick(() => {
      if (unref(modalWrapperRef)) {
        (unref(modalWrapperRef) as any).setModalHeight();
      }
    });
  }
};

const instance = getCurrentInstance();
if (instance) {
  emit('register', modalMethods, instance.uid);
}

// Custom title component: get title
const getMergeProps = computed((): Recordable => {
  return {
    ...props,
    onCancel,
    ...(unref(propsRef) as any)
  };
});

// modal component does not need title and origin buttons
const getProps = computed((): Recordable => {
  const opt = {
    ...unref(getMergeProps),
    visible: unref(visibleRef),
    okButtonProps: undefined,
    cancelButtonProps: undefined,
    title: undefined
  };
  return {
    ...opt
  };
});
const getBindValue = computed((): Recordable => {
  const attr = {
    ...attrs,
    ...unref(getMergeProps),
    visible: unref(visibleRef)
  };
  if (unref(fullscreenVal)) {
    return omit(attr, ['height', 'title']);
  }
  return omit(attr, 'title');
});

const getWrapperHeight = computed(() => {
  if (unref(fullscreenVal)) return undefined;
  return unref(getProps).height;
});

watchEffect(() => {
  visibleRef.value = Boolean(props.visible);
  fullscreenVal.value = Boolean(props.defaultFullscreen);
});

watch(
  () => unref(visibleRef),
  v => {
    emit('visible-change', v);
    emit('update:visible', v);
    instance && modalMethods.emitVisible?.(v, instance.uid);
    // nextTick(() => {
    //   if (props.scrollTop && v && unref(modalWrapperRef)) {
    //     (unref(modalWrapperRef) as any).scrollTop();
    //   }
    // });
  },
  {
    immediate: false
  }
);

// 取消事件
async function handleCancel(e: Event) {
  e?.stopPropagation();
  // 过滤自定义关闭按钮的空白区域
  if (e && (e.target as HTMLElement)?.classList?.contains('-close--custom')) return;
  if (props.closeFunc && isFunction(props.closeFunc)) {
    const isClose: boolean = await props.closeFunc();
    visibleRef.value = !isClose;
    return;
  }
  visibleRef.value = false;
  fullscreenVal.value = false;
  emit('cancel', e);
}

/** @description: 设置modal参数 */
function setModalProps(p: Partial<ModalProps>): void {
  // Keep the last setModalProps
  propsRef.value = deepMerge(unref(propsRef) || ({} as any), p);
  if (Reflect.has(p, 'visible')) {
    visibleRef.value = Boolean(p.visible);
  }
  if (Reflect.has(p, 'defaultFullscreen')) {
    fullscreenVal.value = Boolean(p.defaultFullscreen);
  }
}
function handleOk(e: Event) {
  fullscreenVal.value = false;
  emit('ok', e);
}

function handleHeightChange(height: string) {
  emit('height-change', height);
}

function handleExtHeight(height: number) {
  extHeightRef.value = height;
}

function handleTitleDbClick(isFull: boolean) {
  fullscreenVal.value = isFull;
}
// 全屏
function handleFullscreens(isFull: boolean) {
  fullscreenVal.value = isFull;
}
</script>

<style lang="less">
.self-modal {
  .arco-modal-footer {
    padding: 10px 20px;
  }
}
</style>
