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
                      field="keyname"
                      label="字典名称"
                      validate-trigger="input"
                      :rules="[{ required: true, message: '请填写字典名称' }]"
                    >
                      <AInput
                        v-model="formData.keyname"
                        placeholder="填写字典名称"
                        :max-length="50"
                        allow-clear
                        show-word-limit
                      />
                    </AFormItem>
                  </ACol>
                  <ACol :span="16">
                    <AFormItem
                      field="keyvalue"
                      label="字典项值"
                      validate-trigger="input"
                      :rules="[{ required: true, message: '请填字典项值' }]"
                    >
                      <AInput
                        v-model="formData.keyvalue"
                        placeholder="填写字典项值"
                        :max-length="50"
                        allow-clear
                        show-word-limit
                      />
                    </AFormItem>
                  </ACol>
                  <ACol :span="16">
                    <AFormItem field="weigh" label="排序" validate-trigger="input" style="margin-bottom: 15px">
                      <AInputNumber v-model="formData.weigh" placeholder="请填排序" />
                    </AFormItem>
                  </ACol>
                  <ACol :span="24">
                    <AFormItem field="des" label="字典描述" style="margin-bottom: 15px">
                      <ATextarea
                        v-model="formData.des"
                        placeholder="请填字典描述"
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
import { save } from '@/api/datacenter/dictionary';
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
  keyname: '',
  keyvalue: '',
  des: '',
  tablename: '',
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
  formData.value.tablename = data.tablename;
  setLoading(false);
});
const getTitle = computed(() => (!unref(isUpdate) ? '新增数据' : '编辑数据'));
// 点击保存数据
const handleSubmit = async () => {
  try {
    const res = await formRef.value?.validate();
    if (!res) {
      setLoading(true);
      await save(unref(formData));
      Message.success({ content: '提交成功', id: 'upStatus' });
      closeModal();
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
</script>

<style lang="less" scoped>
@import '@/assets/style/formlayer.less';
//上传图片
</style>
