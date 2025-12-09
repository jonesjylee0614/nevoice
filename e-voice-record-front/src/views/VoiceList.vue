<template>
  <div class="voice-list-page">
    <!-- 背景装饰 -->
    <div class="page-bg">
      <div class="bg-circle bg-circle-1"></div>
      <div class="bg-circle bg-circle-2"></div>
    </div>

    <!-- 顶部导航 -->
    <van-nav-bar title="声纹管理" class="glass-nav" />

    <!-- 页面内容 -->
    <div class="page-content">
      <!-- 页面头部 -->
      <header class="page-header">
        <div class="header-icon">
          <van-icon name="audio" />
        </div>
        <div class="header-text">
          <h1>声纹录制中心</h1>
          <p>录制您的声纹样本，用于语音识别和身份认证</p>
        </div>
      </header>

      <!-- 用户信息卡片 -->
      <div class="user-card" v-if="authStore.getUser">
        <div class="user-avatar">
          <van-icon name="user-circle-o" />
        </div>
        <div class="user-info">
          <div class="user-name">{{ authStore.getUser.username || authStore.getUser.name || '用户' }}</div>
          <div class="user-id">ID: {{ authStore.getUser.userId }}</div>
        </div>
        <div class="user-status" :class="{ active: valid }">
          <span class="status-dot"></span>
          {{ valid ? '已认证' : '未认证' }}
        </div>
      </div>

      <!-- 链接失效提示 -->
      <div class="invalid-card" v-if="!valid && !loading">
        <van-icon name="warning-o" class="invalid-icon" />
        <h3>链接已失效</h3>
        <p>请从管理后台重新获取录音链接</p>
      </div>

      <!-- 录音记录列表 -->
      <div class="records-section" v-if="valid">
        <div class="section-header">
          <h2>
            <van-icon name="records" />
            录音记录
          </h2>
          <span class="record-count">共 {{ sentences.length }} 条</span>
        </div>

        <div class="records-list" v-if="sentences.length > 0">
          <div 
            v-for="(item, index) in sentences" 
            :key="item.id"
            class="record-item"
            :style="{ animationDelay: `${index * 0.05}s` }"
          >
            <div class="record-icon">
              <van-icon name="volume-o" />
            </div>
            <div class="record-content">
              <div class="record-text">{{ item.txt || '语音片段 ' + (index + 1) }}</div>
              <div class="record-meta">
                <span v-if="item.create_time">{{ formatTime(item.create_time) }}</span>
              </div>
            </div>
            <van-icon name="arrow" class="record-arrow" />
          </div>
        </div>

        <div class="empty-state" v-else>
          <div class="empty-icon">
            <van-icon name="audio" />
          </div>
          <p>暂无录音记录</p>
          <span>点击下方按钮开始录制您的第一条声纹</span>
        </div>
      </div>

      <!-- 新增录音按钮 -->
      <div class="action-bar" v-if="valid">
        <button class="add-record-btn" @click="goToRecord()">
          <van-icon name="plus" />
          <span>新增录音</span>
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="loading">
      <van-loading size="32px" vertical>验证中...</van-loading>
    </div>
  </div>
</template>

<script setup lang="ts">
import { setLimitedToken } from '@/service/request'
import { getUserInfo, getUserPrints } from "@/views/api/voice.js";
import { useAuthStore } from '@/stores/auth';

const router = useRouter()
const sentences = ref([])
const authStore = useAuthStore()
const valid = ref(false)
const loading = ref(true)

const goToRecord = () => {
  router.push(`/voice-record/rec`)
}

const loadSentences = async (userId: any) => {
  try {
    const { data } = await getUserPrints(userId)
    sentences.value = data.data?.items || []
  } catch (error) {
    console.error('获取录音列表失败:', error)
    sentences.value = []
  }
}

const formatTime = (time: string) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(async () => {
  // 检查URL中是否有token参数
  const token = router.currentRoute.value.query.token
  if (token) {
    // 设置全局token
    setLimitedToken(token as string)
  }

  // 获取用户信息
  try {
    const { data } = await getUserInfo()
    if (data.data?.userId) {
      // 将用户信息存储到Pinia store中
      authStore.login(data.data)
      // 设置登录状态
      localStorage.setItem('isLoggedIn', 'true')
      valid.value = true
      await loadSentences(data.data.userId)
    }
  } catch (e) {
    console.error('Token验证失败:', e)
    localStorage.removeItem('isLoggedIn')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.voice-list-page {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
  padding-bottom: 100px;
}

/* 背景装饰 */
.page-bg {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 100vh;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
}

.bg-circle-1 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #a5b4fc 0%, #818cf8 100%);
  top: -100px;
  right: -80px;
  opacity: 0.5;
}

.bg-circle-2 {
  width: 250px;
  height: 250px;
  background: linear-gradient(135deg, #c4b5fd 0%, #a78bfa 100%);
  top: 30%;
  left: -100px;
  opacity: 0.4;
}

/* 玻璃导航 */
.glass-nav {
  position: relative;
  z-index: 10;
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

/* 页面内容 */
.page-content {
  position: relative;
  z-index: 1;
  padding: 20px;
  max-width: 480px;
  margin: 0 auto;
}

/* 页面头部 */
.page-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 24px;
  animation: fadeInUp 0.5s ease forwards;
}

.header-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: var(--shadow-primary);
}

.header-icon :deep(.van-icon) {
  font-size: 28px;
  color: white;
}

.header-text h1 {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 6px;
}

.header-text p {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* 用户卡片 */
.user-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--surface);
  border-radius: 20px;
  padding: 18px 20px;
  margin-bottom: 24px;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-light);
  animation: fadeInUp 0.5s ease 0.1s forwards;
  opacity: 0;
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-avatar :deep(.van-icon) {
  font-size: 28px;
  color: var(--primary);
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 4px;
}

.user-id {
  font-size: 12px;
  color: var(--text-tertiary);
}

.user-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: var(--surface-muted);
  color: var(--text-secondary);
}

.user-status.active {
  background: var(--success-light);
  color: var(--success);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

/* 链接失效提示 */
.invalid-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 60px 20px;
  background: var(--surface);
  border-radius: 20px;
  box-shadow: var(--shadow-md);
  animation: fadeInUp 0.5s ease forwards;
}

.invalid-icon {
  font-size: 64px;
  color: var(--warning);
  margin-bottom: 20px;
}

.invalid-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 8px;
}

.invalid-card p {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 录音记录区域 */
.records-section {
  animation: fadeInUp 0.5s ease 0.2s forwards;
  opacity: 0;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-header h2 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
}

.section-header h2 :deep(.van-icon) {
  font-size: 18px;
  color: var(--primary);
}

.record-count {
  font-size: 13px;
  color: var(--text-tertiary);
}

/* 录音列表 */
.records-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-item {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--surface);
  border-radius: 16px;
  padding: 16px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
  cursor: pointer;
  transition: all 0.3s ease;
  animation: fadeInUp 0.4s ease forwards;
  opacity: 0;
}

.record-item:hover {
  transform: translateX(4px);
  box-shadow: var(--shadow-md);
  border-color: var(--primary-light);
}

.record-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: var(--primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.record-icon :deep(.van-icon) {
  font-size: 20px;
  color: var(--primary);
}

.record-content {
  flex: 1;
  min-width: 0;
}

.record-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-main);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.record-meta {
  font-size: 12px;
  color: var(--text-tertiary);
}

.record-arrow {
  font-size: 16px;
  color: var(--text-tertiary);
  flex-shrink: 0;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.empty-icon :deep(.van-icon) {
  font-size: 36px;
  color: var(--primary);
  opacity: 0.6;
}

.empty-state p {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-main);
  margin-bottom: 6px;
}

.empty-state span {
  font-size: 13px;
  color: var(--text-tertiary);
}

/* 操作栏 */
.action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;
  background: linear-gradient(180deg, transparent 0%, rgba(255,255,255,0.9) 20%, #fff 100%);
  z-index: 100;
}

.add-record-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  max-width: 440px;
  margin: 0 auto;
  height: 54px;
  border-radius: 16px;
  border: none;
  background: var(--primary-gradient);
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: var(--shadow-primary);
  transition: all 0.3s ease;
}

.add-record-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 40px -10px rgba(99, 102, 241, 0.6);
}

.add-record-btn :deep(.van-icon) {
  font-size: 20px;
}

/* 加载状态 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* 动画 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
