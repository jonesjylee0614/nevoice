<template>
  <div class="voice-record-page">
    <!-- 背景装饰 -->
    <div class="page-bg">
      <div class="bg-circle bg-circle-1"></div>
      <div class="bg-circle bg-circle-2"></div>
      <div class="bg-circle bg-circle-3"></div>
    </div>

    <!-- 顶部导航 -->
    <van-nav-bar
      title="声纹录制"
      left-text="返回"
      left-arrow
      class="glass-nav"
      @click-left="onClickLeft"
    />

    <!-- 页面内容 -->
    <div class="page-content">
      <!-- 提示卡片 -->
      <div class="tips-card">
        <div class="tips-icon">
          <van-icon name="volume-o" />
        </div>
        <div class="tips-content">
          <h3>录音提示</h3>
          <ul>
            <li>请在安静环境下进行录音</li>
            <li>保持麦克风距离约 20cm</li>
            <li>请清晰朗读提示文本</li>
            <li>每段录音时长建议 3-10 秒</li>
          </ul>
        </div>
      </div>

      <!-- 录音区域 -->
      <div class="record-section">
        <!-- 录音按钮 -->
        <div class="record-wrapper">
          <!-- 波纹效果 -->
          <div class="ripple-container" v-if="isRecording">
            <div class="ripple ripple-1"></div>
            <div class="ripple ripple-2"></div>
            <div class="ripple ripple-3"></div>
          </div>
          
          <button
            :disabled="isParsing"
            :class="['record-btn', { recording: isRecording, parsing: isParsing }]"
            @click="toggleRecording"
          >
            <div class="btn-content">
              <van-icon v-if="isParsing" name="loading" class="loading-icon" />
              <van-icon v-else-if="isRecording" name="pause-circle-o" />
              <van-icon v-else name="audio" />
            </div>
          </button>
        </div>

        <!-- 状态文字 -->
        <div class="record-status">
          <span v-if="isParsing" class="status-parsing">
            <van-icon name="loading" class="spin" />
            解析中，请稍候...
          </span>
          <span v-else-if="isRecording" class="status-recording">
            <span class="dot"></span>
            正在录音...
          </span>
          <span v-else class="status-idle">
            点击上方按钮开始录音
          </span>
        </div>

        <!-- 音频波形可视化 -->
        <div v-if="isRecording" class="wave-visualizer">
          <div v-for="i in 12" :key="i" class="wave-bar" :style="{ animationDelay: `${i * 0.1}s` }"></div>
        </div>
      </div>

      <!-- 识别结果 -->
      <div class="result-section" v-if="recognitionResult">
        <div class="result-header">
          <van-icon name="success" class="success-icon" />
          <span>识别结果</span>
        </div>
        <div class="result-content">
          {{ recognitionResult }}
        </div>
      </div>

      <!-- 用户信息 -->
      <div class="user-info" v-if="authStore.getUser">
        <van-icon name="user-circle-o" />
        <span>当前用户：{{ authStore.getUser.username || authStore.getUser.name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { saveUserPrint } from "@/views/api/voice";
import { showFailToast, showLoadingToast, closeToast, showSuccessToast } from 'vant';
import { useAuthStore } from "@/stores/auth.ts";

const route = useRoute()
const router = useRouter()

const isParsing = ref(false)
const isRecording = ref(false)
const recognitionResult = ref('')
const audioChunks = ref([])
const onClickLeft = () => {
  history.back()
}
let mediaRecorder = null

const authStore = useAuthStore()

// 开始/停止录音
const toggleRecording = async () => {
  if (!isRecording.value) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true
        }
      })
      mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/wav'
      })

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.value.push(event.data)
        }
      }

      mediaRecorder.start(10)
      isRecording.value = true
    } catch (err) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        mediaRecorder = new MediaRecorder(stream)
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunks.value.push(event.data)
          }
        }
        mediaRecorder.start(100)
        isRecording.value = true
      } catch (error) {
        console.error('录音失败:', error)
        showFailToast('无法访问麦克风');
      }
    }
  } else {
    isRecording.value = false
    isParsing.value = true
    mediaRecorder?.stop()
    mediaRecorder.stream.getTracks().forEach(track => track.stop())

    const audioBlob = new Blob(audioChunks.value, { type: mediaRecorder.mimeType })
    const formData = new FormData()
    formData.append('userId', authStore.getUser.userId);
    formData.append('userName', authStore.getUser.username);
    formData.append('audio', audioBlob, 'recording.wav')
    
    showLoadingToast({
      message: '上传解析中...',
      forbidClick: true,
      loadingType: 'spinner',
    });
    
    try {
      const res = await saveUserPrint(formData)
      recognitionResult.value = res.data?.data || res.data || '录制成功'
      closeToast()
      showSuccessToast('声纹录制成功')
    } catch (error) {
      console.error('音频上传失败:', error)
      closeToast()
      showFailToast('音频上传失败');
    }
    
    audioChunks.value = []
    isParsing.value = false
  }
}

onMounted(() => {
  let user = authStore.getUser
  if (!user || !user.userId) {
    router.push(`/voice-list`)
  }
})

onUnmounted(() => {
  if (mediaRecorder) {
    mediaRecorder.stream.getTracks().forEach(track => track.stop())
  }
})
</script>

<style scoped>
.voice-record-page {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
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
  bottom: 20%;
  left: -100px;
  opacity: 0.4;
}

.bg-circle-3 {
  width: 180px;
  height: 180px;
  background: linear-gradient(135deg, #fde68a 0%, #fbbf24 100%);
  top: 40%;
  right: 10%;
  opacity: 0.3;
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

/* 提示卡片 */
.tips-card {
  display: flex;
  gap: 16px;
  background: var(--surface);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-light);
  animation: fadeInUp 0.5s ease forwards;
}

.tips-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: var(--shadow-primary);
}

.tips-icon :deep(.van-icon) {
  font-size: 24px;
  color: white;
}

.tips-content h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 10px;
}

.tips-content ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tips-content li {
  font-size: 13px;
  color: var(--text-secondary);
  padding: 4px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tips-content li::before {
  content: '';
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--primary);
  flex-shrink: 0;
}

/* 录音区域 */
.record-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  animation: fadeInUp 0.5s ease 0.1s forwards;
  opacity: 0;
}

.record-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

/* 波纹效果 */
.ripple-container {
  position: absolute;
  width: 180px;
  height: 180px;
}

.ripple {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid var(--danger);
  opacity: 0;
  animation: ripple 2s infinite ease-out;
}

.ripple-2 {
  animation-delay: 0.5s;
}

.ripple-3 {
  animation-delay: 1s;
}

/* 录音按钮 */
.record-btn {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  color: white;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 10px 40px -10px rgba(16, 185, 129, 0.6);
  position: relative;
  z-index: 1;
}

.record-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 15px 50px -10px rgba(16, 185, 129, 0.7);
}

.record-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.record-btn.recording {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  box-shadow: 0 10px 40px -10px rgba(239, 68, 68, 0.6);
  animation: pulse 1.5s infinite;
}

.record-btn.recording:hover {
  box-shadow: 0 15px 50px -10px rgba(239, 68, 68, 0.7);
}

.record-btn.parsing {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  box-shadow: 0 10px 40px -10px rgba(99, 102, 241, 0.6);
  cursor: not-allowed;
}

.record-btn:disabled {
  opacity: 0.8;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-content :deep(.van-icon) {
  font-size: 48px;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

/* 状态文字 */
.record-status {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 20px;
}

.status-idle {
  color: var(--text-secondary);
}

.status-recording {
  color: var(--danger);
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-recording .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--danger);
  animation: pulse 1s infinite;
}

.status-parsing {
  color: var(--primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.spin {
  animation: spin 1s linear infinite;
}

/* 波形可视化 */
.wave-visualizer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  height: 60px;
  padding: 0 20px;
}

.wave-bar {
  width: 4px;
  height: 20%;
  background: var(--danger);
  border-radius: 2px;
  animation: wave 0.8s ease-in-out infinite;
}

/* 识别结果 */
.result-section {
  background: var(--surface);
  border-radius: 20px;
  padding: 20px;
  margin-top: 30px;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-light);
  animation: fadeInUp 0.5s ease forwards;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
  font-size: 15px;
  font-weight: 600;
  color: var(--success);
}

.success-icon {
  font-size: 20px;
}

.result-content {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-main);
  background: var(--success-light);
  padding: 16px;
  border-radius: 12px;
}

/* 用户信息 */
.user-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 40px;
  font-size: 13px;
  color: var(--text-tertiary);
}

.user-info :deep(.van-icon) {
  font-size: 18px;
}

/* 动画 */
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
}

@keyframes ripple {
  0% {
    transform: translate(-50%, -50%) scale(0.8);
    opacity: 0.8;
  }
  100% {
    transform: translate(-50%, -50%) scale(1.8);
    opacity: 0;
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes wave {
  0%, 100% {
    height: 20%;
  }
  50% {
    height: 100%;
  }
}

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
