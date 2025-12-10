<template>
  <BasicModal
    v-bind="$attrs"
    :title="getTitle"
    :width="700"
    :min-height="500"
    @register="registerModal"
    @ok="handleSubmit"
  >
    <AForm ref="formRef" :model="formModel" :rules="rules" auto-label-width>
      <AFormItem field="title" label="会议标题">
        <AInput v-model="formModel.title" placeholder="请输入会议标题（选填）" allow-clear />
        <template #extra>
          <div class="tip">留空时系统会自动以时间生成标题</div>
        </template>
      </AFormItem>
      <AFormItem field="startTime" label="开始时间">
        <ADatePicker
          v-model="formModel.startTime"
          show-time
          format="YYYY-MM-DD HH:mm"
          placeholder="请选择开始时间"
          style="width: 100%"
        />
      </AFormItem>
      <AFormItem field="endTime" label="结束时间">
        <ADatePicker
          v-model="formModel.endTime"
          show-time
          format="YYYY-MM-DD HH:mm"
          placeholder="请选择结束时间（选填）"
          style="width: 100%"
        />
      </AFormItem>
      <AFormItem field="hostName" label="主持人">
        <AInput v-model="formModel.hostName" placeholder="请输入主持人姓名（选填）" allow-clear />
      </AFormItem>
      <AFormItem field="description" label="会议说明">
        <ATextarea
          v-model="formModel.description"
          placeholder="请输入会议说明、参会科室等辅助信息（选填）"
          :max-length="500"
          :auto-size="{ minRows: 3, maxRows: 6 }"
          show-word-limit
        />
      </AFormItem>
      <AFormItem field="tags" label="标签">
        <AInputTag v-model="formModel.tags" placeholder="输入后按回车添加标签" allow-clear />
      </AFormItem>
    </AForm>
  </BasicModal>
</template>

<script lang="ts" setup>
import { Message } from '@arco-design/web-vue';
import type { FormInstance } from '@arco-design/web-vue/es/form';
import { BasicModal, useModalInner } from '@/components/Modal';
import { save, update } from './api';

const emit = defineEmits(['success', 'register']);

const formRef = ref<FormInstance>();
const isUpdate = ref(false);
const recordId = ref<number | null>(null);

const formModel = reactive({
  title: '',
  startTime: '',
  endTime: '',
  hostName: '',
  description: '',
  tags: [] as string[]
});

const rules = {
  // 可以根据需要添加验证规则
};

const [registerModal, { setModalProps, closeModal }] = useModalInner(async data => {
  formRef.value?.resetFields();
  isUpdate.value = Boolean(data?.isUpdate);

  if (data?.record) {
    recordId.value = data.record.id;
    formModel.title = data.record.title || '';
    formModel.startTime = data.record.startTime || '';
    formModel.endTime = data.record.endTime || '';
    formModel.hostName = data.record.hostName || '';
    formModel.description = data.record.description || '';
    // 解析标签
    if (data.record.tags) {
      try {
        formModel.tags = JSON.parse(data.record.tags);
      } catch {
        formModel.tags = [];
      }
    } else {
      formModel.tags = [];
    }
  } else {
    recordId.value = null;
    formModel.title = '';
    formModel.startTime = '';
    formModel.endTime = '';
    formModel.hostName = '';
    formModel.description = '';
    formModel.tags = [];
  }
});

const getTitle = computed(() => (isUpdate.value ? '编辑会议' : '新建会议'));

const handleSubmit = async () => {
  try {
    const valid = await formRef.value?.validate();
    if (valid) return;

    setModalProps({ confirmLoading: true });

    const params = {
      ...formModel
    };

    if (isUpdate.value && recordId.value) {
      await update({ id: recordId.value, ...params });
      Message.success('更新成功');
      closeModal();
      emit('success');
    } else {
      const result = await save(params);
      Message.success('创建成功');
      closeModal();
      // 新建会议后询问是否进入会议详情
      if (result?.id) {
        emit('success', { newMeetingId: result.id });
      } else {
        emit('success');
      }
    }
  } catch (error) {
    // 错误处理
  } finally {
    setModalProps({ confirmLoading: false });
  }
};
</script>

<style scoped lang="less">
.tip {
  color: var(--color-text-3);
  font-size: 12px;
}
</style>
