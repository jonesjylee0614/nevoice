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
                  <ACol :span="16">
                    <AFormItem
                      field="title"
                      label="名称"
                      validate-trigger="input"
                      :rules="[{ required: true, message: '请填写名称' }]"
                    >
                      <AInput
                        v-model="formData.title"
                        placeholder="请填名称"
                        :max-length="50"
                        allow-clear
                        show-word-limit
                      />
                    </AFormItem>
                  </ACol>
                  <ACol :span="12">
                    <AFormItem field="weigh" label="排序" validate-trigger="input" style="margin-bottom: 15px">
                      <AInputNumber v-model="formData.weigh" placeholder="请填排序" />
                    </AFormItem>
                  </ACol>
                  <ACol :span="12">
                    <AFormItem field="status" label="状态" style="margin-bottom: 5px">
                      <ARadioGroup v-model="formData.status" :options="OYoptions" />
                    </AFormItem>
                  </ACol>
                  <ACol :span="24">
                    <AFormItem field="remark" label="备注" style="margin-bottom: 15px">
                      <ATextarea
                        v-model="formData.remark"
                        placeholder="请填备注"
                        :max-length="200"
                        allow-clear
                        show-word-limit
                        :auto-size="{ minRows: 3, maxRows: 5 }"
                      />
                    </AFormItem>
                  </ACol>
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
import { save } from '@/api/datacenter/tabledata';
import useLoading from '@/hooks/loading';
import { BasicModal, useModalInner } from '@/components/Modal';
// api

const attrs = useAttrs();
const emit = defineEmits(['success']);
const isUpdate = ref(false);
const modelHeight = ref(350);
const windHeight = ref(350);
// 表单
const { loading, setLoading } = useLoading();
const formRef = ref<FormInstance>();
// 表单字段
const basedata = {
  id: 0,
  title: '',
  remark: '',
  status: 0,
  weigh: 1
};
const formData = ref(basedata);
// 编辑器
const [registerModal, { setModalProps, closeModal }] = useModalInner(async data => {
  formRef.value?.resetFields();
  setLoading(true);
  setModalProps({ confirmLoading: false });
  isUpdate.value = Boolean(data?.isUpdate);
  if (unref(isUpdate)) {
    formData.value = cloneDeep(data.record);
  } else {
    formData.value = cloneDeep(basedata);
  }
  setLoading(false);
});
const getTitle = computed(() => (!unref(isUpdate) ? '新增数据' : '编辑数据'));
// 点击保存数据
const handleSubmit = async () => {
  try {
    const res = await formRef.value?.validate();
    if (!res) {
      setLoading(true);

      const savedata = cloneDeep(unref(formData));
      await save(savedata);
      Message.success({ content: '提交成功', id: 'upStatus' });
      closeModal();
      formData.value = basedata;
      emit('success');
      setLoading(false);
    }
  } catch (error) {
    setLoading(false);
  }
};
// 监听高度
const onHeightChange = (val: any) => {
  windHeight.value = val;
};

const OYoptions = [
  { label: '正常', value: 0 },
  { label: '禁用', value: 1 }
];
</script>

<style lang="less" scoped>
@import '@/assets/style/formlayer.less';
.tabs-content {
  padding: 0 25px;
}
</style>
