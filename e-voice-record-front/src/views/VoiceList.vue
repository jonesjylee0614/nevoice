<template>
  <div class="voice-list-page">
    <!-- 顶部导航 -->
    <van-nav-bar title="声纹管理" class="top-nav" />

    <!-- 页面主体 -->
    <div class="page-body">
      <!-- 链接失效提示 -->
      <div class="invalid-card" v-if="!valid && !loading">
        <div class="invalid-icon-wrap">
          <van-icon name="warning-o" />
        </div>
        <h3>链接已失效</h3>
        <p>请从管理后台重新获取录音链接</p>
      </div>

      <!-- 正常内容 -->
      <template v-if="valid">
        <!-- 用户信息卡片 -->
        <div class="user-card" v-if="authStore.getUser">
          <div class="user-avatar">
            <van-icon name="user-o" />
          </div>
          <div class="user-info">
            <div class="user-name">{{ authStore.getUser.username || authStore.getUser.name || '用户' }}</div>
            <div class="user-id">用户ID: {{ authStore.getUser.userId }}</div>
          </div>
        </div>

        <!-- 录音记录区域 -->
        <div class="records-section">
          <div class="section-title">
            <span>我的声纹录音</span>
            <span class="record-count">{{ sentences.length }} 条</span>
          </div>

          <!-- 有记录时显示列表 -->
          <div class="records-list" v-if="sentences.length > 0">
            <div 
              v-for="(item, index) in sentences" 
              :key="item.id"
              class="record-item"
            >
              <div class="record-num">{{ index + 1 }}</div>
              <div class="record-content">
                <div class="record-text">{{ item.txt || '语音片段 ' + (index + 1) }}</div>
                <div class="record-time" v-if="item.create_time">{{ formatTime(item.create_time) }}</div>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div class="empty-state" v-else>
            <div class="empty-icon">
              <van-icon name="audio" />
            </div>
            <div class="empty-text">暂无录音记录</div>
            <div class="empty-hint">点击下方按钮开始录制</div>
          </div>
        </div>
      </template>
    </div>

    <!-- 底部操作栏 -->
    <div class="bottom-bar" v-if="valid">
      <button class="record-btn" @click="goToRecord()">
        <van-icon name="plus" />
        新增录音
      </button>
    </div>

    <!-- 加载状态 -->
    <div class="loading-mask" v-if="loading">
      <van-loading size="32px" vertical color="#4f46e5">验证中...</van-loading>
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
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

/* 顶部导航 */
.top-nav {
  background: #4f46e5 !important;
  flex-shrink: 0;
}

.top-nav :deep(.van-nav-bar__title) {
  color: #ffffff !important;
  font-weight: 600;
  font-size: 18px;
}

/* 页面主体 */
.page-body {
  flex: 1;
  padding: 16px;
  padding-bottom: 100px;
  max-width: 600px;
  margin: 0 auto;
  width: 100%;
}

/* 用户卡片 */
.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #ffffff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #ede9fe;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-avatar :deep(.van-icon) {
  font-size: 24px;
  color: #4f46e5;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 2px;
}

.user-id {
  font-size: 13px;
  color: #6b7280;
}

/* 链接失效提示 */
.invalid-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 60px 20px;
  background: #ffffff;
  border-radius: 12px;
  margin-top: 40px;
}

.invalid-icon-wrap {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #fef3c7;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.invalid-icon-wrap :deep(.van-icon) {
  font-size: 36px;
  color: #f59e0b;
}

.invalid-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.invalid-card p {
  font-size: 14px;
  color: #6b7280;
}

/* 录音记录区域 */
.records-section {
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #f3f4f6;
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
}

.record-count {
  font-size: 13px;
  font-weight: 500;
  color: #6b7280;
  background: #f3f4f6;
  padding: 4px 10px;
  border-radius: 12px;
}

/* 录音列表 */
.records-list {
  max-height: 400px;
  overflow-y: auto;
}

.record-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.2s;
}

.record-item:last-child {
  border-bottom: none;
}

.record-item:active {
  background: #f9fafb;
}

.record-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #ede9fe;
  color: #4f46e5;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.record-content {
  flex: 1;
  min-width: 0;
}

.record-text {
  font-size: 14px;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
}

.record-time {
  font-size: 12px;
  color: #9ca3af;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 20px;
}

.empty-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.empty-icon :deep(.van-icon) {
  font-size: 28px;
  color: #9ca3af;
}

.empty-text {
  font-size: 15px;
  font-weight: 500;
  color: #4b5563;
  margin-bottom: 4px;
}

.empty-hint {
  font-size: 13px;
  color: #9ca3af;
}

/* 底部操作栏 */
.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px 16px;
  padding-bottom: calc(12px + env(safe-area-inset-bottom, 0px));
  background: #ffffff;
  border-top: 1px solid #e5e7eb;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.record-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  height: 52px;
  border-radius: 12px;
  border: none;
  background: #4f46e5;
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.record-btn:active {
  background: #4338ca;
  transform: scale(0.98);
}

.record-btn :deep(.van-icon) {
  font-size: 20px;
}

/* 加载遮罩 */
.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
</style>
