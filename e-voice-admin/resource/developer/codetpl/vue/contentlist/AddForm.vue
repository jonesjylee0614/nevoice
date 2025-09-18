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
                <ARow :gutter="16">
<!--replaceTpl-->
                </ARow>
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
import { BasicModal, useModalInner } from '@/components/Modal';
import { useAttrs } from '@/hooks/core/useAttrs';
import FileUpload from '@/components/upload/FileUpload.vue';
import ImgUpload from '@/components/upload/ImgUpload.vue';
import { save } from './api/index';

const attrs = useAttrs();
const emit = defineEmits(['success']);

const isUpdate = ref(false);
const modelHeight = ref(420);
const windHeight = ref(420);
// 表单
const formRef = ref<FormInstance>();
// 表单字段
const basedata = {
  id: 0,
replaceField:null
};
const formData = ref<any>(basedata);
// 编辑器
const editorRef = ref();
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

const state = {
  OYoptions: [
    { label: '否', value: 0 },
    { label: '是', value: 1 }
  ],
  SHoptions: [
    { label: '正常', value: 0 },
    { label: '禁用', value: 1 }
  ],
  tapList: [
    { id: 1, name: '基础内容' },
    { id: 2, name: '详细内容' }
  ]
};
const { OYoptions, SHoptions, tapList } = state;
</script>

<style lang="less" scoped>
@import '@/assets/style/formlayer.less';
</style>