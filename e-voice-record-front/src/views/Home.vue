<script setup lang="ts">

const router = useRouter()
const isLoggedIn = ref(false) // 这里可以通过pinia存储登录状态

const goToLogin = () => {
  router.push('/login')
}

const goToVoiceList = () => {
  router.push('/voice-list')
}
</script>

<template>
  <div class="home">
    <h1 class="title">欢迎使用语音录入系统</h1>
    <div class="button-group">
      <van-button v-if="!isLoggedIn" @click="goToLogin" type="success" size="large">登录</van-button>
      <van-button v-else @click="goToVoiceList" class="btn">进入语音录入</van-button>
    </div>
  </div>
</template>

<style scoped>
.home {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  box-sizing: border-box;
}

.title {
  font-size: clamp(1.5rem, 5vw, 2rem);
  text-align: center;
  margin: 0 0 2rem;
  padding: 0 1rem;
}

.button-group {
  margin-top: 2rem;
  width: 100%;
  max-width: 300px;
  padding: 0 1rem;
}
</style>