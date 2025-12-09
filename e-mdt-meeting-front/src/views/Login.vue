<template>
  <div class="login-page">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-circle bg-circle-1"></div>
      <div class="bg-circle bg-circle-2"></div>
      <div class="bg-circle bg-circle-3"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <!-- Logo 区域 -->
      <div class="login-header">
        <div class="logo-icon">
          <van-icon name="video-o" />
        </div>
        <h1 class="app-name">MDT 会议纪要系统</h1>
        <p class="app-desc">多学科团队会议智能记录与总结</p>
      </div>

      <!-- 登录表单 -->
      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">账号</label>
          <div class="input-wrapper">
            <van-icon name="user-o" class="input-icon" />
            <input
              v-model="formData.username"
              type="text"
              placeholder="请输入用户名"
              class="form-input"
              autocomplete="username"
            />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">密码</label>
          <div class="input-wrapper">
            <van-icon name="lock" class="input-icon" />
            <input
              v-model="formData.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码"
              class="form-input"
              autocomplete="current-password"
            />
            <van-icon
              :name="showPassword ? 'eye-o' : 'closed-eye'"
              class="toggle-password"
              @click="showPassword = !showPassword"
            />
          </div>
        </div>

        <div class="form-options">
          <label class="remember-me">
            <input type="checkbox" v-model="rememberMe" />
            <span>记住账号</span>
          </label>
        </div>

        <button type="submit" class="login-btn" :disabled="loading">
          <van-loading v-if="loading" size="20px" color="#fff" />
          <span v-else>登 录</span>
        </button>
      </form>

      <!-- 底部信息 -->
      <div class="login-footer">
        <p>© 2024 MDT 会议纪要系统</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { showToast, showSuccessToast } from 'vant'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 表单数据
const formData = reactive({
  username: '',
  password: ''
})

const showPassword = ref(false)
const rememberMe = ref(true)
const loading = ref(false)

// 从本地存储恢复记住的账号
onMounted(() => {
  const savedUsername = localStorage.getItem('mdt_remember_username')
  if (savedUsername) {
    formData.username = savedUsername
  }
})

// 登录处理
const handleLogin = async () => {
  if (!formData.username.trim()) {
    showToast('请输入用户名')
    return
  }
  if (!formData.password.trim()) {
    showToast('请输入密码')
    return
  }

  loading.value = true
  try {
    await userStore.login({
      username: formData.username.trim(),
      password: formData.password.trim()
    })

    // 记住账号
    if (rememberMe.value) {
      localStorage.setItem('mdt_remember_username', formData.username.trim())
    } else {
      localStorage.removeItem('mdt_remember_username')
    }

    showSuccessToast('登录成功')
    
    // 跳转到首页或之前的页面
    const redirect = (router.currentRoute.value.query.redirect as string) || '/'
    router.replace(redirect)
  } catch (error: any) {
    console.error('登录失败:', error)
    // 错误提示在 request 拦截器中处理
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

// 背景装饰
.bg-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
}

.bg-circle-1 {
  width: 600px;
  height: 600px;
  background: #fff;
  top: -200px;
  right: -100px;
}

.bg-circle-2 {
  width: 400px;
  height: 400px;
  background: #fff;
  bottom: -150px;
  left: -100px;
}

.bg-circle-3 {
  width: 200px;
  height: 200px;
  background: #fff;
  top: 50%;
  left: 10%;
}

// 登录卡片
.login-card {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 48px 40px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  position: relative;
  z-index: 1;
}

// 头部
.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-icon {
  width: 72px;
  height: 72px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 30px -10px rgba(102, 126, 234, 0.6);

  :deep(.van-icon) {
    font-size: 36px;
    color: #fff;
  }
}

.app-name {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.app-desc {
  font-size: 14px;
  color: #64748b;
}

// 表单
.login-form {
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 10px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 16px;
  font-size: 18px;
  color: #94a3b8;
  pointer-events: none;
}

.form-input {
  width: 100%;
  height: 52px;
  padding: 0 48px;
  border: 2px solid #e2e8f0;
  border-radius: 14px;
  font-size: 15px;
  color: #1e293b;
  background: #f8fafc;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
    background: #fff;
    box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
  }

  &::placeholder {
    color: #94a3b8;
  }
}

.toggle-password {
  position: absolute;
  right: 16px;
  font-size: 18px;
  color: #94a3b8;
  cursor: pointer;
  transition: color 0.2s;

  &:hover {
    color: #64748b;
  }
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #64748b;
  cursor: pointer;

  input[type="checkbox"] {
    width: 18px;
    height: 18px;
    accent-color: #667eea;
    cursor: pointer;
  }
}

.login-btn {
  width: 100%;
  height: 52px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 30px -10px rgba(102, 126, 234, 0.5);

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 15px 35px -10px rgba(102, 126, 234, 0.6);
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
}

// 底部
.login-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;

  p {
    font-size: 12px;
    color: #94a3b8;
  }
}

// 响应式
@media (max-width: 480px) {
  .login-card {
    padding: 36px 24px;
    border-radius: 20px;
  }

  .logo-icon {
    width: 60px;
    height: 60px;
    border-radius: 16px;

    :deep(.van-icon) {
      font-size: 30px;
    }
  }

  .app-name {
    font-size: 20px;
  }
}
</style>
