<template>
  <div class="login">
    <van-form class="login-form" @submit.prevent="handleLogin">
      <h2 class="form-title">用户登录</h2>

      <van-cell-group inset>
        <van-field
            v-model="username"
            name="用户名"
            label="用户名"
            placeholder="用户名"
            :rules="[{ required: true, message: '请填写用户名' }]"
        />
        <van-field
            v-model="password"
            type="password"
            name="密码"
            label="密码"
            placeholder="密码"
            :rules="[{ required: true, message: '请填写密码' }]"
        />
      </van-cell-group>
      <van-button type="success" @click="handleLogin" size="large">登录</van-button>
    </van-form>
  </div>
</template>

<script setup>
import {useAuthStore} from "@/stores/auth";
import {showToast} from "vant";

const router = useRouter()
const username = ref('')
const password = ref('')

const auth = useAuthStore()

const handleLogin = () => {
  if (username.value && password.value) {
    // 这里添加实际的登录逻辑
    localStorage.setItem('isLoggedIn', 'true') // 简单存储登录状态

    auth.login({
      id: 1,
      username: username.value,
      password: password.value,
      token: '123',
    })
    router.push('/voice-list')

  } else {
    showToast('请输入用户名和密码');
  }
}
</script>

<style scoped>
.login {
  padding: 1rem;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  box-sizing: border-box;
}

.login-form {
  width: 100%;
  max-width: 350px;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.form-title {
  text-align: center;
  margin-bottom: 2rem;
  font-size: 1.5rem;
  color: #333;
}

.form-item {
  margin-bottom: 1rem;
}

input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box;
  outline: none;
  transition: border-color 0.3s;
}

input:focus {
  border-color: #4CAF50;
}

</style>