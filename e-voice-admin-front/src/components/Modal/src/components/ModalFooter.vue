<template>
  <div>
    <slot name="insertFooter"></slot>
    <AButton v-if="showCancelBtn" @click="handleCancel">
      {{ cancelText }}
    </AButton>
    <slot name="centerFooter"></slot>
    <AButton v-if="showOkBtn" :loading="loading" :type="okType" style="margin-left: 8px" @click="handleOk">
      {{ okText }}
    </AButton>
    <slot name="appendFooter"></slot>
  </div>
</template>

<script lang="ts">
import { basicProps } from '../props';
export default defineComponent({
  name: 'BasicModalFooter',
  props: basicProps,
  emits: ['ok', 'cancel'],
  setup(_, { emit }) {
    function handleOk(e: Event) {
      emit('ok', e);
    }
    function handleCancel(e: Event) {
      emit('cancel', e);
    }

    return { handleOk, handleCancel };
  }
});
</script>
