<template>
  <BasicModal
    v-bind="attrs"
    :is-padding="false"
    :loading="loading"
    width="800px"
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
                <AFormItem field="name" label="">
                  <ATextarea v-model="formData.text" :min-rows="6" placeholder="内容" />
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
import { cloneDeep } from 'lodash-es';
import type { FormInstance } from '@arco-design/web-vue';
import { Message } from '@arco-design/web-vue';
import useLoading from '@/hooks/loading';
import { useAttrs } from '@/hooks/core/useAttrs';
import { BasicModal, useModalInner } from '@/components/Modal';
import { updateDetail } from './api/index';

const attrs = useAttrs();
const emit = defineEmits(['success']);

const isUpdate = ref(false);
const modelHeight = ref(220);
const windHeight = ref(420);
// 表单
const formRef = ref<FormInstance>();
// 表单字段
const basedata = {
  id: 0,
  spkUserId: 0,
  text: ''
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
      await updateDetail(savedata);
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
