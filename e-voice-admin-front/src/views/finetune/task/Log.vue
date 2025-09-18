<template>
  <ADrawer v-model:visible="model.visible" placement="right" width="1000px">
    <pre style="font-size: 10px">{{ model.data }}</pre>
  </ADrawer>
</template>

<script setup lang="ts">
import { fetchLog } from '@/views/finetune/task/api';

export interface LogModel {
  data?: string;
  taskId: any;
  visible: boolean;
  running: boolean;
}

const emit = defineEmits(['success']);

const model = defineModel<LogModel>('logModel', {
  required: true,
  default: {
    data: '获取日志中...'
  }
});

let i = 0;
const getLog = async () => {
  try {
    const { log, lastLine } = await fetchLog({ id: model.value.taskId });
    model.value.data = log;
    // 判断最后一行是否为Finished training
    if (lastLine.startsWith('Finished training')) {
      emit('success');
      clearInterval(i);
    }
  } catch (e) {}
};

watch(
  () => model.value.visible,
  val => {
    clearInterval(i);
    if (val) {
      getLog();
      // 运行中的日志定时刷新
      if (model.value.running) {
        i = setInterval(getLog, 1000) as any;
      }
    }
  }
);
</script>

<style scoped lang="less"></style>
