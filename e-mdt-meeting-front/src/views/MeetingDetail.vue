<template>
  <div class="meeting-detail-page">
    <!-- 顶部导航栏 -->
    <header class="top-header">
      <div class="header-content">
        <div class="header-left">
          <button class="back-btn" @click="goBack">
            <van-icon name="arrow-left" />
            <span>返回列表</span>
          </button>
        </div>
        <div class="header-center">
          <h1 class="page-title">{{ meeting?.title || '会议详情' }}</h1>
        </div>
        <div class="header-right">
          <button 
            v-if="meeting?.status === 1" 
            class="end-btn"
            @click="handleEndMeeting"
          >
            <van-icon name="stop-circle-o" />
            <span>结束会议</span>
          </button>
          <div class="user-info" @click="showUserMenu = true">
            <div class="user-avatar">
              {{ userStore.userName.charAt(0) }}
            </div>
            <van-icon name="arrow-down" />
          </div>
        </div>
      </div>
    </header>

    <!-- 用户菜单弹窗 -->
    <van-popup v-model:show="showUserMenu" round position="center" class="user-menu-popup">
      <div class="user-menu-content">
        <div class="menu-header">
          <span>用户菜单</span>
          <van-icon name="cross" @click="showUserMenu = false" />
        </div>
        <div class="menu-list">
          <div 
            v-for="action in userMenuActions" 
            :key="action.name" 
            class="menu-item"
            :style="{ color: action.color }"
            @click="onUserMenuSelect(action); showUserMenu = false"
          >
            <van-icon :name="action.icon" />
            <span>{{ action.name }}</span>
          </div>
        </div>
      </div>
    </van-popup>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <van-loading size="40px" vertical>加载中...</van-loading>
    </div>

    <!-- 主内容区 -->
    <main class="main-content" v-else-if="meeting">
      <div class="content-grid">
        <!-- 左侧：会议信息 + 对话记录 -->
        <div class="left-panel">
          <!-- 会议信息卡片（包含录音控制） -->
          <div class="info-card">
            <!-- 顶部：状态和录音控制 -->
            <div class="card-top">
              <div class="status-area">
                <span class="status-badge" :class="statusClass(meeting.status)">
                  <span class="status-dot"></span>
                  {{ statusText(meeting.status) }}
                </span>
                <span class="meeting-id">#{{ meeting.id }}</span>
              </div>
              
              <!-- 录音控制 -->
              <div class="recording-area" v-if="meeting.status !== 2">
                <template v-if="!recording">
                  <button class="btn-record-mini" :disabled="connecting" @click="handleStartRecording">
                    <van-loading v-if="connecting" size="16px" color="#fff" />
                    <van-icon v-else name="play-circle-o" />
                    <span>{{ meeting.status === 0 ? '开始录音' : '继续录音' }}</span>
                  </button>
                  <!-- 上传音频测试按钮 -->
                  <button 
                    class="btn-upload-mini" 
                    @click="showAudioUpload = !showAudioUpload"
                  >
                    <van-icon :name="showAudioUpload ? 'arrow-up' : 'upgrade'" />
                    <span>{{ showAudioUpload ? '收起测试' : '上传测试' }}</span>
                  </button>
                </template>
                <template v-else>
                  <div class="recording-indicator">
                    <span class="rec-dot" :class="{ active: !paused }"></span>
                    <span class="rec-text">{{ paused ? '已暂停' : '录音中' }}</span>
                  </div>
                  <div class="recording-btns">
                    <button class="btn-mini" :class="{ warning: !paused }" @click="handleTogglePause">
                      <van-icon :name="paused ? 'play-circle-o' : 'pause-circle-o'" />
                    </button>
                    <button class="btn-mini danger" @click="handleStopRecording">
                      <van-icon name="stop-circle-o" />
                    </button>
                  </div>
                </template>
              </div>
              <div v-else class="completed-badge">
                <van-icon name="success" />
                <span>会议已结束</span>
              </div>
            </div>
            
            <!-- 会议信息 -->
            <div class="info-grid">
              <div class="info-item">
                <van-icon name="manager-o" />
                <span class="label">主持人</span>
                <span class="value">{{ meeting.hostName || '未指定' }}</span>
              </div>
              <div class="info-item">
                <van-icon name="clock-o" />
                <span class="label">时间</span>
                <span class="value">{{ formatTimeRange(meeting.startTime, meeting.endTime) }}</span>
              </div>
              <div class="info-item">
                <van-icon name="chat-o" />
                <span class="label">对话</span>
                <span class="value">{{ meeting.dialogCount || 0 }} 条</span>
              </div>
              <div class="info-item">
                <van-icon name="description" />
                <span class="label">总结</span>
                <span class="value" :class="summaryStatusClass(meeting.summaryStatus)">
                  {{ summaryStatusText(meeting.summaryStatus) }}
                </span>
              </div>
            </div>
            
            <!-- 标签和说明 -->
            <div class="info-extra" v-if="meeting.tagList?.length || meeting.description">
              <div v-if="meeting.tagList?.length" class="info-tags">
                <span v-for="tag in meeting.tagList" :key="tag" class="tag">{{ tag }}</span>
              </div>
              <div v-if="meeting.description" class="info-desc">
                <span class="desc-text">{{ meeting.description }}</span>
              </div>
            </div>
            
            <!-- 实时识别预览（录音时显示） -->
            <div v-if="recording || runningText" class="realtime-preview">
              <div class="preview-header">
                <span class="preview-dot" :class="{ active: recording && !paused }"></span>
                <span>{{ recording ? (paused ? '已暂停' : '正在识别...') : '识别预览' }}</span>
              </div>
              <div class="preview-text">{{ runningText }}</div>
            </div>
          </div>

          <!-- 音频文件上传测试 - 浮动在右下角 -->
          <Teleport to="body">
            <div 
              v-if="showAudioUpload && meeting?.status !== 2" 
              class="audio-upload-floating-wrapper"
            >
              <AudioFileUpload
                :meeting-id="meetingId"
                @dialog-received="handleFileDialogReceived"
                @live-text-update="handleLiveTextUpdate"
                @session-complete="handleSessionComplete"
              />
            </div>
          </Teleport>

          <!-- 实时识别预览 - 独立显示在对话记录上方 -->
          <div v-if="uploadLiveText" class="upload-live-preview-card">
            <div class="preview-header">
              <span class="preview-dot active"></span>
              <span>🎯 实时识别</span>
            </div>
            <div class="preview-content">{{ uploadLiveText }}</div>
          </div>

          <!-- 对话记录 -->
          <div class="dialogs-card">
            <div class="card-header">
              <h3>
                <van-icon name="chat-o" />
                对话记录
              </h3>
              <div class="header-actions">
                <span class="dialog-count">共 {{ meeting.dialogs?.length || 0 }} 条</span>
                <button 
                  v-if="meeting.dialogs?.length"
                  class="btn-copy-dialogs"
                  @click="copyAllDialogs"
                >
                  <van-icon name="description" />
                  复制全部
                </button>
              </div>
            </div>
            <div class="dialogs-list" v-if="meeting.dialogs?.length">
              <div 
                v-for="dialog in meeting.dialogs" 
                :key="dialog.id || dialog.seq" 
                class="dialog-item"
              >
                <!-- 右上角迷你音频播放器 -->
                <div v-if="dialog.audioPath" class="dialog-audio-mini">
                  <audio 
                    :ref="el => setAudioRef(dialog.id || dialog.seq, el as HTMLAudioElement)"
                    :src="getFullAudioUrl(dialog.audioPath)" 
                    preload="metadata"
                    @ended="() => audioPlaying[dialog.id || dialog.seq] = false"
                  />
                  <button 
                    class="audio-play-btn"
                    @click.stop="toggleAudio(dialog.id || dialog.seq)"
                  >
                    <van-icon :name="audioPlaying[dialog.id || dialog.seq] ? 'pause-circle-o' : 'play-circle-o'" />
                  </button>
                  <span class="audio-time">{{ formatAudioTime(audioDurations[dialog.id || dialog.seq]) }}</span>
                </div>
                
                <div class="dialog-meta">
                  <span class="dialog-time">{{ formatDialogTime(dialog) }}</span>
                  <span class="dialog-speaker" v-if="dialog.speakerName">
                    <van-icon name="user-o" />
                    {{ dialog.speakerName }}
                  </span>
                  <button 
                    v-else 
                    class="btn-assign"
                    @click="openAssignModal(dialog)"
                  >
                    <van-icon name="add-o" />
                    指定发言人
                  </button>
                  <span class="dialog-role" v-if="dialog.speakerRole">{{ dialog.speakerRole }}</span>
                </div>
                <div class="dialog-content" @click="startEditDialog(dialog)">
                  {{ dialog.text }}
                </div>
              </div>
            </div>
            <div v-else class="empty-dialogs">
              <van-icon name="chat-o" />
              <p>暂无对话记录</p>
              <span>开始录音后，识别结果将显示在这里</span>
            </div>
          </div>
        </div>

        <!-- 右侧：AI 总结 -->
        <div class="right-panel">
          <div class="summary-card">
            <div class="card-header">
              <h3>
                <van-icon name="magic-stick-o" />
                AI 智能总结
              </h3>
            </div>
            
            <div class="summary-actions">
              <button 
                class="btn-generate"
                :disabled="summaryLoading || meeting.summaryStatus === 1 || !meeting.dialogs?.length"
                @click="handleGenerateSummary"
              >
                <van-loading v-if="summaryLoading" size="18px" color="#fff" />
                <van-icon v-else name="magic-stick-o" />
                <span>{{ 
                  meeting.summaryStatus === 1 ? '正在生成...' : 
                  !meeting.dialogs?.length ? '暂无对话' : 
                  '一键生成总结' 
                }}</span>
              </button>
              <span class="summary-status">
                {{ !meeting.dialogs?.length ? '需要先录入对话' : summaryStatusText(meeting.summaryStatus) }}
              </span>
            </div>
            
            <div v-if="meeting.summary" class="summary-content">
              <pre>{{ meeting.summary }}</pre>
              <button class="btn-copy" @click="copySummary">
                <van-icon name="share-o" />
                复制总结
              </button>
            </div>
            <div v-else class="empty-summary">
              <div class="empty-icon">
                <van-icon name="description" />
              </div>
              <p>暂无总结</p>
              <span>点击上方按钮，AI 将自动分析对话内容并生成会议总结</span>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 指定发言人弹窗 -->
    <van-popup
      v-model:show="showAssignModal"
      round
      position="center"
      class="assign-popup"
    >
      <div class="assign-modal">
        <div class="modal-header">
          <h3>指定发言人</h3>
          <van-icon name="cross" @click="showAssignModal = false" />
        </div>
        <van-search
          v-model="staffKeyword"
          placeholder="搜索姓名或科室"
          shape="round"
        />
        <div class="staff-list">
          <div 
            v-for="staff in filteredStaffList" 
            :key="staff.userId"
            class="staff-item"
            :class="{ active: selectedStaff?.userId === staff.userId }"
            @click="selectStaff(staff)"
          >
            <div class="staff-avatar">{{ staff.userName.charAt(0) }}</div>
            <div class="staff-info">
              <strong>{{ staff.userName }}</strong>
              <span>{{ staff.role }} · {{ staff.department }}</span>
            </div>
            <van-icon v-if="selectedStaff?.userId === staff.userId" name="success" class="check-icon" />
          </div>
          <div v-if="!filteredStaffList.length" class="empty-staff">
            <van-icon name="search" />
            <p>未找到匹配人员</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showAssignModal = false">取消</button>
          <button class="btn-confirm" :disabled="!selectedStaff" @click="confirmAssign">确认</button>
        </div>
      </div>
    </van-popup>

    <!-- 编辑对话文本弹窗 -->
    <van-popup
      v-model:show="showEditDialog"
      round
      position="center"
      class="edit-popup"
    >
      <div class="edit-modal">
        <div class="modal-header">
          <h3>编辑识别文本</h3>
          <van-icon name="cross" @click="showEditDialog = false" />
        </div>
        <textarea
          v-model="editingText"
          placeholder="请输入识别文本"
          class="edit-textarea"
          rows="6"
        ></textarea>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showEditDialog = false">取消</button>
          <button class="btn-confirm" @click="handleEditConfirm">保存</button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { showSuccessToast, showToast, showConfirmDialog } from 'vant'
import { onBeforeRouteLeave } from 'vue-router'
import type { MeetingDetail, MeetingDialog, Participant, MeetingStatus, SummaryStatus } from '@/api/types'
import { 
  getDetail, 
  startMeeting, 
  endMeeting, 
  generateSummary, 
  assignSpeaker, 
  updateDialogText,
  getStaffList,
  saveDialog
} from '@/api/meeting'
import { useMeetingStore } from '@/stores/meeting'
import { useUserStore } from '@/stores/user'
import AudioFileUpload from '@/components/AudioFileUpload.vue'

const route = useRoute()
const router = useRouter()
const meetingStore = useMeetingStore()
const userStore = useUserStore()

// 用户菜单
const showUserMenu = ref(false)
const userMenuActions = [
  { name: '返回首页', icon: 'wap-home-o' },
  { name: '退出登录', icon: 'revoke', color: '#ee0a24' }
]

// 用户菜单选择
const onUserMenuSelect = async (action: { name: string }) => {
  if (action.name === '返回首页') {
    router.push('/')
  } else if (action.name === '退出登录') {
    try {
      await showConfirmDialog({
        title: '退出登录',
        message: '确定要退出登录吗？'
      })
      await userStore.logout()
      router.replace('/login')
    } catch {
      // 用户取消
    }
  }
}

// 会议ID
const meetingId = computed(() => Number(route.params.id) || 0)

// 状态
const loading = ref(true)
const meeting = ref<MeetingDetail | null>(null)
const summaryLoading = ref(false)

// 录音相关状态
const recording = ref(false)
const connecting = ref(false)
const paused = ref(false)
const runningText = ref('')

// WebSocket 实时录音相关
const SAMPLE_RATE = 16000
const CHUNK_SIZE = 960 // 60ms @ 16kHz
let websocket: WebSocket | null = null
let audioContext: AudioContext | null = null
let audioWorkletNode: AudioWorkletNode | null = null
let scriptProcessorNode: ScriptProcessorNode | null = null
let currentSeq = 0
let currentSegmentId = '' // 用于跟踪当前语音段，避免预览重叠

// 获取 WebSocket 地址
const getWsHost = () => {
  const hostname = window.location.hostname
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'ws://localhost:8210'
  } else {
    return 'wss://pyapi.xnng.yfqwl.com'
  }
}

// 音频上传测试
const showAudioUpload = ref(false)

// 迷你音频播放器状态
const audioRefs = ref<Record<string | number, HTMLAudioElement | null>>({})
const audioPlaying = ref<Record<string | number, boolean>>({})
const audioDurations = ref<Record<string | number, number>>({})

// 获取 Python HTTP 服务地址（用于音频文件）
const getPyHttpHost = () => {
  const hostname = window.location.hostname
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8210'
  } else {
    return 'https://pyapi.xnng.yfqwl.com'
  }
}

// 获取完整的音频 URL
const getFullAudioUrl = (audioPath: string | undefined): string => {
  if (!audioPath) return ''
  // 如果已经是完整 URL（兼容旧数据）
  if (audioPath.startsWith('http://') || audioPath.startsWith('https://')) {
    // 替换旧的 localhost URL 为新的域名
    if (audioPath.includes('localhost:8210')) {
      return audioPath.replace('http://localhost:8210', getPyHttpHost())
    }
    return audioPath
  }
  // 相对路径，拼接完整 URL
  return `${getPyHttpHost()}${audioPath}`
}

function setAudioRef(id: string | number, el: HTMLAudioElement | null) {
  if (el) {
    audioRefs.value[id] = el
    // 监听音频元数据加载完成，获取总时长
    el.addEventListener('loadedmetadata', () => {
      audioDurations.value[id] = el.duration
    })
    // 如果已经加载过了
    if (el.duration) {
      audioDurations.value[id] = el.duration
    }
  }
}

function toggleAudio(id: string | number) {
  const audio = audioRefs.value[id]
  if (!audio) return
  
  // 暂停其他正在播放的音频
  Object.entries(audioRefs.value).forEach(([key, el]) => {
    if (key !== String(id) && el && !el.paused) {
      el.pause()
      audioPlaying.value[key] = false
    }
  })
  
  if (audio.paused) {
    audio.play()
    audioPlaying.value[id] = true
  } else {
    audio.pause()
    audioPlaying.value[id] = false
  }
}

function formatAudioTime(seconds: number): string {
  if (!seconds || isNaN(seconds)) return '--:--'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
const uploadLiveText = ref('')

// 处理实时识别文本更新
function handleLiveTextUpdate(text: string) {
  uploadLiveText.value = text
}

// 指定发言人相关
const showAssignModal = ref(false)
const currentDialog = ref<MeetingDialog | null>(null)
const staffKeyword = ref('')
const staffList = ref<Participant[]>([])
const selectedStaff = ref<Participant | null>(null)

// 编辑对话相关
const showEditDialog = ref(false)
const editingDialog = ref<MeetingDialog | null>(null)
const editingText = ref('')

// 过滤人员列表
const filteredStaffList = computed(() => {
  const keyword = staffKeyword.value.toLowerCase()
  if (!keyword) return staffList.value
  return staffList.value.filter(s =>
    s.userName.toLowerCase().includes(keyword) ||
    s.department.toLowerCase().includes(keyword) ||
    s.role.toLowerCase().includes(keyword)
  )
})

// 获取会议详情
const fetchDetail = async () => {
  loading.value = true
  try {
    const { data } = await getDetail(meetingId.value)
    meeting.value = data.data
    meetingStore.setCurrentMeeting(data.data)
  } catch (error) {
    console.error('获取会议详情失败:', error)
    showToast('获取会议详情失败')
  } finally {
    loading.value = false
  }
}

// 获取人员列表
const fetchStaffList = async () => {
  try {
    const { data } = await getStaffList()
    staffList.value = data.data || []
  } catch (error) {
    // 使用模拟数据
    staffList.value = [
      { userId: 1, userName: '张主任', department: '呼吸与危重症医学科', role: '科室主任' },
      { userId: 2, userName: '王专家', department: '影像科', role: '主任医师' },
      { userId: 3, userName: '刘医生', department: '重症医学科', role: '主治医师' },
      { userId: 4, userName: '李护士长', department: '呼吸治疗护理组', role: '护理组长' },
      { userId: 5, userName: '陈教授', department: '胸外科', role: '特聘教授' }
    ]
  }
}

// 麦克风权限和媒体流
let mediaStream: MediaStream | null = null

// 请求麦克风权限
const requestMicrophonePermission = async (): Promise<boolean> => {
  try {
    // 请求麦克风权限
    mediaStream = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      } 
    })
    return true
  } catch (error: any) {
    console.error('麦克风权限请求失败:', error)
    if (error.name === 'NotAllowedError') {
      showToast('请允许使用麦克风')
    } else if (error.name === 'NotFoundError') {
      showToast('未检测到麦克风设备')
    } else {
      showToast('无法访问麦克风')
    }
    return false
  }
}

// 开始录音
const handleStartRecording = async () => {
  if (!meeting.value) return
  
  connecting.value = true
  
  try {
    // 请求麦克风权限
    const hasPermission = await requestMicrophonePermission()
    if (!hasPermission) {
      connecting.value = false
      return
    }
    
    // 如果会议状态是待开始，先开始会议
    if (meeting.value.status === 0) {
      await startMeeting(meetingId.value)
      meeting.value.status = 1
      showSuccessToast('会议已开始')
    }
    
    // 建立 WebSocket 连接
    const wsUrl = `${getWsHost()}/ws/recognize`
    console.log('[Recording] 连接到:', wsUrl)
    
    websocket = new WebSocket(wsUrl)
    websocket.binaryType = 'arraybuffer'
    
    websocket.onopen = () => {
      console.log('[Recording] WebSocket 连接成功')
      // 发送配置
      const config = {
        chunk_size: [5, 10, 5],
        chunk_interval: 10,
        wav_name: `meeting_realtime_${meetingId.value}`,
        is_speaking: true,
        mode: '2pass',
        itn: true,
        sample_rate: SAMPLE_RATE
      }
      websocket?.send(JSON.stringify(config))
      
      // 开始捕获音频
      startAudioCapture()
      
      recording.value = true
      showSuccessToast('录音已开始')
      connecting.value = false
    }
    
    websocket.onmessage = event => {
      handleRecognitionMessage(JSON.parse(event.data))
    }
    
    websocket.onerror = (error) => {
      console.error('[Recording] WebSocket 错误:', error)
      showToast('WebSocket 连接错误')
      handleStopRecording()
    }
    
    websocket.onclose = () => {
      console.log('[Recording] WebSocket 关闭')
      if (recording.value) {
        handleStopRecording()
      }
    }
  } catch (error) {
    console.error('开始录音失败:', error)
    showToast('开始录音失败')
    connecting.value = false
  }
}

// 开始音频捕获
const startAudioCapture = async () => {
  if (!mediaStream) return
  
  try {
    // 创建 AudioContext - 不指定采样率，让浏览器使用默认值
    audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    console.log('[Recording] AudioContext 采样率:', audioContext.sampleRate)
    
    const source = audioContext.createMediaStreamSource(mediaStream)
    
    // 添加增益节点放大音频信号
    const gainNode = audioContext.createGain()
    gainNode.gain.value = 5.0 // 放大 5 倍（提高灵敏度）
    
    // 使用 ScriptProcessorNode（兼容性更好）
    const bufferSize = 4096
    scriptProcessorNode = audioContext.createScriptProcessor(bufferSize, 1, 1)
    
    // 连接：source -> gainNode -> scriptProcessor -> destination
    source.connect(gainNode)
    gainNode.connect(scriptProcessorNode)
    
    // 用于累积音频数据
    let audioBuffer: Float32Array[] = []
    let samplesCount = 0
    const samplesPerChunk = CHUNK_SIZE // 60ms @ 16kHz = 960 samples
    let chunksSent = 0
    
    // 客户端 VAD 参数
    const VAD_THRESHOLD = 0.01 // 音量阈值（降低，更敏感）
    const SILENCE_TIMEOUT = 2000 // 静音超时（毫秒），增加到 2 秒
    let isSpeaking = false // 是否正在说话
    let silenceStart = 0 // 静音开始时间
    let speechStartSent = false // 是否已发送过语音开始的数据
    let lastSendTime = Date.now() // 上次发送时间
    
    scriptProcessorNode.onaudioprocess = (event) => {
      if (!recording.value || paused.value || !websocket || websocket.readyState !== WebSocket.OPEN) {
        return
      }
      
      const inputData = event.inputBuffer.getChannelData(0)
      
      // 计算当前块的 RMS 音量
      let sumSquares = 0
      for (let i = 0; i < inputData.length; i++) {
        sumSquares += inputData[i] * inputData[i]
      }
      const rms = Math.sqrt(sumSquares / inputData.length)
      
      // 客户端 VAD：检测是否在说话
      const now = Date.now()
      if (rms > VAD_THRESHOLD) {
        // 检测到语音
        if (!isSpeaking) {
          console.log(`[Recording] 语音开始，RMS: ${rms.toFixed(4)}`)
        }
        isSpeaking = true
        silenceStart = 0
        speechStartSent = true
      } else {
        // 静音
        if (isSpeaking) {
          if (silenceStart === 0) {
            silenceStart = now
          } else if (now - silenceStart > SILENCE_TIMEOUT) {
            // 静音超时，停止发送
            isSpeaking = false
            speechStartSent = false
            console.log(`[Recording] 静音超时，暂停发送`)
          }
        }
      }
      
      // 客户端 VAD：只在说话时发送音频
      // speechStartSent 保证语音开始后的短暂静音也会发送
      // lastSendTime 保证即使长时间静音，也间隔发送一些数据保持连接
      const shouldSend = isSpeaking || speechStartSent || (now - lastSendTime > 5000) // 最多 5 秒发送一次心跳
      if (!shouldSend) {
        return // 不发送静音数据，减少后端积压
      }
      
      // 调试日志
      if (chunksSent % 50 === 0) {
        console.log(`[Recording] chunk#${chunksSent} RMS: ${rms.toFixed(4)}, 说话中: ${isSpeaking}`)
      }
      lastSendTime = now
      
      // 重采样到 16kHz（如果需要）
      let resampled = inputData
      if (audioContext!.sampleRate !== SAMPLE_RATE) {
        const ratio = SAMPLE_RATE / audioContext!.sampleRate
        const newLength = Math.floor(inputData.length * ratio)
        resampled = new Float32Array(newLength)
        for (let i = 0; i < newLength; i++) {
          const srcIndex = i / ratio
          const srcIndexFloor = Math.floor(srcIndex)
          const srcIndexCeil = Math.min(srcIndexFloor + 1, inputData.length - 1)
          const t = srcIndex - srcIndexFloor
          resampled[i] = inputData[srcIndexFloor] * (1 - t) + inputData[srcIndexCeil] * t
        }
      }
      
      // 累积数据
      audioBuffer.push(new Float32Array(resampled))
      samplesCount += resampled.length
      
      // 当累积足够数据时发送
      while (samplesCount >= samplesPerChunk) {
        // 合并缓冲区
        const totalBuffer = new Float32Array(samplesCount)
        let offset = 0
        for (const buf of audioBuffer) {
          totalBuffer.set(buf, offset)
          offset += buf.length
        }
        
        // 提取一个 chunk
        const chunk = totalBuffer.slice(0, samplesPerChunk)
        
        // 转换为 Int16 PCM
        const pcm = new Int16Array(samplesPerChunk)
        for (let i = 0; i < samplesPerChunk; i++) {
          const s = Math.max(-1, Math.min(1, chunk[i]))
          pcm[i] = s < 0 ? s * 0x8000 : s * 0x7fff
        }
        
        // 发送到 WebSocket
        websocket?.send(pcm.buffer)
        chunksSent++
        
        // 保留剩余数据
        const remaining = totalBuffer.slice(samplesPerChunk)
        audioBuffer = remaining.length > 0 ? [remaining] : []
        samplesCount = remaining.length
      }
    }
    
    // 连接到目标（否则音频处理不会触发）
    scriptProcessorNode.connect(audioContext.destination)
    
    console.log('[Recording] 音频捕获已启动, 目标采样率:', SAMPLE_RATE, ', 增益:', gainNode.gain.value)
  } catch (error) {
    console.error('[Recording] 启动音频捕获失败:', error)
    showToast('音频捕获失败')
    handleStopRecording()
  }
}

// 处理识别消息
const handleRecognitionMessage = async (data: any) => {
  console.log('[Recording] 收到消息:', JSON.stringify(data).substring(0, 200))
  
  // 处理会话完成信号
  if (data.type === 'session_complete') {
    console.log('[Recording] 收到 session_complete 信号')
    return
  }
  
  const mode = data.mode || ''
  const text = data.text || ''
  const startOffsetMs = data.start_offset_ms || 0
  const endOffsetMs = data.end_offset_ms || 0
  const durationMs = data.duration_ms || (endOffsetMs - startOffsetMs)
  const audioPath = data.audio_path || ''
  const speakerInfo = data.speaker_info || null
  const segmentId = data.segment_id || '' // 语音段 ID
  
  // 处理实时预览（online 模式）
  if (mode === '2pass-online' || mode === 'online') {
    // 检查是否是新的语音段，如果是则清空预览
    if (segmentId && segmentId !== currentSegmentId) {
      console.log('[Recording] 新语音段开始:', segmentId, '清空预览')
      runningText.value = ''
      currentSegmentId = segmentId
    }
    console.log('[Recording] online 结果:', text)
    runningText.value += text
  } 
  // 处理最终结果（offline 模式）
  else if (mode === '2pass-offline' || mode === 'offline') {
    // 清空实时预览
    runningText.value = ''
    // 重置 segment ID，准备接收下一个语音段
    currentSegmentId = ''
    
    if (text) {
      currentSeq++
      
      // 处理声纹匹配结果
      let speakerId: number | null = null
      let speakerName = '未知发言人'
      let speakerRole = ''
      let recognized = 0
      let recognitionNote = '等待声纹匹配'
      
      if (speakerInfo && speakerInfo.recognized) {
        speakerId = speakerInfo.speaker_id
        speakerName = speakerInfo.speaker_name || '未知'
        recognized = 1
        recognitionNote = speakerInfo.recognition_note || '声纹匹配成功'
      } else if (speakerInfo) {
        recognitionNote = speakerInfo.recognition_note || '声纹未匹配'
      }
      
      // 构建完整的音频 URL
      const fullAudioUrl = audioPath ? `${getPyHttpHost()}${audioPath}` : ''
      
      const dialog: MeetingDialog = {
        id: 0, // 临时 ID，保存后会更新
        seq: currentSeq,
        speakerId: speakerId || 0,
        speakerName,
        speakerRole,
        recognized,
        recognitionNote,
        speakTime: new Date().toISOString().replace('T', ' ').substring(0, 19),
        text,
        startOffset: startOffsetMs,
        endOffset: endOffsetMs,
        durationMs: durationMs,
        audioPath: fullAudioUrl
      }
      
      // 添加到本地对话列表
      if (meeting.value) {
        meeting.value.dialogs = [...(meeting.value.dialogs || []), dialog]
        meeting.value.dialogCount = meeting.value.dialogs.length
      }
      
      // 保存到后端
      try {
        await saveDialog({
          meetingId: meetingId.value,
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
          audioPath: audioPath // 只存相对路径
        } as any)
      } catch (e) {
        console.error('[Recording] 保存对话失败:', e)
      }
    }
  }
}

// 停止录音
const handleStopRecording = () => {
  // 发送停止信号
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    websocket.send(JSON.stringify({ is_speaking: false, mode: '2pass' }))
    console.log('[Recording] 发送停止信号')
    // 延迟关闭 WebSocket，等待最后的识别结果
    setTimeout(() => {
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.close(1000, 'stop_recording')
      }
      websocket = null
    }, 3000)
  }
  
  // 停止音频处理节点
  if (scriptProcessorNode) {
    scriptProcessorNode.disconnect()
    scriptProcessorNode = null
  }
  if (audioWorkletNode) {
    audioWorkletNode.disconnect()
    audioWorkletNode = null
  }
  if (audioContext) {
    audioContext.close()
    audioContext = null
  }
  
  // 释放媒体流资源
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }
  
  recording.value = false
  paused.value = false
  runningText.value = ''
  connecting.value = false
  currentSegmentId = '' // 重置语音段 ID
  showSuccessToast('录音已停止')
}

// 处理音频文件上传测试的对话回调
const handleFileDialogReceived = async (dialog: Partial<MeetingDialog>) => {
  // 如果会议状态是待开始，先开始会议
  if (meeting.value?.status === 0) {
    try {
      await startMeeting(meetingId.value)
      if (meeting.value) {
        meeting.value.status = 1
      }
      showSuccessToast('会议已开始')
    } catch (error) {
      console.error('开始会议失败:', error)
    }
  }
  
  // 将识别结果添加到对话列表
  if (meeting.value) {
    meeting.value.dialogs = [...(meeting.value.dialogs || []), dialog as MeetingDialog]
    meeting.value.dialogCount = meeting.value.dialogs.length
  }
}

// 处理音频处理完成
const handleSessionComplete = () => {
  // 更新会议结束时间为当前时间
  if (meeting.value) {
    const now = new Date().toISOString().replace('T', ' ').substring(0, 19)
    meeting.value.endTime = now
  }
  console.log('[MeetingDetail] 音频处理完成，已更新结束时间')
}

// 暂停/恢复录音
const handleTogglePause = () => {
  paused.value = !paused.value
}

// 结束会议
const handleEndMeeting = async () => {
  try {
    await showConfirmDialog({
      title: '结束会议',
      message: '确定要结束会议吗？结束后将无法继续录音。'
    })
    
    if (recording.value) {
      handleStopRecording()
    }
    
    await endMeeting(meetingId.value)
    if (meeting.value) {
      meeting.value.status = 2
    }
    showSuccessToast('会议已结束')
  } catch {
    // 用户取消
  }
}

// 生成AI总结
const handleGenerateSummary = async () => {
  if (!meeting.value) return
  
  // 检查是否有对话记录
  if (!meeting.value.dialogs || meeting.value.dialogs.length === 0) {
    showToast('暂无对话记录，无法生成总结')
    return
  }
  
  summaryLoading.value = true
  try {
    await generateSummary(meetingId.value)
    if (meeting.value) {
      meeting.value.summaryStatus = 1
    }
    showToast('正在生成总结，请稍后刷新')
    
    // 轮询检查状态
    pollSummaryStatus()
  } catch (error) {
    console.error('生成总结失败:', error)
    showToast('生成总结失败')
  } finally {
    summaryLoading.value = false
  }
}

// 轮询总结状态
const pollSummaryStatus = () => {
  const timer = setInterval(async () => {
    await fetchDetail()
    if (meeting.value?.summaryStatus !== 1) {
      clearInterval(timer)
      if (meeting.value?.summaryStatus === 2) {
        showSuccessToast('总结生成完成')
      }
    }
  }, 3000)
}

// 复制总结
const copySummary = () => {
  if (!meeting.value?.summary) return
  navigator.clipboard.writeText(meeting.value.summary)
  showSuccessToast('已复制到剪贴板')
}

// 复制所有对话记录
const copyAllDialogs = () => {
  if (!meeting.value?.dialogs?.length) {
    showToast('暂无对话记录')
    return
  }
  
  const dialogText = meeting.value.dialogs.map((dialog, index) => {
    const time = formatDialogTime(dialog)
    const speaker = dialog.speakerName || '未知发言人'
    return `[${time}] ${speaker}\n${dialog.text}`
  }).join('\n\n')
  
  navigator.clipboard.writeText(dialogText)
  showSuccessToast('对话记录已复制到剪贴板')
}

// 打开指定发言人弹窗
const openAssignModal = (dialog: MeetingDialog) => {
  if (!dialog.id) {
    showToast('对话记录尚未保存')
    return
  }
  currentDialog.value = dialog
  selectedStaff.value = null
  staffKeyword.value = ''
  showAssignModal.value = true
}

// 选择人员
const selectStaff = (staff: Participant) => {
  selectedStaff.value = staff
}

// 确认指定发言人
const confirmAssign = async () => {
  if (!currentDialog.value || !selectedStaff.value) return
  
  try {
    await assignSpeaker({
      dialogId: currentDialog.value.id,
      speakerId: selectedStaff.value.userId,
      speakerName: selectedStaff.value.userName,
      speakerRole: `${selectedStaff.value.department} · ${selectedStaff.value.role}`
    })
    
    // 更新本地数据
    currentDialog.value.speakerName = selectedStaff.value.userName
    currentDialog.value.speakerRole = `${selectedStaff.value.department} · ${selectedStaff.value.role}`
    currentDialog.value.recognized = 2  // 2-手动指定
    
    showAssignModal.value = false
    showSuccessToast('指定成功')
  } catch (error) {
    console.error('指定发言人失败:', error)
    showToast('指定失败')
  }
}

// 开始编辑对话
const startEditDialog = (dialog: MeetingDialog) => {
  if (!dialog.id) {
    showToast('对话记录尚未保存')
    return
  }
  editingDialog.value = dialog
  editingText.value = dialog.text
  showEditDialog.value = true
}

// 确认编辑
const handleEditConfirm = async () => {
  if (!editingDialog.value) return
  
  if (!editingText.value.trim()) {
    showToast('文本不能为空')
    return
  }
  
  try {
    await updateDialogText(editingDialog.value.id, editingText.value.trim())
    editingDialog.value.text = editingText.value.trim()
    showEditDialog.value = false
    showSuccessToast('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    showToast('保存失败')
  }
}

// 格式化时间范围
const formatTimeRange = (start: string, end: string) => {
  if (!start) return '时间待定'
  const startDate = new Date(start)
  const dateStr = startDate.toLocaleDateString('zh-CN')
  const startTime = startDate.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  
  if (!end) return `${dateStr} ${startTime} - 待定`
  
  const endDate = new Date(end)
  const endTime = endDate.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  return `${dateStr} ${startTime} - ${endTime}`
}

// 格式化对话时间
const formatDialogTime = (dialog: MeetingDialog) => {
  if (dialog.startOffset !== undefined && dialog.startOffset !== null) {
    const start = formatOffsetTime(dialog.startOffset)
    const end = formatOffsetTime(dialog.endOffset)
    return `${start} - ${end}`
  }
  return dialog.speakTime ? dialog.speakTime.split(' ')[1] || dialog.speakTime : '-'
}

// 格式化时间偏移
const formatOffsetTime = (offsetMs: number | undefined) => {
  if (!offsetMs && offsetMs !== 0) return '--:--'
  const totalSeconds = Math.floor(offsetMs / 1000)
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}

// 状态文本
const statusText = (status: MeetingStatus) => {
  const map: Record<number, string> = {
    0: '待开始',
    1: '进行中',
    2: '已结束'
  }
  return map[status] || '未知'
}

// 状态样式类
const statusClass = (status: MeetingStatus) => {
  const map: Record<number, string> = {
    0: 'status-pending',
    1: 'status-running',
    2: 'status-completed'
  }
  return map[status] || ''
}

// 总结状态文本
const summaryStatusText = (status: SummaryStatus) => {
  const map: Record<number, string> = {
    0: '未生成',
    1: '生成中...',
    2: '已完成'
  }
  return map[status] || '未知'
}

// 总结状态样式
const summaryStatusClass = (status: SummaryStatus) => {
  const map: Record<number, string> = {
    0: 'text-muted',
    1: 'text-warning',
    2: 'text-success'
  }
  return map[status] || ''
}

// 返回（录音中需要确认）
const goBack = async () => {
  if (recording.value) {
    try {
      await showConfirmDialog({
        title: '正在录音中',
        message: '当前正在录音，离开页面将停止录音。确定要离开吗？',
        confirmButtonText: '停止并离开',
        confirmButtonColor: '#ee0a24'
      })
      // 用户确认，停止录音
      handleStopRecording()
      router.back()
    } catch {
      // 用户取消
    }
  } else {
    router.back()
  }
}

// 页面刷新/关闭保护
const handleBeforeUnload = (e: BeforeUnloadEvent) => {
  if (recording.value) {
    e.preventDefault()
    e.returnValue = '当前正在录音，离开页面将停止录音。确定要离开吗？'
    return e.returnValue
  }
}

// 路由离开守卫
onBeforeRouteLeave(async (to, from, next) => {
  if (recording.value) {
    try {
      await showConfirmDialog({
        title: '正在录音中',
        message: '当前正在录音，离开页面将停止录音。确定要离开吗？',
        confirmButtonText: '停止并离开',
        confirmButtonColor: '#ee0a24'
      })
      // 用户确认，停止录音
      handleStopRecording()
      next()
    } catch {
      // 用户取消，阻止导航
      next(false)
    }
  } else {
    next()
  }
})

// 初始化
onMounted(() => {
  fetchDetail()
  fetchStaffList()
  // 添加页面刷新/关闭保护
  window.addEventListener('beforeunload', handleBeforeUnload)
})

// 清理
onUnmounted(() => {
  // 移除页面离开保护
  window.removeEventListener('beforeunload', handleBeforeUnload)
  // 如果正在录音，停止录音
  if (recording.value) {
    handleStopRecording()
  }
  // 确保 WebSocket 关闭
  if (websocket) {
    websocket.close()
    websocket = null
  }
})
</script>

<style lang="scss" scoped>
// 用户菜单弹框
.user-menu-popup {
  width: 320px;
  max-width: 90vw;
}

.user-menu-content {
  padding: 20px;
  background: #ffffff;
  color: var(--text-main);
}

.menu-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  
  span {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-main);
  }
  
  :deep(.van-icon) {
    font-size: 20px;
    color: var(--text-secondary);
    cursor: pointer;
    
    &:hover {
      color: var(--text-main);
    }
  }
}

.menu-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-main);
  
  &:hover {
    background: var(--surface-muted);
  }
  
  :deep(.van-icon) {
    font-size: 20px;
  }
  
  span {
    font-size: 15px;
    font-weight: 500;
  }
}

.meeting-detail-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f5f7ff 0%, #fafbff 50%, #ffffff 100%);
}

// 顶部导航栏
.top-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(99, 102, 241, 0.08);
  box-shadow: 0 2px 12px rgba(99, 102, 241, 0.06);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 32px;
  height: 72px;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 24px;
}

.header-left {
  justify-self: start;
}

.header-center {
  .page-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-main);
    max-width: 400px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.header-right {
  justify-self: end;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: transparent;
  border: 2px solid var(--border);
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary);
    color: var(--primary);
    background: var(--primary-light);
  }

  :deep(.van-icon) {
    font-size: 16px;
  }
}

.end-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--danger);
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
  }

  :deep(.van-icon) {
    font-size: 18px;
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px 6px 6px;
  background: var(--surface-muted);
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--surface-hover);
  }
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary-gradient);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

// 加载状态
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

// 主内容区
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 28px;
}

// 左侧面板
.left-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

// 会议信息卡片（整合录音控制）
.info-card {
  background: var(--surface);
  border-radius: 18px;
  padding: 20px 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  border: 1px solid var(--border-light);
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
}

.status-area {
  display: flex;
  align-items: center;
  gap: 10px;
}

.meeting-id {
  font-size: 12px;
  color: var(--text-tertiary);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;

  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
  }

  &.status-pending {
    background: var(--surface-muted);
    color: var(--text-secondary);
    .status-dot { background: var(--text-tertiary); }
  }

  &.status-running {
    background: var(--warning-light);
    color: var(--warning);
    .status-dot { 
      background: var(--warning);
      animation: pulse 1.5s infinite;
    }
  }

  &.status-completed {
    background: var(--success-light);
    color: var(--success);
    .status-dot { background: var(--success); }
  }
}

// 录音控制区域
.recording-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-record-mini {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 18px;
  background: var(--primary-gradient);
  border: none;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  :deep(.van-icon) {
    font-size: 16px;
  }
}

.btn-upload-mini {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--surface-muted);
  border: 1px solid var(--border);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover:not(.disabled) {
    border-color: var(--primary);
    color: var(--primary);
    background: var(--primary-light);
  }

  &.disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  :deep(.van-icon) {
    font-size: 14px;
  }
}

.recording-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: var(--danger-light);
  border-radius: 20px;
  
  .rec-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--text-tertiary);
    
    &.active {
      background: var(--danger);
      animation: pulse 1s infinite;
    }
  }
  
  .rec-text {
    font-size: 12px;
    font-weight: 600;
    color: var(--danger);
  }
}

.recording-btns {
  display: flex;
  gap: 6px;
}

.btn-mini {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-secondary);

  &:hover {
    border-color: var(--primary);
    color: var(--primary);
  }
  
  &.warning {
    border-color: var(--warning);
    color: var(--warning);
    background: var(--warning-light);
  }
  
  &.danger {
    border-color: var(--danger);
    color: var(--danger);
    
    &:hover {
      background: var(--danger);
      color: #fff;
    }
  }

  :deep(.van-icon) {
    font-size: 16px;
  }
}

.completed-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: var(--success-light);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: var(--success);
  
  :deep(.van-icon) {
    font-size: 14px;
  }
}

// 会议信息网格
.info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: var(--surface-muted);
  border-radius: 12px;
  
  :deep(.van-icon) {
    font-size: 18px;
    color: var(--primary);
    flex-shrink: 0;
  }
  
  .label {
    font-size: 11px;
    color: var(--text-tertiary);
  }
  
  .value {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-main);
    
    &.text-success { color: var(--success); }
    &.text-warning { color: var(--warning); }
    &.text-muted { color: var(--text-tertiary); }
  }
}

// 标签和说明
.info-extra {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px dashed var(--border-light);
}

.info-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  padding: 4px 10px;
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.info-desc {
  flex: 1;
  min-width: 200px;
  
  .desc-text {
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.5;
  }
}

// 实时识别预览
.realtime-preview {
  margin-top: 16px;
  padding: 14px 16px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(52, 211, 153, 0.04) 100%);
  border: 1px solid var(--success);
  border-radius: 12px;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 12px;
  color: var(--success);
  font-weight: 600;
}

.preview-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-tertiary);
  
  &.active {
    background: var(--success);
    animation: pulse 1.5s infinite;
  }
}

.preview-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-main);
}

// 对话记录卡片
.dialogs-card {
  background: var(--surface);
  border-radius: 18px;
  padding: 20px 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  border: 1px solid var(--border-light);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  
  h3 {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 15px;
    font-weight: 600;
    color: var(--text-main);
    margin: 0;
    
    :deep(.van-icon) {
      font-size: 18px;
      color: var(--primary);
    }
  }
  
  .header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

/* 复制对话按钮 */
.btn-copy-dialogs {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: linear-gradient(135deg, var(--primary-light) 0%, rgba(139, 92, 246, 0.08) 100%);
  border: 1px solid var(--primary);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  color: var(--primary);
  cursor: pointer;
  transition: all 0.2s ease;
  
  :deep(.van-icon) {
    font-size: 14px;
  }
  
  &:hover {
    background: var(--primary);
    color: white;
  }
  
  &:active {
    transform: scale(0.98);
  }
}

.dialog-count {
  font-size: 12px;
  color: var(--text-tertiary);
  padding: 3px 10px;
  background: var(--surface-muted);
  border-radius: 12px;
}

.dialogs-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 450px;
  overflow-y: auto;
}

.dialog-item {
  position: relative;
  padding: 14px 16px;
  padding-right: 100px; // 为右上角播放器留空间
  background: var(--surface-muted);
  border-radius: 12px;
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  }
}

// 迷你音频播放器 - 右上角透明白色风格
.dialog-audio-mini {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  
  audio {
    display: none; // 隐藏原生控件
  }
  
  .audio-play-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    padding: 0;
    background: transparent;
    border: none;
    cursor: pointer;
    color: var(--primary);
    transition: all 0.2s ease;
    
    &:hover {
      transform: scale(1.1);
    }
    
    :deep(.van-icon) {
      font-size: 20px;
    }
  }
  
  .audio-time {
    font-size: 10px;
    font-weight: 500;
    color: var(--text-secondary);
    min-width: 28px;
    font-family: 'SF Mono', Monaco, monospace;
  }
}

.dialog-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.dialog-time {
  font-size: 12px;
  font-weight: 600;
  color: var(--primary);
  background: var(--primary-light);
  padding: 3px 8px;
  border-radius: 6px;
}

.dialog-speaker {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-main);
  font-weight: 500;
  
  :deep(.van-icon) {
    font-size: 13px;
    color: var(--text-tertiary);
  }
}

.dialog-role {
  font-size: 11px;
  color: var(--text-secondary);
}

.btn-assign {
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 3px 8px;
  background: var(--primary);
  border: none;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    opacity: 0.9;
  }

  :deep(.van-icon) {
    font-size: 12px;
  }
}

.dialog-content {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-main);
  padding: 10px 12px;
  background: var(--surface);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--surface-hover);
  }
}

// 旧的 .dialog-audio 已移除，改用 .dialog-audio-mini

.empty-dialogs {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-tertiary);
  
  :deep(.van-icon) {
    font-size: 40px;
    margin-bottom: 12px;
    opacity: 0.5;
  }
  
  p {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-secondary);
    margin: 0 0 6px;
  }
  
  span {
    font-size: 12px;
  }
}

// 右侧面板 - AI 总结
.right-panel {
  position: sticky;
  top: 96px;
  height: fit-content;
}

.summary-card {
  background: var(--surface);
  border-radius: 18px;
  padding: 20px 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  border: 1px solid var(--border-light);
}

.summary-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding: 14px 16px;
  background: linear-gradient(135deg, var(--primary-light) 0%, rgba(139, 92, 246, 0.08) 100%);
  border-radius: 12px;
  border: 1px solid rgba(99, 102, 241, 0.1);
}

.btn-generate {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: var(--primary-gradient);
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  :deep(.van-icon) {
    font-size: 16px;
  }
}

.summary-status {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.summary-content {
  pre {
    margin: 0;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: inherit;
    font-size: 13px;
    line-height: 1.8;
    color: var(--text-main);
    padding: 16px;
    background: var(--surface-muted);
    border-radius: 12px;
    margin-bottom: 12px;
    max-height: 350px;
    overflow-y: auto;
  }
}

.btn-copy {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-main);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary);
    color: var(--primary);
    background: var(--primary-light);
  }

  :deep(.van-icon) {
    font-size: 14px;
  }
}

.empty-summary {
  text-align: center;
  padding: 40px 16px;
  
  .empty-icon {
    width: 64px;
    height: 64px;
    margin: 0 auto 16px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary-light) 0%, rgba(139, 92, 246, 0.1) 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    
    :deep(.van-icon) {
      font-size: 28px;
      color: var(--primary);
      opacity: 0.7;
    }
  }
  
  p {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-secondary);
    margin: 0 0 6px;
  }
  
  span {
    font-size: 12px;
    color: var(--text-tertiary);
    line-height: 1.5;
  }
}

// 弹窗样式
.assign-popup,
.edit-popup {
  width: 500px;
  max-width: 90vw;
}

.assign-modal,
.edit-modal {
  padding: 28px;
  background: #ffffff;
  color: var(--text-main);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  
  h3 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-main);
    margin: 0;
  }
  
  :deep(.van-icon) {
    font-size: 22px;
    color: var(--text-secondary);
    cursor: pointer;
    
    &:hover {
      color: var(--text-main);
    }
  }
}

.staff-list {
  max-height: 300px;
  overflow-y: auto;
  margin: 20px 0;
}

.staff-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border: 2px solid var(--border);
  border-radius: 14px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: var(--primary);
    background: var(--primary-light);
  }
  
  &.active {
    border-color: var(--primary);
    background: var(--primary-light);
  }
}

.staff-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--primary-gradient);
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.staff-info {
  flex: 1;
  min-width: 0;
  
  strong {
    display: block;
    font-size: 15px;
    color: var(--text-main);
    margin-bottom: 4px;
  }
  
  span {
    font-size: 13px;
    color: var(--text-secondary);
  }
}

.check-icon {
  font-size: 22px;
  color: var(--primary);
}

.empty-staff {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-tertiary);
  
  :deep(.van-icon) {
    font-size: 36px;
    margin-bottom: 12px;
    opacity: 0.5;
  }
  
  p {
    margin: 0;
    font-size: 14px;
  }
}

.modal-footer {
  display: flex;
  gap: 14px;
  padding-top: 20px;
  border-top: 1px solid var(--border-light);
}

.btn-cancel,
.btn-confirm {
  flex: 1;
  padding: 14px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel {
  border: 2px solid var(--border);
  background: var(--surface);
  color: var(--text-main);
  
  &:hover {
    background: var(--surface-muted);
  }
}

.btn-confirm {
  border: none;
  background: var(--primary-gradient);
  color: #fff;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  
  &:hover:not(:disabled) {
    box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.edit-textarea {
  width: 100%;
  padding: 16px;
  border: 2px solid var(--border);
  border-radius: 14px;
  font-size: 15px;
  line-height: 1.7;
  color: var(--text-main);
  resize: none;
  font-family: inherit;
  margin-bottom: 20px;
  
  &:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 4px var(--primary-light);
  }
}

// 动画
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

// 响应式
@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .right-panel {
    position: static;
  }
}

@media (max-width: 900px) {
  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 16px;
  }
  
  .header-content {
    padding: 0 16px;
    height: 60px;
  }
  
  .header-center .page-title {
    font-size: 15px;
    text-align: center;
  }
  
  .back-btn span,
  .end-btn span {
    display: none;
  }
  
  .back-btn,
  .end-btn {
    padding: 8px 12px;
  }
  
  .info-grid {
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  
  .info-item {
    padding: 10px;
  }
  
  .card-top {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .recording-area {
    width: 100%;
    justify-content: flex-end;
  }
  
  .btn-record-mini {
    flex: 1;
    justify-content: center;
  }
}

/* 音频上传浮动框 - 右侧固定定位（紧凑模式） */
.audio-upload-floating-wrapper {
  position: fixed;
  right: 16px;
  bottom: 20px;
  z-index: 1000;
  width: 320px;
  max-width: calc(100vw - 32px);
  background: var(--surface, #fff);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  border-radius: 12px;
  overflow: visible;
  font-size: 12px;
  
  // 缩小内部组件
  :deep(.card-header) {
    padding: 8px 12px;
    
    .title {
      font-size: 12px;
    }
  }
  
  :deep(.drop-zone) {
    padding: 12px;
    min-height: 60px;
    
    .drop-icon {
      font-size: 20px;
    }
    
    .drop-text {
      font-size: 11px;
    }
    
    .drop-hint {
      font-size: 10px;
    }
  }
  
  :deep(.file-info) {
    padding: 6px 12px;
    font-size: 10px;
  }
  
  :deep(.progress-section) {
    padding: 8px 12px;
  }
  
  :deep(.controls) {
    padding: 8px 12px;
    gap: 6px;
    
    .van-button {
      height: 28px;
      font-size: 11px;
      padding: 0 10px;
    }
  }
}

@media (max-width: 768px) {
  .audio-upload-floating-wrapper {
    width: 300px;
    right: 12px;
    bottom: 12px;
  }
}

/* 实时识别预览卡片 - 独立显示在对话记录上方 */
.upload-live-preview-card {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(99, 102, 241, 0.06) 100%);
  border-radius: 12px;
  padding: 14px 16px;
  margin-bottom: 16px;
  border: 1px solid rgba(16, 185, 129, 0.2);
  
  .preview-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    font-weight: 600;
    color: var(--success);
    margin-bottom: 8px;
    
    .preview-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--success);
      
      &.active {
        animation: pulse 1.5s ease-in-out infinite;
      }
    }
  }
  
  .preview-content {
    font-size: 14px;
    color: var(--text-main);
    line-height: 1.6;
    word-break: break-all;
  }
}
</style>
