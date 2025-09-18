<template>
  <BasicModal
    v-bind="attrs"
    :loading="loading"
    :footer="false"
    width="600px"
    :min-height="390"
    :title="getTitle"
    @register="registerModal"
  >
    <div class="modalbox">
      <AForm ref="formRef" :model="formData" auto-label-width style="padding: 10px 20px" @submit="handleSubmit">
        <AFormItem
          field="name"
          label="名称"
          validate-trigger="input"
          :rules="[{ required: true, message: '请填写名称' }]"
        >
          <AInput v-model="formData.name" placeholder="请填写名称" />
        </AFormItem>
        <AFormItem
          field="path_url"
          label="跳转路径"
          validate-trigger="input"
          :rules="[{ required: true, message: '请填写跳转路径' }]"
        >
          <AInput v-model="formData.path_url" placeholder="请填跳转路径" />
        </AFormItem>
        <AFormItem field="icon" label="选择图标" :rules="[{ required: true, message: '请填写选择图标' }]">
          <AInputSearch v-model="formData.icon" placeholder="选择图标/填写" search-button>
            <template v-if="formData.icon" #prefix>
              <Icon :icon="formData.icon" />
            </template>
            <template #button-icon>
              <APopover position="br" trigger="click">
                <icon-apps :size="23" />
                <template #content>
                  <IconPicker
                    @change="
                      icon => {
                        formData.icon = icon;
                      }
                    "
                  ></IconPicker>
                </template>
              </APopover>
            </template>
          </AInputSearch>
        </AFormItem>
        <AFormItem label="类型" field="type" style="margin-bottom: 10px">
          <ARadioGroup v-model="formData.type">
            <ARadio :value="0">跳转系统</ARadio>
            <ARadio :value="1">跳转外部</ARadio>
          </ARadioGroup>
        </AFormItem>
        <AFormItem label="排序" field="weigh" style="margin-bottom: 15px">
          <AInputNumber v-model="formData.weigh" placeholder="请填排序" />
        </AFormItem>
        <AFormItem>
          <AButton
            type="primary"
            html-type="submit"
            :loading="loading"
            style="width: 150px; margin-left: 80px; margin-top: 15px"
          >
            提交
          </AButton>
        </AFormItem>
      </AForm>
    </div>
  </BasicModal>
</template>

<script lang="ts" setup>
import { cloneDeep } from 'lodash-es';
import type { FormInstance } from '@arco-design/web-vue';
import { Message } from '@arco-design/web-vue';
import { saveQuick } from '@/api/dashboard/workplace';
import useLoading from '@/hooks/loading';
import { BasicModal, useModalInner } from '@/components/Modal';
// api
import { Icon, IconPicker } from '@/components/Icon';

const attrs = useAttrs();
const emit = defineEmits(['success']);

const isUpdate = ref(false);
// 表单
const formRef = ref<FormInstance>();
// 表单字段
const basedata = {
  id: 0,
  type: 0,
  name: '',
  path_url: '',
  icon: '',
  weigh: 0
};
const formData = ref(basedata);
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
const getTitle = computed(() => (!unref(isUpdate) ? '新增快捷按键' : '编辑快捷按键'));
// 回复留言
const { loading, setLoading } = useLoading();
const handleSubmit = async () => {
  try {
    const res = await formRef.value?.validate();
    if (!res) {
      setLoading(true);

      await saveQuick(formData.value);
      Message.success({
        content: '提交成功',
        id: 'upStatus',
        duration: 2000
      });
      closeModal();
      emit('success');
      setLoading(false);
    }
  } catch (error) {
    setLoading(false);
  }
};
</script>

<style lang="less" scoped>
.modalbox {
  margin-bottom: 30px;
}
</style>
