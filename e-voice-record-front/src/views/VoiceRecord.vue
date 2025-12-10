<template>
  <div class="voice-record-page">
    <!-- 顶部导航 -->
    <van-nav-bar
      title="声纹录制"
      left-text="返回"
      left-arrow
      class="top-nav"
      @click-left="onClickLeft"
    />

    <!-- 页面主体 -->
    <div class="page-body">
      <!-- 提示卡片 -->
      <div class="tips-card">
        <div class="tips-title">
          <van-icon name="info-o" />
          录音提示
        </div>
        <ul class="tips-list">
          <li>请在安静环境下进行录音</li>
          <li>保持麦克风距离约 20cm</li>
          <li>请清晰朗读内容</li>
          <li>每段录音时长建议 3-10 秒</li>
        </ul>
      </div>

      <!-- 录音区域 -->
      <div class="record-area">
        <!-- 录音按钮 -->
        <div class="record-btn-wrapper">
          <button
            :disabled="isParsing"
            :class="['main-record-btn', { recording: isRecording, parsing: isParsing }]"
            @click="toggleRecording"
          >
            <van-icon v-if="isParsing" name="loading" class="spin-icon" />
            <van-icon v-else-if="isRecording" name="stop-circle-o" />
            <van-icon v-else name="audio" />
          </button>
          
          <!-- 录音中的动画圈 -->
          <div class="pulse-ring" v-if="isRecording"></div>
        </div>

        <!-- 状态文字 -->
        <div class="status-text">
          <template v-if="isParsing">
            <van-icon name="loading" class="spin-icon" />
            <span>上传解析中...</span>
          </template>
          <template v-else-if="isRecording">
            <span class="rec-dot"></span>
            <span>正在录音，再次点击停止</span>
          </template>
          <template v-else>
            <span>点击按钮开始录音</span>
          </template>
        </div>
      </div>

      <!-- 识别结果 -->
      <div class="result-card" v-if="recognitionResult">
        <div class="result-title">
          <van-icon name="passed" />
          录制成功
        </div>
        <div class="result-text">{{ recognitionResult }}</div>
      </div>

      <!-- 用户信息 -->
      <div class="user-tag" v-if="authStore.getUser">
        <van-icon name="user-o" />
        {{ authStore.getUser.username || authStore.getUser.name }}
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
        // 根据错误类型显示不同的提示
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
          showFailToast('麦克风权限被拒绝，请在浏览器设置中允许访问麦克风');
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
          showFailToast('未检测到麦克风设备');
        } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
          showFailToast('麦克风被其他程序占用');
        } else if (error.name === 'OverconstrainedError') {
          showFailToast('麦克风不支持所需的音频格式');
        } else if (error.name === 'SecurityError') {
          showFailToast('安全限制：请使用 HTTPS 或 localhost 访问');
        } else {
          showFailToast(`无法访问麦克风: ${error.message || error.name}`);
        }
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

.top-nav :deep(.van-nav-bar__left) {
  color: #ffffff !important;
}

.top-nav :deep(.van-nav-bar__text) {
  color: #ffffff !important;
}

/* 页面主体 */
.page-body {
  flex: 1;
  padding: 16px;
  max-width: 600px;
  margin: 0 auto;
  width: 100%;
}

/* 提示卡片 */
.tips-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.tips-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 12px;
}

.tips-title :deep(.van-icon) {
  color: #4f46e5;
  font-size: 18px;
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tips-list li {
  font-size: 13px;
  color: #4b5563;
  padding: 6px 0;
  padding-left: 16px;
  position: relative;
}

.tips-list li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #4f46e5;
  font-weight: bold;
}

/* 录音区域 */
.record-area {
  background: #ffffff;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.record-btn-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

/* 录音按钮 */
.main-record-btn {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: none;
  background: #10b981;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.main-record-btn :deep(.van-icon) {
  font-size: 40px;
}

.main-record-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.main-record-btn.recording {
  background: #ef4444;
}

.main-record-btn.parsing {
  background: #6b7280;
  cursor: not-allowed;
}

.main-record-btn:disabled {
  opacity: 0.7;
}

/* 录音中的脉冲圈 */
.pulse-ring {
  position: absolute;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 3px solid #ef4444;
  animation: pulse-ring 1.5s infinite;
  z-index: 1;
}

@keyframes pulse-ring {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.6);
    opacity: 0;
  }
}

/* 状态文字 */
.status-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  color: #4b5563;
}

.rec-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ef4444;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 识别结果 */
.result-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 16px;
  margin-top: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.result-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #10b981;
  margin-bottom: 12px;
}

.result-title :deep(.van-icon) {
  font-size: 20px;
}

.result-text {
  font-size: 14px;
  line-height: 1.6;
  color: #374151;
  background: #f0fdf4;
  padding: 12px;
  border-radius: 8px;
}

/* 用户标签 */
.user-tag {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 30px;
  font-size: 13px;
  color: #9ca3af;
}

.user-tag :deep(.van-icon) {
  font-size: 16px;
}
</style>
