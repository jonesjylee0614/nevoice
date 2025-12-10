<template>
  <div class="audio-upload-card">
    <div class="card-header">
      <div class="header-left">
        <van-icon name="music-o" />
        <span class="title">上传音频文件测试</span>
      </div>
      <van-tag :type="isStreaming || progress >= 1 ? 'success' : 'default'" size="medium">
        {{ isStreaming ? (progress >= 1 ? '处理中...' : '发送中...') : (progress >= 1 ? '已完成' : '就绪') }}
      </van-tag>
    </div>

    <!-- 文件拖放区 -->
    <div
      class="drop-zone"
      :class="{ dragover: isDragOver, 'has-file': audioBuffer }"
      @click="triggerFileInput"
      @dragover.prevent="isDragOver = true"
      @dragleave.prevent="isDragOver = false"
      @drop.prevent="handleDrop"
    >
      <div class="drop-icon">{{ audioBuffer ? '📄' : '📁' }}</div>
      <div class="drop-text">
        {{ audioBuffer ? fileName : '拖放音频文件到这里，或点击选择' }}
      </div>
      <div v-if="!audioBuffer" class="drop-hint">支持 WAV, MP3, M4A 等格式</div>
      <input 
        ref="fileInputRef" 
        type="file" 
        accept="audio/*" 
        style="display: none" 
        @change="handleFileSelect" 
      />
    </div>

    <!-- 文件信息 -->
    <div v-if="audioBuffer" class="file-info">
      <span>⏱️ {{ formatTime(fileDuration) }}</span>
      <span>📊 {{ fileSampleRate }} Hz</span>
      <span>📦 {{ (fileSize / 1024).toFixed(1) }} KB</span>
    </div>

    <!-- 进度条 -->
    <div v-if="isStreaming || progress > 0" class="progress-section">
      <van-progress 
        :percentage="Math.round(progress * 100)" 
        :show-pivot="false"
        stroke-width="8"
        color="linear-gradient(90deg, #6366f1, #8b5cf6)"
      />
      <div class="progress-text">
        {{ formatTime(currentTime) }} / {{ formatTime(fileDuration) }}
        ({{ Math.round(progress * 100) }}%)
      </div>
    </div>

    <!-- 控制按钮 -->
    <div class="controls">
      <van-button 
        type="success" 
        size="small"
        :disabled="!audioBuffer || isStreaming" 
        @click="startStreaming"
      >
        <van-icon name="play-circle-o" />
        <span>开始发送</span>
      </van-button>
      <van-button 
        type="danger" 
        size="small"
        plain
        :disabled="!isStreaming" 
        @click="stopStreaming"
      >
        <van-icon name="stop-circle-o" />
        <span>停止</span>
      </van-button>
      <van-button 
        size="small"
        plain
        :disabled="isStreaming" 
        @click="resetAll"
      >
        <van-icon name="replay" />
        <span>重置</span>
      </van-button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { showToast, showSuccessToast } from 'vant'
import type { MeetingDialog } from '@/api/types'
import { saveDialog } from '@/api/meeting'

const SAMPLE_RATE = 16000
const CHUNK_SIZE = 960 // 60ms @ 16kHz

const props = defineProps<{
  meetingId: number
  // WebSocket 地址，默认为开发环境
  wsHost?: string
}>()

const emit = defineEmits<{
  (e: 'dialog-received', dialog: Partial<MeetingDialog>): void
  (e: 'live-text-update', text: string): void
  (e: 'session-complete'): void
}>()

// WebSocket 配置 - 根据当前访问域名动态选择
const getWsHost = () => {
  if (props.wsHost) return props.wsHost
  
  // 根据当前页面 URL 判断环境
  const hostname = window.location.hostname
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    // 本地开发环境 - 直接连接 Python 后端
    return 'ws://localhost:8210'
  } else {
    // 外网环境 - 使用 Python API 域名
    return 'wss://pyapi.xnng.yfqwl.com'
  }
}

// 获取 Python HTTP 服务地址（用于音频文件等）
const getPyHttpHost = () => {
  const hostname = window.location.hostname
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8210'
  } else {
    return 'https://pyapi.xnng.yfqwl.com'
  }
}

// Refs
const fileInputRef = ref<HTMLInputElement | null>(null)

// 状态
const isDragOver = ref(false)
const audioBuffer = ref<AudioBuffer | null>(null)
const pcmData = ref<ArrayBuffer | null>(null)
const fileName = ref('')
const fileDuration = ref(0)
const fileSampleRate = ref(0)
const fileSize = ref(0)

// 流式状态
const isStreaming = ref(false)
const progress = ref(0)
const currentTime = ref(0)
const liveText = ref('')

// WebSocket 和定时器
let websocket: WebSocket | null = null
let streamingInterval: ReturnType<typeof setInterval> | null = null
let audioContext: AudioContext | null = null
let currentSeq = 0

// 工具函数
function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// 文件处理
function triggerFileInput() {
  fileInputRef.value?.click()
}

function handleDrop(e: DragEvent) {
  isDragOver.value = false
  const files = e.dataTransfer?.files
  if (files && files.length > 0 && files[0].type.startsWith('audio/')) {
    loadAudioFile(files[0])
  } else {
    showToast('请拖放音频文件')
  }
}

function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    loadAudioFile(file)
  }
}

async function loadAudioFile(file: File) {
  try {
    if (!audioContext) {
      audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    }

    const buffer = await file.arrayBuffer()
    const decoded = await audioContext.decodeAudioData(buffer.slice(0))
    audioBuffer.value = decoded
    pcmData.value = convertToPCM(decoded)

    fileName.value = file.name
    fileDuration.value = decoded.duration
    fileSampleRate.value = decoded.sampleRate
    fileSize.value = pcmData.value.byteLength

    showSuccessToast(`音频加载完成: ${decoded.duration.toFixed(2)}s`)
  } catch (e: any) {
    showToast(`加载失败: ${e.message}`)
  }
}

function convertToPCM(buffer: AudioBuffer): ArrayBuffer {
  let channelData = buffer.getChannelData(0)

  // 重采样到 16kHz
  if (buffer.sampleRate !== SAMPLE_RATE) {
    const ratio = SAMPLE_RATE / buffer.sampleRate
    const newLength = Math.floor(channelData.length * ratio)
    const resampled = new Float32Array(newLength)

    for (let i = 0; i < newLength; i++) {
      const srcIndex = i / ratio
      const srcIndexFloor = Math.floor(srcIndex)
      const srcIndexCeil = Math.min(srcIndexFloor + 1, channelData.length - 1)
      const t = srcIndex - srcIndexFloor
      resampled[i] = channelData[srcIndexFloor] * (1 - t) + channelData[srcIndexCeil] * t
    }
    channelData = resampled
  }

  // 转换为 Int16
  const pcm = new Int16Array(channelData.length)
  for (let i = 0; i < channelData.length; i++) {
    const s = Math.max(-1, Math.min(1, channelData[i]))
    pcm[i] = s < 0 ? s * 0x8000 : s * 0x7fff
  }

  return pcm.buffer
}

// WebSocket 流式发送
async function startStreaming() {
  if (!pcmData.value) {
    showToast('请先选择音频文件')
    return
  }

  if (isStreaming.value) return

  const wsUrl = `${getWsHost()}/ws/recognize`
  console.log('连接到:', wsUrl)

  try {
    websocket = new WebSocket(wsUrl)
    websocket.binaryType = 'arraybuffer'

    websocket.onopen = () => {
      console.log('WebSocket 连接成功')
      showSuccessToast('连接成功，开始发送音频')
      beginStreaming()
    }

    websocket.onmessage = event => {
      handleMessage(JSON.parse(event.data))
    }

    websocket.onerror = () => {
      showToast('WebSocket 连接错误')
    }

    websocket.onclose = () => {
      console.log('WebSocket 关闭')
      stopStreaming()
    }
  } catch (e: any) {
    showToast(`连接失败: ${e.message}`)
  }
}

function beginStreaming() {
  isStreaming.value = true
  liveText.value = ''

  // 发送配置
  const config = {
    chunk_size: [5, 10, 5],
    chunk_interval: 10,
    wav_name: `meeting_${props.meetingId}`,
    is_speaking: true,
    mode: '2pass',
    itn: true,
    sample_rate: SAMPLE_RATE
  }
  websocket?.send(JSON.stringify(config))

  // 开始流式发送
  const chunkBytes = CHUNK_SIZE * 2
  const intervalMs = (CHUNK_SIZE / SAMPLE_RATE) * 1000 // 60ms

  const pcmArray = new Uint8Array(pcmData.value!)
  const totalChunks = Math.ceil(pcmArray.length / chunkBytes)
  let currentChunk = 0

  console.log(`开始发送: ${totalChunks} 帧, 间隔 ${intervalMs.toFixed(1)}ms`)

  streamingInterval = setInterval(() => {
    if (!isStreaming.value || !websocket || websocket.readyState !== WebSocket.OPEN) {
      stopStreaming()
      return
    }

    if (currentChunk >= totalChunks) {
      // 发送停止信号，通知后端所有音频已发送完毕
      websocket.send(JSON.stringify({ is_speaking: false, mode: '2pass' }))
      console.log('发送完成，等待最终识别结果...')
      showToast('音频发送完成，等待最终识别结果...')

      if (streamingInterval) {
        clearInterval(streamingInterval)
        streamingInterval = null
      }

      // 兜底机制：等待后端处理完成
      // RTF=2.5 意味着处理 1 秒音频需要 2.5 秒
      // 动态计算超时时间：音频时长 * 3 + 30秒缓冲
      const estimatedProcessTime = Math.max(fileDuration.value * 3 + 30, 180) * 1000
      console.log(`[AudioUpload] 发送完成，等待后端处理，预计耗时: ${(estimatedProcessTime/1000).toFixed(0)}秒`)
      setTimeout(() => {
        if (websocket && websocket.readyState === WebSocket.OPEN) {
          console.log('[AudioUpload] 兜底关闭：超时未完成')
          websocket.close(1000, 'timeout')
        }
        if (isStreaming.value) {
          stopStreaming()
        }
      }, estimatedProcessTime)
      return
    }

    // 发送音频块
    const start = currentChunk * chunkBytes
    const end = Math.min(start + chunkBytes, pcmArray.length)
    const chunk = pcmArray.slice(start, end)

    websocket.send(chunk.buffer)
    currentChunk++

    // 更新进度
    progress.value = currentChunk / totalChunks
    currentTime.value = (currentChunk * CHUNK_SIZE) / SAMPLE_RATE
  }, intervalMs)
}

function stopStreaming() {
  isStreaming.value = false

  if (streamingInterval) {
    clearInterval(streamingInterval)
    streamingInterval = null
  }

  showToast('发送结束')
}

async function handleMessage(data: any) {
  // 处理会话完成信号
  if (data.type === 'session_complete') {
    console.log('[AudioUpload] 收到 session_complete 信号，处理已完成')
    showSuccessToast('音频处理完成')
    
    // 关闭 WebSocket 连接
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.close(1000, 'session_complete')
    }
    
    // 停止流式状态
    stopStreaming()
    
    // 通知父组件处理已完成
    emit('session-complete')
    return
  }
  
  const mode = data.mode || ''
  const text = data.text || ''
  const isFinal = data.is_final || false
  const startOffsetMs = data.start_offset_ms || 0
  const endOffsetMs = data.end_offset_ms || 0
  const durationMs = data.duration_ms || (endOffsetMs - startOffsetMs)  // 使用端点差值作为默认时长
  const audioPath = data.audio_path || ''
  const speakerInfo = data.speaker_info || null

  // 更新实时预览
  if (mode === '2pass-online' || mode === 'online') {
    liveText.value += text
    emit('live-text-update', liveText.value)
  } else if (mode === '2pass-offline' || mode === 'offline') {
    // 离线纠错结果 - 保存到会议记录
    liveText.value = ''
    emit('live-text-update', '')

    if (text) {
      currentSeq++
      
      // audioPath 是 Python 后端返回的相对路径，如 /data/meeting/audio_segments/xxx.wav
      // 前端显示时拼接完整 URL，保存到数据库时只存相对路径
      const fullAudioUrl = audioPath ? `${getPyHttpHost()}${audioPath}` : ''
      
      // 处理声纹匹配结果
      // recognized: 0-未识别, 1-声纹自动识别, 2-手动指定
      let speakerId: number | null = null
      let speakerName = '未知发言人'
      let speakerRole = ''
      let recognized = 0  // 默认未识别
      let recognitionNote = '等待声纹匹配'
      // let recognitionScore: number | undefined = undefined
      
      if (speakerInfo && speakerInfo.recognized) {
        speakerId = speakerInfo.speaker_id
        speakerName = speakerInfo.speaker_name || '未知'
        recognized = 1  // 声纹自动识别
        recognitionNote = speakerInfo.recognition_note || '声纹匹配成功'
        // recognitionScore = speakerInfo.recognition_score
      } else if (speakerInfo) {
        recognitionNote = speakerInfo.recognition_note || '声纹未匹配'
      }
      
      const dialog: Partial<MeetingDialog> = {
        meetingId: props.meetingId,
        seq: currentSeq,
        speakerId: speakerId || 0,
        speakerName,
        speakerRole,
        recognized,
        recognitionNote,
        speakTime: new Date().toISOString().replace('T', ' ').substring(0, 19),
        text,
        // 时间信息
        startOffset: startOffsetMs,
        endOffset: endOffsetMs,
        durationMs: durationMs,
        // 音频路径 - 前端显示用完整 URL
        audioPath: fullAudioUrl
      }

      // 通知父组件
      emit('dialog-received', dialog)

      // 保存到后端 - 只存相对路径，便于在不同环境下使用
      try {
        await saveDialog({
          meetingId: props.meetingId,
          seq: currentSeq,
          speakerId: speakerId || 0,
          speakerName,
          speakerRole,
          recognized,
          recognitionNote,
          text,
          startOffset: startOffsetMs,
          endOffset: endOffsetMs,
          durationMs: durationMs,
          audioPath: audioPath  // 只存相对路径，如 /data/meeting/audio_segments/xxx.wav
        } as any)
      } catch (e) {
        console.error('保存对话失败:', e)
      }
    }
    
    // 注意：isFinal 只表示某个语音段的最终结果，不是整个 session 的结束
    // 不在这里关闭连接，让超时机制来处理关闭
    // 这样可以确保后端有足够时间处理完所有数据
    if (isFinal) {
      console.log(`[AudioUpload] 收到 final 结果 (progress: ${(progress.value * 100).toFixed(1)}%)，继续等待更多结果...`)
    }
  }
}

function resetAll() {
  stopStreaming()
  if (websocket) {
    websocket.close()
    websocket = null
  }

  audioBuffer.value = null
  pcmData.value = null
  fileName.value = ''
  fileDuration.value = 0
  fileSampleRate.value = 0
  fileSize.value = 0
  progress.value = 0
  currentTime.value = 0
  liveText.value = ''
  currentSeq = 0

  showToast('已重置')
}

// 清理
onBeforeUnmount(() => {
  stopStreaming()
  if (websocket) {
    websocket.close()
  }
})
</script>

<style lang="scss" scoped>
.audio-upload-card {
  background: var(--surface);
  border-radius: 10px;
  padding: 10px 12px;
  border: 1px solid var(--border-light);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 6px;
    
    :deep(.van-icon) {
      font-size: 14px;
      color: var(--primary);
    }
    
    .title {
      font-size: 12px;
      font-weight: 600;
      color: var(--text-main);
    }
  }
  
  :deep(.van-tag) {
    font-size: 10px;
  }
}

.drop-zone {
  border: 1px dashed var(--border);
  border-radius: 8px;
  padding: 10px;
  text-align: center;
  background: var(--surface-muted);
  transition: all 0.3s ease;
  cursor: pointer;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover,
  &.dragover {
    border-color: var(--primary);
    background: rgba(99, 102, 241, 0.04);
  }

  &.has-file {
    border-color: var(--success);
    background: rgba(16, 185, 129, 0.04);
  }
}

.drop-icon {
  font-size: 1.2rem;
}

.drop-text {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
  flex: 1;
  text-align: left;
}

.drop-hint {
  font-size: 10px;
  color: var(--text-tertiary);
}

.file-info {
  display: flex;
  gap: 10px;
  font-size: 10px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  padding: 6px 8px;
  background: var(--surface-muted);
  border-radius: 6px;
}

.progress-section {
  margin-bottom: 8px;
}

.progress-text {
  font-size: 10px;
  color: var(--text-secondary);
  margin-top: 4px;
  text-align: center;
}

.controls {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
  
  .van-button {
    display: flex;
    align-items: center;
    gap: 2px;
    font-size: 11px;
    padding: 0 8px;
    height: 26px;
  }
}

</style>

