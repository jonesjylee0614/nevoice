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
            <AScrollbar style="overflow: auto" :style="{ height: `${windHeight}px` }">
              <div class="besecontent">
                <AFormItem v-if="!isUpdate" field="audio" label="上传音频" :required="!isUpdate">
                  <AudioUpload ref="audioUploadRef" :params="formData" @change="file => (formData.audio = file)" />
                </AFormItem>
                <AFormItem field="text" label="语料对应的文字" required>
                  <ATextarea
                    v-model="formData.text"
                    placeholder="请填语料对应的文字"
                    :auto-size="{ minRows: 4, maxRows: 5 }"
                  />
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
import AudioUpload from '@/views/finetune/detail/AudioUpload.vue';
import { update } from './api/index';

const attrs = useAttrs();
const emit = defineEmits(['success']);

const audioUploadRef = ref();
const isUpdate = ref(false);
const modelHeight = ref(250);
const windHeight = ref(250);
// 表单
const formRef = ref<FormInstance>();
// 表单字段
const basedata = {
  id: 0,
  finetuneId: 0,
  voicePath: '',
  text: '',
  meetingDetailId: 0
};
const formData = ref<any>(basedata);
// 编辑器
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
      if (!isUpdate.value) {
        await audioUploadRef.value.submit();
      } else {
        await update(savedata);
      }
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
