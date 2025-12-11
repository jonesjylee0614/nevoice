<template>
  <div class="container">
    <div class="logo">
      <img alt="logo" src="/logo.png" style="width: 35px" />
      <div class="logo-text">{{ AppTitle }}</div>
    </div>
    <div class="content">
      <div class="content-inner">
        <LoginForm v-if="showType == 'login'" @reback="GoToType" />
        <ForgetForm v-else-if="showType == 'forget'" @reback="GoToType" />
      </div>
      <div class="footer">
        <Footer />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import Footer from '@/components/footer/index.vue';
import LoginForm from './components/login-form.vue';
import ForgetForm from './components/forget-form.vue';
// 获取网站配置-应用名称
const AppTitle = import.meta.env.VITE_APP_TITLE;
const showType = ref('login');
const GoToType = (keys: string) => {
  showType.value = keys;
};
</script>

<style lang="less" scoped>
.container {
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

  .content {
    position: relative;
    display: flex;
    flex: 1;
    align-items: center;
    justify-content: center;
    padding-bottom: 40px;
  }

  .content-inner {
    background: rgba(255, 255, 255, 0.95);
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  }

  .footer {
    position: absolute;
    right: 0;
    bottom: 0;
    width: 100%;
  }
}

.logo {
  position: fixed;
  top: 24px;
  left: 22px;
  z-index: 1;
  display: inline-flex;
  align-items: center;

  &-text {
    margin-right: 4px;
    margin-left: 4px;
    color: #fff;
    font-size: 20px;
    font-weight: 500;
  }
}
</style>

<style lang="less" scoped>
.logo-text {
  padding-top: 5px;
  padding-left: 5px;
}
</style>
