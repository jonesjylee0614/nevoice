<template>
  <BasicModal
    v-bind="attrs"
    :loading="loading"
    help-message="编辑和修改部门"
    width="600px"
    :min-height="280"
    :title="getTitle"
    @register="registerModal"
    @ok="handleSubmit"
  >
    <AForm ref="formRef" :model="formData" auto-label-width style="padding: 10px 20px">
      <AFormItem
        field="name"
        label="部门名称"
        validate-trigger="input"
        :rules="[{ required: true, message: '请填写部门名称' }]"
        style="margin-bottom: 15px"
      >
        <AInput v-model="formData.name" placeholder="请填写部门名称" />
      </AFormItem>
      <AFormItem label="上级部门" field="pid" style="margin-bottom: 15px">
        <ATreeSelect
          v-model="formData.pid"
          placeholder="选择上级部门"
          :data="parntList"
          :field-names="{
            key: 'id',
            title: 'name',
            children: 'children'
          }"
        ></ATreeSelect>
      </AFormItem>
      <AFormItem label="排序" field="weigh" style="margin-bottom: 15px">
        <AInputNumber v-model="formData.weigh" placeholder="请填排序" />
      </AFormItem>
      <AFormItem field="remark" label="备注" validate-trigger="input" style="margin-bottom: 15px">
        <ATextarea v-model="formData.remark" placeholder="请填写备注" allow-clear />
      </AFormItem>
    </AForm>
  </BasicModal>
</template>

<script lang="ts" setup>
import { cloneDeep } from 'lodash-es';
import type { FormInstance } from '@arco-design/web-vue';
import { Message } from '@arco-design/web-vue';
import { getParent, save } from '@/api/system/dept';
import useLoading from '@/hooks/loading';
import { BasicModal, useModalInner } from '@/components/Modal';
// api
const attrs = useAttrs();
const emit = defineEmits(['success']);

const isUpdate = ref(false);
const parntList = ref([]);
// 表单
const formRef = ref<FormInstance>();
// 表单字段
const basedata = {
  id: 0,
  name: '',
  pid: 0,
  weigh: 1,
  remark: ''
};
const formData = ref(basedata);
const m_component = ref('');
const [registerModal, { setModalProps, closeModal }] = useModalInner(async data => {
  formRef.value?.resetFields();
  setModalProps({ confirmLoading: false });
  const resultData = await getParent();
  const parentList_df: any = [{ id: 0, name: '一级部门', pid: 0 }];
  if (resultData) {
    parntList.value = parentList_df.concat(resultData);
  } else {
    parntList.value = parentList_df;
  }
  isUpdate.value = Boolean(data?.isUpdate);
  if (unref(isUpdate)) {
    m_component.value = data.record.component;
    formData.value = cloneDeep(data.record);
  } else {
    formData.value = cloneDeep(basedata);
  }
});
const getTitle = computed(() => (!isUpdate.value ? '新增部门' : '编辑部门'));
// 点击确认
const { loading, setLoading } = useLoading();
const handleSubmit = async () => {
  try {
    const res = await formRef.value?.validate();
    if (!res) {
      setLoading(true);

      await save(unref(formData));
      Message.success({ content: '更新成功', id: 'upStatus' });
      closeModal();
      emit('success');
      setLoading(false);
    }
  } catch (error) {
    setLoading(false);
  }
};
</script>
