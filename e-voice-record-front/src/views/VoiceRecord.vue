<template>

  <van-nav-bar
      title="参照文档提交录音"
      left-text="返回"
      left-arrow
      @click-left="onClickLeft"
  />

  <div class="record-btn-box">
    <button
        :disabled="isParsing"
        :class="['record-btn', { recording: isRecording }]"
        @click="toggleRecording"
    >
      {{ isRecording ? '停止录音' : '开始录音' }}
    </button>
  </div>
  <div class="result-display">
    <h4>识别结果：</h4>
    <p>{{ recognitionResult }}</p>
  </div>
</template>

<script setup>
import {register} from "@/views/api/voice";
import {showFailToast, showLoadingToast} from 'vant';

const route = useRoute()
const currentSentence = ref('')
const isParsing = ref(false)
const isRecording = ref(false)
const recognitionResult = ref('')
const audioChunks = ref([])
const onClickLeft = () => {
  // 返回上一页
  history.back()
}
let mediaRecorder = null

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
        const stream = await navigator.mediaDevices.getUserMedia({audio: true})
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

    const audioBlob = new Blob(audioChunks.value, {type: mediaRecorder.mimeType})
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.wav')
    const t1 = showLoadingToast({
      message: '解析中...',
      forbidClick: true,
      loadingType: 'spinner',
    });
    try {
      const res = await register(formData)
      recognitionResult.value = res.data
    } catch (error) {
      console.error('音频上传失败:', error)
      showFailToast('音频上传失败');
    }
    // t1.close()
    audioChunks.value = []
    isParsing.value = false
  }
}

onMounted(() => {
  // 获取当前句子信息
  const sentenceId = route.params.idg
  // 这里应该调用API获取句子内容
  currentSentence.value = `示例句子${sentenceId}`
})

onUnmounted(() => {
  if (mediaRecorder) {
    mediaRecorder.stream.getTracks().forEach(track => track.stop())
  }
})
</script>

<style scoped>


.record-btn {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: none;
  background-color: #4CAF50;
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.record-btn-box {
  display: grid;
  place-items: center;
}

.record-btn.recording {
  background-color: #f44336;
  animation: pulse 1.5s infinite;
}

.result-display {
  margin-top: 30px;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}
</style> 