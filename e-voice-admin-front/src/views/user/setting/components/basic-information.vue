<template>
  <ASpin :loading="loading" style="width: 100%">
    <AForm ref="formRef" :model="model" class="form" :label-col-props="{ span: 8 }" :wrapper-col-props="{ span: 16 }">
      <AFormItem
        field="email"
        :label="$t('userSetting.basicInfo.form.label.email')"
        :rules="[
          {
            required: true,
            message: $t('userSetting.form.error.email.required')
          }
        ]"
      >
        <AInput v-model="model.email" :placeholder="$t('userSetting.basicInfo.placeholder.email')" />
      </AFormItem>
      <AFormItem
        field="nickname"
        :label="$t('userSetting.basicInfo.form.label.nickname')"
        :rules="[
          {
            required: true,
            message: $t('userSetting.form.error.nickname.required')
          }
        ]"
      >
        <AInput v-model="model.nickname" :placeholder="$t('userSetting.basicInfo.placeholder.nickname')" />
      </AFormItem>
      <!--      <AFormItem field="area" :label="$t('userSetting.basicInfo.form.label.area')">-->
      <!--        <ACascader-->
      <!--          v-model="model.area"-->
      <!--          :placeholder="$t('userSetting.basicInfo.placeholder.area')"-->
      <!--          :options="[-->
      <!--            {-->
      <!--              label: '北京',-->
      <!--              value: 'beijing',-->
      <!--              children: [-->
      <!--                {-->
      <!--                  label: '北京',-->
      <!--                  value: 'beijing',-->
      <!--                  children: [-->
      <!--                    {-->
      <!--                      label: '朝阳',-->
      <!--                      value: 'chaoyang'-->
      <!--                    }-->
      <!--                  ]-->
      <!--                }-->
      <!--              ]-->
      <!--            }-->
      <!--          ]"-->
      <!--          allow-clear-->
      <!--        />-->
      <!--      </AFormItem>-->
      <AFormItem field="address" :label="$t('userSetting.basicInfo.form.label.address')">
        <AInput v-model="model.address" :placeholder="$t('userSetting.basicInfo.placeholder.address')" />
      </AFormItem>
      <AFormItem
        field="profile"
        :label="$t('userSetting.basicInfo.form.label.profile')"
        :rules="[
          {
            maxLength: 200,
            message: $t('userSetting.form.error.profile.maxLength')
          }
        ]"
        row-class="keep-margin"
      >
        <ATextarea v-model="model.remark" :placeholder="$t('userSetting.basicInfo.placeholder.profile')" />
      </AFormItem>
      <AFormItem>
        <ASpace>
          <AButton type="primary" @click="validate">
            {{ $t('userSetting.save') }}
          </AButton>
          <AButton type="secondary" @click="reset">
            {{ $t('userSetting.reset') }}
          </AButton>
        </ASpace>
      </AFormItem>
    </AForm>
  </ASpin>
</template>

<script lang="ts" setup>
import type { FormInstance } from '@arco-design/web-vue';
import { Message } from '@arco-design/web-vue';
import type { BasicInfoModel } from '@/api/user-center';
import { saveInfo } from '@/api/user-center';
import useLoading from '@/hooks/loading';

const formRef = ref<FormInstance>();
const model = defineModel<BasicInfoModel>('formData', { required: true });

const { loading, setLoading } = useLoading(true);
const validate = async () => {
  const res = await formRef.value?.validate();
  setLoading(true);
  if (!res) {
    const res = await saveInfo(model.value);
    if (res) {
      Message.success({ content: '更新成功', id: 'delaction' });
    }
  }

  setLoading(false);
};
const reset = async () => {
  await formRef.value?.resetFields();
};
</script>

<style scoped lang="less">
.form {
  width: 540px;
  margin: 0 auto;
}
</style>
