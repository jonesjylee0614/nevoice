<template>
  <div class="login-form-wrapper">
    <div class="login-form-title">{{ loginTitle }}</div>
    <div class="login-form-sub-title">
      {{ loginSubTitle }}
    </div>
    <div class="login-form-error-msg">{{ errorMessage }}</div>
    <AForm :model="userInfo" class="login-form" layout="vertical" @submit="handleSubmit">
      <AFormItem
        field="username"
        :rules="[{ required: true, message: $t('login.form.userName.errMsg') }]"
        :validate-trigger="['change', 'blur']"
        hide-label
      >
        <AInput v-model="userInfo.username" :placeholder="$t('login.form.userName.placeholder')">
          <template #prefix>
            <icon-user />
          </template>
        </AInput>
      </AFormItem>
      <AFormItem
        field="password"
        :rules="[{ required: true, message: $t('login.form.password.errMsg') }]"
        :validate-trigger="['change', 'blur']"
        hide-label
      >
        <AInputPassword v-model="userInfo.password" :placeholder="$t('login.form.password.placeholder')" allow-clear>
          <template #prefix>
            <icon-lock />
          </template>
        </AInputPassword>
      </AFormItem>
      <ASpace :size="16" direction="vertical">
        <AButton type="primary" html-type="submit" long :loading="loading">
          {{ $t('login.form.login') }}
        </AButton>
        <!--
 <a-button type="text" long class="login-form-register-btn">
          {{ $t('login.form.register') }}
        </a-button> 
-->
      </ASpace>
    </AForm>

    <GoCaptcha ref="captchaRef" v-model:visible="captchaVisible" @success="handleSuccess" />
  </div>
</template>

<script lang="ts" setup>
import { Message } from '@arco-design/web-vue';
import type { ValidatedError } from '@arco-design/web-vue/es/form/interface';
import type { LoginData } from '@/api/user';
import { useUserStore } from '@/store';
import useLoading from '@/hooks/loading';
import GoCaptcha from '@/components/captcha/go-captcha.vue';

const captchaVisible = ref(false);
const captchaRef = ref();

const emit = defineEmits(['reback']);
const router = useRouter();
// 获取标题
const loginTitle = `登录${import.meta.env.VITE_APP_TITLE}`;
const loginSubTitle = '';
const errorMessage = ref('');
const { loading, setLoading } = useLoading();
const userStore = useUserStore();
const userInfo = reactive({
  username: '',
  password: ''
});

async function handleSubmit({
  errors,
  values
}: {
  errors: Record<string, ValidatedError> | undefined;
  values: Record<string, any>;
}) {
  if (loading.value || errors) return;

  captchaVisible.value = true;
}

const handleSuccess = async (data: any) => {
  if (loading.value) return;
  setLoading(true);
  try {
    const loginData = {
      ...userInfo,
      ...data,
      t: new Date().getTime()
    };
    const res = await userStore.login(loginData as LoginData);
    if (!res) {
      console.log(res);
      captchaRef.value.reset();
      return;
    }

    const { redirect, ...othersQuery } = router.currentRoute.value.query;
    let toURl = redirect as string;
    if (toURl == 'notFound') {
      toURl = 'home';
    }
    router.replace({
      name: toURl || 'home',
      query: {
        ...othersQuery
      }
    });
    Message.success({ content: '欢迎使用', id: 'menuNotice' });
  } catch (err) {
    errorMessage.value = (err as Error).message;
  } finally {
    setLoading(false);
  }
};
</script>

<style lang="less" scoped>
.login-form {
  &-wrapper {
    width: 320px;
  }

  &-title {
    color: var(--color-text-1);
    font-weight: 500;
    font-size: 24px;
    line-height: 32px;
  }

  &-sub-title {
    color: var(--color-text-3);
    font-size: 16px;
    line-height: 24px;
  }

  &-error-msg {
    height: 32px;
    color: rgb(var(--red-6));
    line-height: 32px;
  }

  &-password-actions {
    display: flex;
    justify-content: space-between;
  }

  &-register-btn {
    color: var(--color-text-3) !important;
  }
}
</style>
