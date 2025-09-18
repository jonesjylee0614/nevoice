<template>
  <span class="colorpicker-group">
    <AmColorPickerItem
      v-for="color in colors"
      :key="color.value"
      :engine="engine"
      :color="color.value"
      :active="color.active"
      :on-select="onSelect"
      :set-stroke="setStroke"
    />
  </span>
</template>

<script lang="ts">
import { colorPickerGroupProps } from '../../../types';
import AmColorPickerItem from './item.vue';

export default defineComponent({
  name: 'AmColorPlickerGroup',
  components: {
    AmColorPickerItem
  },
  props: colorPickerGroupProps
});
</script>
