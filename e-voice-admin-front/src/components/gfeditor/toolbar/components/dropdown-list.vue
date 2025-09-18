<template>
  <div
    ref="element"
    class="toolbar-dropdown-list"
    :class="[
      `toolbar-dropdown-${direction || 'vertical'}`,
      { [`toolbar-dropdown-placement-${placement}`]: !!placement },
      { 'toolbar-dropdown-dot': hasDot !== false },
      className
    ]"
  >
    <template v-for="{ key, placement, title, content, className, icon, disabled } in items" :key="key">
      <ATooltip v-if="(!!title || !!hotkeys[key]) && !isMobile" :position="placement || 'right'">
        <template #content>
          <div v-if="!!title" class="toolbar-tooltip-title">{{ title }}</div>
          <div v-if="!!hotkeys[key]" class="toolbar-tooltip-hotkey" v-html="hotkeys[key]"></div>
        </template>
        <a
          class="toolbar-dropdown-list-item"
          :class="[className, { 'toolbar-dropdown-list-item-disabled': disabled }]"
          @click="triggerSelect($event, key)"
        >
          <span
            v-if="
              ((typeof values === 'string' && values === key) || (Array.isArray(values) && values.includes(key))) &&
              direction !== 'horizontal' &&
              hasDot !== false
            "
            class="data-icon data-icon-dot"
          ></span>
          <slot name="icon"><span v-if="icon" class="data-icon" :class="[`data-icon-${icon}`]" /></slot>
          <div v-html="typeof content === 'function' ? content(engine) : content"></div>
        </a>
      </ATooltip>
      <a
        v-else
        class="toolbar-dropdown-list-item"
        :class="[className, { 'toolbar-dropdown-list-item-disabled': disabled }]"
        @click="triggerSelect($event, key)"
      >
        <span
          v-if="
            ((typeof values === 'string' && values === key) || (Array.isArray(values) && values.includes(key))) &&
            direction !== 'horizontal' &&
            hasDot !== false
          "
          class="data-icon data-icon-dot"
        ></span>
        <slot name="icon"><span v-if="icon" class="data-icon" :class="[`data-icon-${icon}`]" /></slot>
        <div v-html="typeof content === 'function' ? content(engine) : content"></div>
      </a>
    </template>
  </div>
</template>

<script lang="ts" setup>
import { formatHotkey, isMobile } from '@/components/gfeditor/emain';
import type { DropdownListItem } from '../types';
import { dropdownListProps } from '../types';
import { autoGetHotkey } from '../utils';

const props = defineProps(dropdownListProps);

const placement = ref<string>('');
const element = ref<HTMLElement | null>(null);
const getHotkey = (item: DropdownListItem) => {
  const { command, key } = item;
  let { hotkey } = item;
  // 默认获取插件的热键
  if (props.engine && (hotkey === true || hotkey === undefined)) {
    hotkey = autoGetHotkey(props.engine, command && !Array.isArray(command) ? command.name : props.name, key);
  }
  if (typeof hotkey === 'string' && hotkey !== '') {
    hotkey = formatHotkey(hotkey);
  }
  return hotkey;
};

const hotkeys: { [key: string]: any } = {};
props.items.forEach(item => {
  hotkeys[item.key] = getHotkey(item);
});

const triggerSelect = (event: MouseEvent, key: string) => {
  event.preventDefault();
  event.stopPropagation();
  const item = props.items.find(item => item.key === key);
  if (!item || item.disabled) return;
  const { autoExecute, command } = item;
  if (props.onSelect && props.onSelect(event, key, props.engine) === false) return;
  if (autoExecute !== false) {
    let commandName = props.name;
    let commandArgs = [key];
    if (command) {
      if (!Array.isArray(command)) {
        commandName = command.name;
        commandArgs = commandArgs.concat(command.args);
      } else {
        commandArgs = commandArgs.concat(command);
      }
    }
    if (props.engine) props.engine.command.execute(commandName, ...commandArgs);
  }
};

onMounted(() => {
  if (element.value && props.engine && props.engine.scrollNode) {
    const ev = element.value;
    const scrollElement = props.engine.scrollNode.get<HTMLElement>();
    if (!scrollElement) return;
    const rect = ev.getBoundingClientRect();
    const scrollRect = scrollElement.getBoundingClientRect();
    if (rect.top < scrollRect.top) placement.value = 'bottom';
    if (rect.bottom > scrollRect.bottom) placement.value = 'top';
  }
});
</script>
