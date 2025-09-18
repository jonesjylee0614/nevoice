<template>
  <BasicModal
    v-bind="attrs"
    :is-padding="false"
    :loading="loading"
    width="600px"
    :min-height="modelHeight"
    :title="getTitle"
    @register="registerModal"
    @height-change="onHeightChange"
    @ok="handleSubmit"
  >
    <div class="addFormbox" :style="{ 'min-height': `${windHeight}px` }">
      <div class="tabs-content">
        <AForm ref="formRef" :model="formData" auto-label-width>
          <div class="content_box">
            <!--基础信息-->
            <AScrollbar style="overflow: auto" :style="{ height: `${windHeight}px` }">
              <div class="besecontent">
                <AFormItem field="name" label="微调任务名" required>
                  <AInput v-model="formData.name" placeholder="请填微调任务名" />
                </AFormItem>
                <AFormItem v-if="isUpdate" field="status" label="训练状态" required>
                  <ARadioGroup v-model="formData.status">
                    <ARadio :value="1">训练中</ARadio>
                    <ARadio :value="2">训练完成</ARadio>
                    <ARadio :value="3">待训练</ARadio>
                  </ARadioGroup>
                </AFormItem>
              </div>
            </AScrollbar>
          </div>
        </AForm>
      </div>
    </div>
  </BasicModal>
</template>

<script lang="ts" setup>
import dayjs from 'dayjs';
import { cloneDeep } from 'lodash-es';
import type { FormInstance } from '@arco-design/web-vue';
import { Message } from '@arco-design/web-vue';
import useLoading from '@/hooks/loading';
import { useAttrs } from '@/hooks/core/useAttrs';
import { BasicModal, useModalInner } from '@/components/Modal';
import { save } from './api/index';

const attrs = useAttrs();
const emit = defineEmits(['success']);

const isUpdate = ref(false);
const modelHeight = ref(220);
const windHeight = ref(220);
// 表单
const formRef = ref<FormInstance>();

const randomName = () => {
  const timestamp = dayjs().format('YYYY-MM-DD');
  const random = Math.floor(Math.random() * 10000);
  return `新建微调训练-${timestamp}_${random}`;
};

// 表单字段
const basedata = {
  id: 0,
  name: randomName(),
  baseModelPath: '',
  status: 3
};

const formData = ref<any>(basedata);
const [registerModal, { setModalProps, closeModal }] = useModalInner(async data => {
  formRef.value?.resetFields();
  setModalProps({ confirmLoading: false });
  isUpdate.value = Boolean(data?.isUpdate);
  if (unref(isUpdate)) {
    formData.value = cloneDeep(data.record);
  } else {
    formData.value = cloneDeep(basedata);
  }
});
const getTitle = computed(() => (!unref(isUpdate) ? '新增数据' : '编辑数据'));
// 点击确认
const { loading, setLoading } = useLoading();
const handleSubmit = async () => {
  try {
    const res = await formRef.value?.validate();
    if (!res) {
      setLoading(true);
      Message.loading({ content: '提交中', id: 'upStatus', duration: 0 });
      const savedata = cloneDeep(unref(formData));
      await save(savedata);
      Message.success({ content: '提交成功', id: 'upStatus', duration: 1500 });
      closeModal();
      formData.value = basedata;
      emit('success');
      setLoading(false);
    }
  } catch (error) {
    setLoading(false);
    Message.clear('top');
  }
};
// 监听高度
const onHeightChange = (val: any) => {
  windHeight.value = val;
};
</script>

<style lang="less" scoped>
@import '@/assets/style/formlayer.less';
</style>
