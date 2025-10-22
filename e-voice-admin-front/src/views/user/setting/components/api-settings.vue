<template>
  <AForm ref="formRef" :model="model" class="form" :label-col-props="{ span: 6 }" :wrapper-col-props="{ span: 18 }">
    <ASpace>
      <AFormItem field="appKey" label="AppKey">
        <AInput v-model="model.appKey" readonly />
      </AFormItem>
      <AFormItem field="appKeySecret" label="AppSecret">
        <AInput v-model="model.appKeySecret" readonly style="width: 350px" />
      </AFormItem>
      <AFormItem>
        <APopconfirm content="您确定要重新生成吗?" @ok="regen">
          <AButton type="primary">重新生成</AButton>
        </APopconfirm>
      </AFormItem>
    </ASpace>

    <ADescriptions title="加密规则(请求头)" layout="horizontal" :data="signDesData" :column="1" />
  </AForm>
</template>

<script lang="ts" setup>
import type { FormInstance } from '@arco-design/web-vue';
import { Message } from '@arco-design/web-vue';
import type { BasicInfoModel } from '@/api/user-center';
import { saveInfo } from '@/api/user-center';
import { generateRandomString } from '@/utils/string';

const signDesData = [
  {
    label: 'x-ak',
    value: 'appKey'
  },
  {
    label: 'x-t',
    value: '当前毫秒时间戳(误差不超过5分钟)'
  },
  {
    label: 'x-sign',
    value: 'md5( AppKey + AppSecret + t )'
  },
  {
    label: '接口文档',
    value: 'http://xx/xx/xx/'
  }
];

const model = defineModel<BasicInfoModel>('formData', { required: true });

const formRef = ref<FormInstance>();
const regen = async () => {
  // 重新生成ak sk
  model.value.appKey = generateRandomString(16);
  model.value.appKeySecret = generateRandomString(30);

  const res = await formRef.value?.validate();
  if (!res) {
    const res = await saveInfo(model.value);
    if (res) {
      Message.success({ content: '更新成功', id: 'delaction' });
    }
  }
};
</script>

<style scoped lang="less">
.form {
  width: 800px;
  margin: 0 auto;
}
</style>
