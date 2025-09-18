<template>
  <ASpin :loading="loading" style="width: 100%">
    <AList :bordered="false">
      <AListItem>
        <AListItemMeta>
          <template #avatar>
            <ATypographyParagraph>
              {{ $t('userSetting.SecuritySettings.form.label.password') }}
            </ATypographyParagraph>
          </template>
          <template #description>
            <div class="content">
              <ATypographyParagraph>
                {{ $t('userSetting.SecuritySettings.placeholder.password') }}
              </ATypographyParagraph>
            </div>
            <div class="operation">
              <ALink @click="changePassWord = true">
                {{ $t('userSetting.SecuritySettings.button.update') }}
              </ALink>
            </div>
          </template>
        </AListItemMeta>
      </AListItem>
      <!--      <AListItem>-->
      <!--        <AListItemMeta>-->
      <!--          <template #avatar>-->
      <!--            <ATypographyParagraph>-->
      <!--              {{ $t('userSetting.SecuritySettings.form.label.securityQuestion') }}-->
      <!--            </ATypographyParagraph>-->
      <!--          </template>-->
      <!--          <template #description>-->
      <!--            <div class="content">-->
      <!--              <ATypographyParagraph class="tip">-->
      <!--                {{ $t('userSetting.SecuritySettings.placeholder.securityQuestion') }}-->
      <!--              </ATypographyParagraph>-->
      <!--            </div>-->
      <!--            <div class="operation">-->
      <!--              <ALink>-->
      <!--                {{ $t('userSetting.SecuritySettings.button.settings') }}-->
      <!--              </ALink>-->
      <!--            </div>-->
      <!--          </template>-->
      <!--        </AListItemMeta>-->
      <!--      </AListItem>-->
      <AListItem>
        <AListItemMeta>
          <template #avatar>
            <ATypographyParagraph>
              {{ $t('userSetting.SecuritySettings.form.label.phone') }}
            </ATypographyParagraph>
          </template>
          <template #description>
            <div class="content">
              <ATypographyParagraph>
                {{ phoneFilter(formData.mobile) }}
              </ATypographyParagraph>
            </div>
            <div class="operation">
              <ALink>
                {{ $t('userSetting.SecuritySettings.button.update') }}
              </ALink>
            </div>
          </template>
        </AListItemMeta>
      </AListItem>
      <AListItem>
        <AListItemMeta>
          <template #avatar>
            <ATypographyParagraph>
              {{ $t('userSetting.SecuritySettings.form.label.email') }}
            </ATypographyParagraph>
          </template>
          <template #description>
            <div class="content">
              <ATypographyParagraph :class="{ tip: !formData.email }">
                <template v-if="formData.email">
                  {{ formData.email }}
                </template>
                <template v-else>
                  {{ $t('userSetting.SecuritySettings.placeholder.email') }}
                </template>
              </ATypographyParagraph>
            </div>
            <div class="operation">
              <ALink>
                {{ $t('userSetting.SecuritySettings.button.update') }}
              </ALink>
            </div>
          </template>
        </AListItemMeta>
      </AListItem>
    </AList>
    <!--修改密码-->
    <AModal v-model:visible="changePassWord" title="修改密码" :on-before-ok="handlePassword">
      <AForm ref="formRef" :model="formpassword">
        <AFormItem field="oldpassword" label="原来密码" :rules="rules">
          <AInputPassword v-model="formpassword.oldpassword" allow-clear />
        </AFormItem>
        <AFormItem field="password" label="新密码" :rules="rulesnew">
          <AInputPassword v-model="formpassword.password" allow-clear />
        </AFormItem>
        <AFormItem field="secondpassword" label="确认密码" :rules="rulessecond">
          <AInputPassword v-model="formpassword.secondpassword" allow-clear />
        </AFormItem>
      </AForm>
    </AModal>
  </ASpin>
</template>

<script lang="ts" setup>
import { Message } from '@arco-design/web-vue';
import type { BasicInfoModel } from '@/api/user-center';
import { changePassword, checkPassword } from '@/api/user-center';
// import useLoading from '@/hooks/loading';
interface Props {
  formData?: BasicInfoModel;
  loading: boolean;
}

withDefaults(defineProps<Props>(), {
  formData: {} as any
});

// 修改密码
const formRef = ref();
const formpassword = ref({
  oldpassword: '',
  password: '',
  secondpassword: ''
});
const rules = [
  {
    validator: (value: any, cb: any) => {
      return new Promise(async resolve => {
        if (!value) {
          cb('请输入原来密码');
        } else {
          const resData = await checkPassword({ password: value });
          if (!resData) {
            cb('您输入的原来密码不正确！');
          }
        }
        resolve(null);
      });
    }
  }
];
// 新密码
const rulesnew = [
  {
    validator: (value: any, cb: any) => {
      return new Promise(resolve => {
        if (value == undefined) {
          cb('请输入新密码');
        } else if (value) {
          const passwordreg = /(?![A-Z]*$)(?![a-z]*$)(?![0-9]*$)(?![^a-zA-Z0-9]*$)/;
          if (!passwordreg.test(value)) {
            cb('密码必须由大写字母、小写字母、数字、特殊符号中的2种及以上类型组成!');
          }
        }
        resolve(null);
      });
    }
  }
];
// 确认密码
const rulessecond = [
  {
    validator: (value: any, cb: any) => {
      return new Promise(resolve => {
        if (value == undefined) {
          cb('请输入确认密码');
        } else if (value != formpassword.value.password) {
          cb('两次密码不一致');
        }
        resolve(null);
      });
    }
  }
];
const changePassWord = ref(false);
// 提交修改
const handlePassword = () => {
  formRef.value.validate(async (res: any) => {
    console.log('提交修改', res);
    if (res == undefined) {
      const resultdata = await changePassword({
        oldpassword: formpassword.value.oldpassword,
        password: formpassword.value.password
      });
      if (resultdata) {
        changePassWord.value = false;
        Message.success({ content: '修改密码成功', id: 'delaction' });
      }
    }
  });
  return false;
  // okLoading.value=false
};
// 手机号过滤器
const phoneFilter = (val: string) => {
  const reg = /^(.{3}).*(.{4})$/;
  return val.replace(reg, '$1****$2');
};
</script>

<style scoped lang="less">
:deep(.arco-list-item) {
  border-bottom: none !important;
  .arco-typography {
    margin-bottom: 20px;
  }
  .arco-list-item-meta-avatar {
    margin-bottom: 1px;
  }
  .arco-list-item-meta {
    padding: 0;
  }
}
:deep(.arco-list-item-meta-content) {
  flex: 1;
  border-bottom: 1px solid var(--color-neutral-3);

  .arco-list-item-meta-description {
    display: flex;
    flex-flow: row;
    justify-content: space-between;

    .tip {
      color: rgb(var(--gray-6));
    }
    .operation {
      margin-right: 6px;
    }
  }
}
</style>
