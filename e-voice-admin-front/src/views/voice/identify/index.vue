<template>
  <div class="voice-identify-container">
    <ACard class="main-card">
      <template #title>
        <div class="card-header">
          <icon-sound size="24" style="color: rgb(var(--blue-6))" />
          <span class="title">实时语音识别</span>
          <ATag :color="wsConnected ? 'green' : 'red'" size="small">
            {{ wsConnected ? '已连接' : '未连接' }}
          </ATag>
        </div>
      </template>

      <!-- 连接控制区域 -->
      <div class="control-section">
        <ASpace size="medium">
          <AButton 
            type="primary" 
            :loading="wsConnecting"
            :disabled="wsConnected"
            @click="connectWS"
          >
            <template #icon><icon-wifi /></template>
            {{ wsConnecting ? '连接中...' : '连接服务' }}
          </AButton>
          
          <AButton 
            :disabled="!wsConnected"
            @click="disconnectWS"
          >
            <template #icon><icon-disconnect /></template>
            断开连接
          </AButton>
        </ASpace>
      </div>

      <!-- 录音控制区域 -->
      <div class="recording-section">
        <div class="recording-controls">
          <ASpace size="large">
            <AButton 
              type="primary" 
              size="large"
              :disabled="!wsConnected || isRealtimeRecording"
              @click="startRealtime"
              class="record-btn"
            >
              <template #icon><icon-record size="20" /></template>
              开始识别
            </AButton>
            
            <AButton 
              status="danger" 
              size="large"
              :disabled="!isRealtimeRecording"
              @click="stopRealtime"
              class="stop-btn"
            >
              <template #icon><icon-record-stop size="20" /></template>
              停止识别
            </AButton>
            
            <AButton 
              :disabled="isRealtimeRecording"
              @click="clearResults"
            >
              <template #icon><icon-delete /></template>
              清空结果
            </AButton>
          </ASpace>
        </div>

        <!-- 录音状态显示 -->
        <div class="recording-status" v-if="isRealtimeRecording || displayTime !== '00:00'">
          <div class="status-info">
            <div class="timer-display">
              <icon-clock-circle />
              <span class="time">{{ displayTime }}</span>
            </div>
            
            <div class="volume-meter">
              <span class="volume-label">音量</span>
              <div class="volume-bar">
                <div class="volume-fill" :style="{ width: volumePercent + '%' }"></div>
              </div>
              <span class="volume-percent">{{ volumePercent }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 识别结果展示 -->
      <div class="results-section">
        <ACard title="识别结果" class="results-card">
          <div class="result-content">
            <div class="partial-result">
              <div class="result-label">
                <icon-loading v-if="isRealtimeRecording" spin />
                <icon-message v-else />
                实时内容
              </div>
              <div class="partial-text">
                <template v-if="hasPartialText">
                  <span v-if="partialConfirmedText" class="partial-confirmed">{{ partialConfirmedText }}</span>
                  <span v-if="partialCandidateText" class="partial-candidate">{{ partialCandidateText }}</span>
                </template>
                <template v-else>
                  {{ isRealtimeRecording ? '正在监听语音...' : '等待开始识别' }}
                </template>
              </div>
              <div class="partial-meta" v-if="hasPartialText || partialConfidence !== null">
                <span v-if="partialSegmentId">段落 {{ partialSegmentId }}</span>
                <span v-if="partialRevision !== null">修订 #{{ partialRevision }}</span>
                <span v-if="partialConfidence !== null">置信度 {{ Math.round(partialConfidence * 100) }}%</span>
              </div>
            </div>

            <ADivider />

            <div class="final-result">
              <div class="result-label">
                <icon-check-circle />
                确认文本
              </div>
              <div class="final-text">
                <template v-if="finalDisplaySentences.length">
                  <p
                    v-for="(sentence, index) in finalDisplaySentences"
                    :key="`${sentence}-${index}`"
                    class="final-sentence"
                  >
                    {{ sentence }}
                  </p>
                </template>
                <template v-else>
                  暂无识别结果
                </template>
              </div>
            </div>
          </div>
        </ACard>
      </div>

      <!-- 高级配置 -->
      <div class="config-section">
        <ACard title="高级配置" size="small" class="config-card">
          <div class="config-row">
            <ASpace>
              <div class="config-item">
                <label>协议版本:</label>
                <ASpace>
                  <AButton type="primary" disabled>实时识别 v2</AButton>
                </ASpace>
              </div>

              <div class="config-item">
                <label>音频块间隔:</label>
                <ASelect 
                  v-model="chunkIntervalMs" 
                  :disabled="isRealtimeRecording"
                  style="width: 120px"
                  @change="onChunkIntervalChange"
                >
                  <AOption :value="64">64ms</AOption>
                  <AOption :value="128">128ms</AOption>
                  <AOption :value="256">256ms (默认)</AOption>
                  <AOption :value="512">512ms</AOption>
                  <AOption :value="1024">1024ms</AOption>
                </ASelect>
              </div>
              
              <div class="config-item">
                <ACheckbox v-model="DROP_SILENCE" :disabled="isRealtimeRecording">
                  启用静音检测
                </ACheckbox>
              </div>
              
              <div class="config-item">
                <ACheckbox v-model="APPLY_CUSTOM_AGC" :disabled="isRealtimeRecording">
                  自适应增益控制
                </ACheckbox>
              </div>

              <div class="config-item">
                <ACheckbox v-model="recordingPreferences.enableHotwords" :disabled="isRealtimeRecording">
                  热词增强
                </ACheckbox>
              </div>

              <div class="config-item">
                <ACheckbox v-model="recordingPreferences.enableSpeaker" :disabled="isRealtimeRecording">
                  声纹辅助
                </ACheckbox>
              </div>
            </ASpace>
          </div>
          
          <div class="config-info">
            <div class="config-summary">
              <div class="summary-line">
                <strong>链路策略:</strong>
                <span>{{ gatewaySummary }}</span>
              </div>
              <div class="summary-line">
                <strong>音频配置:</strong>
                <span>
                  {{ chunkIntervalMs }}ms 间隔 ({{ chunkSamples }} 样本/块)，静音检测{{ DROP_SILENCE ? '开启' : '关闭' }}，自适应增益{{ APPLY_CUSTOM_AGC ? '开启' : '关闭' }}，热词{{ recordingPreferences.enableHotwords ? '开启' : '关闭' }}，声纹{{ recordingPreferences.enableSpeaker ? '开启' : '关闭' }}
                </span>
              </div>
              <div class="summary-line debug-json" v-if="showLogs">
                <strong>配置JSON:</strong>
                <code>{{ JSON.stringify({ preferences: recordingPreferences }, null, 0) }}</code>
              </div>
            </div>
          </div>
        </ACard>
      </div>

      <!-- 日志控制 -->
      <div class="logs-section">
        <div class="logs-header">
          <ASpace>
            <ACheckbox v-model="showLogs">显示详细日志</ACheckbox>
            <AButton size="small" @click="refreshServerLogs">
              <template #icon><icon-refresh /></template>
              拉取服务关键日志
            </AButton>
            <AButton size="small" :disabled="!logs" @click="downloadLogs">
              <template #icon><icon-download /></template>
              下载日志
            </AButton>
            <AButton size="small" :disabled="!logs" @click="copyLogs">
              <template #icon><icon-copy /></template>
              复制日志
            </AButton>
          </ASpace>
        </div>
        
        <ACard v-show="showLogs" class="logs-card">
          <template #title>
            <icon-file-text />
            系统日志
          </template>
          <div class="log-content">{{ logs || '暂无日志' }}</div>
        </ACard>
      </div>

      <!-- 实时状态面板 -->
      <div class="logs-section">
        <ACard class="logs-card" title="实时状态">
          <div class="log-content">
            <div>连接: {{ wsConnected ? '已连接' : '未连接' }} | 会话数: {{ status.counters.active_connections || 0 }}</div>
            <div>消息: {{ status.counters.total_messages || 0 }} | 块: {{ status.counters.total_chunks || 0 }} | 实时: {{ status.counters.total_partials || 0 }} | 最终: {{ status.counters.total_finals || 0 }}</div>
            <div v-if="(status.active_sessions || []).length">活跃会话: {{ (status.active_sessions || []).length }}</div>
          </div>
        </ACard>
      </div>
    </ACard>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onBeforeUnmount } from 'vue';
import { defHttp } from '@/utils/http';

const wsHost = (import.meta as any).env.VITE_API_PY_WS_HOST || 'ws://localhost:8210';
const httpHost = wsHost.replace(/^wss:/, 'https:').replace(/^ws:/, 'http:');

const recordingPreferences = reactive({
  enableHotwords: false,
  enableSpeaker: false
});

const gatewaySummary = '直连实时识别 v2 链路';

let websocket: WebSocket | null = null;
let audioContext: AudioContext | null = null;
let scriptProcessor: ScriptProcessorNode | null = null;
let mediaStream: MediaStream | null = null;
let timer: number | null = null;
let startTs = 0;
let reconnectTimer: number | null = null;
let reconnectAttempts = 0;
let heartbeatTimer: number | null = null;
let lastPongTs = 0;

const wsConnected = ref(false);
const wsConnecting = ref(false);
const isRealtimeRecording = ref(false);
const finalSentences = ref<string[]>([]);
const finalDisplaySentences = computed(() => finalSentences.value.filter(Boolean));
const partialConfirmedText = ref('');
const partialCandidateText = ref('');
const partialCombinedText = computed(() => `${partialConfirmedText.value}${partialCandidateText.value}`);
const hasPartialText = computed(() => Boolean(partialConfirmedText.value || partialCandidateText.value));
const partialConfidence = ref<number | null>(null);
const partialRevision = ref<number | null>(null);
const partialSegmentId = ref('');
const showLogs = ref(true);
const logs = ref('');
const displayTime = ref('00:00');
const volumePercent = ref(0);
const status = ref<any>({ counters: {}, active_sessions: [] });
let statusTimer: number | null = null;

// 🌐 基于网络标准的自适应增益控制
let gainHistory: number[] = [];
let currentGain = 15.0; // 默认增益（网络推荐范围内）

// 🔧 可配置的音频处理参数
const chunkIntervalMs = ref(256);  // chunk间隔时间(毫秒)
const chunkSamples = ref(4096);    // 对应的采样数
const APPLY_CUSTOM_AGC = ref(false);    // 是否应用自定义AGC
const DROP_SILENCE = ref(true);         // 是否丢弃静音帧（现在默认开启，但阈值已放宽）
const DISABLE_WEBRTC_DSP = true;        // 关闭浏览器内置回声/降噪/自动增益
let seq = 0;                            // 分片序号，用于排查丢包乱序

// 🔧 根据时间间隔计算采样数
function calculateChunkSamples(intervalMs: number): number {
  const sampleRate = 16000; // 16kHz采样率
  const samples = Math.round((intervalMs / 1000) * sampleRate);
  // 确保是2的幂次方，便于音频处理
  const powers = [256, 512, 1024, 2048, 4096, 8192, 16384];
  return powers.find(p => p >= samples) || 4096;
}

// 🔧 chunk间隔变化处理
function onChunkIntervalChange() {
  chunkSamples.value = calculateChunkSamples(chunkIntervalMs.value);
  addLog('info', `音频块配置更新: ${chunkIntervalMs.value}ms (${chunkSamples.value}样本)`);
}

function calculateAdaptiveGain(rms: number): number {
  // 网络标准：1-32倍增益范围，目标RMS: 0.01-0.1
  const TARGET_RMS = 0.05;           // 目标RMS（-26dB）
  const MIN_GAIN = 1.0;              // 最小增益（网络标准）
  const MAX_GAIN = 32.0;             // 最大增益（网络标准）
  const ADAPTATION_SPEED = 0.1;      // 适应速度
  
  // 计算理想增益
  let idealGain = TARGET_RMS / (rms + 1e-10);
  idealGain = Math.max(MIN_GAIN, Math.min(MAX_GAIN, idealGain));
  
  // 平滑调整（避免剧烈变化）
  currentGain = currentGain * (1 - ADAPTATION_SPEED) + idealGain * ADAPTATION_SPEED;
  
  // 记录增益历史（用于监控）
  gainHistory.push(currentGain);
  if (gainHistory.length > 10) gainHistory.shift();
  
  return currentGain;
}

function addLog(level: 'info' | 'error' | 'partial' | 'final' | 'success', message: string) {
  const ts = new Date().toLocaleTimeString();
  const prefix = level === 'error' ? '❌' : level === 'success' ? '✅' : level === 'partial' ? '🗣️' : level === 'final' ? '🏁' : 'ℹ️';
  logs.value += `[${ts}] ${prefix} ${message}\n`;
}

// 文本后处理：大小写、规范化等
function postProcessText(input: string): string {
  if (!input) return input;
  let t = input;
  // 统一将 ipo -> IPO（大小写规范化）
  t = t.replace(/\bipo\b/gi, 'IPO');
  // 兼容带标点的 IPO.
  t = t.replace(/\bipo(?=[\u4e00-\u9fa5\w]?\.|\s|$)/gi, 'IPO');
  return t;
}

function syncConfirmedSentencesFromState(confirmed: string) {
  const normalized = confirmed.replace(/\s+/g, ' ').trim();
  if (!normalized) return;

  const segments = normalized
    .split(/(?<=[。！？!?…])/u)
    .map(seg => seg.trim())
    .filter(Boolean);

  if (segments.length > 0) {
    finalSentences.value = segments;
  } else {
    finalSentences.value = [normalized];
  }
}

async function refreshServerLogs() {
  try {
    const res = await fetch(`${httpHost}/logs/key`);
    const txt = await res.text();
    addLog('info', '载入服务关键日志');
    logs.value += `\n===== 服务器关键日志 =====\n` + txt + `\n==========================\n`;
  } catch (e: any) {
    addLog('error', `载入关键日志失败: ${e?.message || e}`);
  }
}

async function refreshWsStatus() {
  try {
    const res = await fetch(`${httpHost}/ws/status`);
    const data = await res.json();
    status.value = data || { counters: {}, active_sessions: [] };
  } catch {}
}

async function resolveWsUrl() {
  try {
    const res: any = await defHttp.post({ url: '/voice/gateway/wsRecognize' });
    const data = res?.data && typeof res.data === 'object' ? res.data : res;
    const ws = data?.ws;
    if (ws && typeof ws === 'string') return ws;
  } catch (e: any) {
    addLog('error', `获取网关WS地址失败，降级直连: ${e?.message || e}`);
  }
  return `${wsHost}/ws/recognize`;
}

async function connectWS() {
  if (wsConnected.value || wsConnecting.value) return;
  try {
    wsConnecting.value = true;
    const url = await resolveWsUrl();
    addLog('info', `连接 ${url}`);
    websocket = new WebSocket(url);
    websocket.onopen = () => {
      wsConnected.value = true;
      wsConnecting.value = false;
      reconnectAttempts = 0;
      if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }
      addLog('success', 'WebSocket连接已建立');
      // 心跳：每10s发送一次，若30s未收到pong则判定断线
      startHeartbeat();
      // 开始轮询状态
      if (!statusTimer) {
        statusTimer = window.setInterval(refreshWsStatus, 5000) as unknown as number;
      }
    };
    websocket.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        if (data && data.type === 'pong') {
          lastPongTs = Date.now();
          return;
        }
        handleWSMessage(data);
      } catch (e: any) {
        addLog('error', `消息解析失败: ${e?.message || e}`);
      }
    };
    websocket.onclose = (event: CloseEvent) => {
      addLog('info', `WebSocket已关闭: code=${event.code} reason=${event.reason || '无'}`);
      wsConnected.value = false;
      stopHeartbeat();
      if (isRealtimeRecording.value) stopRealtime();
      if (statusTimer) { clearInterval(statusTimer); statusTimer = null; }
      scheduleReconnect();
    };
    websocket.onerror = () => {
      addLog('error', 'WebSocket错误');
    };
  } catch (e: any) {
    wsConnecting.value = false;
    addLog('error', `连接失败: ${e?.message || e}`);
  }
}

function disconnectWS() {
  if (websocket) {
    try {
      // 优先结束实时识别，通知服务端输出最终结果
      if (isRealtimeRecording.value && websocket.readyState === WebSocket.OPEN) {
        try { websocket.send(JSON.stringify({ type: 'end' })); } catch {}
      }
      websocket.close(1000, '用户主动断开');
    } catch {}
    websocket = null;
  }
}

function handleWSMessage(data: any) {
  switch (data.type) {
    case 'started':
      addLog('info', `识别开始: ${data.message || ''}`);
      if (recordingPreferences.enableHotwords) {
        addLog('info', '热词增强已启用');
      }
      if (recordingPreferences.enableSpeaker) {
        addLog('info', '声纹辅助已启用');
      }
      break;
    case 'partial':
      if (!isRealtimeRecording.value) break;
      {
        const textState = data?.text_state ?? {};
        const rawConfirmed = typeof textState.confirmed_text === 'string' ? textState.confirmed_text : '';
        const rawCandidate = typeof textState.candidate_text === 'string'
          ? textState.candidate_text
          : (typeof data.text === 'string' ? data.text : '');
        const rawCombined = typeof data.combined_text === 'string'
          ? data.combined_text
          : typeof textState.full_text === 'string'
            ? textState.full_text
            : '';

        const confirmedProcessed = rawConfirmed ? postProcessText(rawConfirmed) : '';
        if (confirmedProcessed) {
          syncConfirmedSentencesFromState(confirmedProcessed);
        }
        partialConfirmedText.value = confirmedProcessed;

        let candidateProcessed = rawCandidate ? postProcessText(rawCandidate) : '';
        partialCandidateText.value = candidateProcessed;

        let combinedProcessed = rawCombined ? postProcessText(rawCombined) : '';
        if (!combinedProcessed) {
          combinedProcessed = `${partialConfirmedText.value}${partialCandidateText.value}`;
        } else if (!candidateProcessed && partialConfirmedText.value && combinedProcessed.startsWith(partialConfirmedText.value)) {
          partialCandidateText.value = combinedProcessed.slice(partialConfirmedText.value.length);
        } else if (!candidateProcessed && !partialConfirmedText.value && combinedProcessed) {
          partialCandidateText.value = combinedProcessed;
        }

        let confValue: number | null = null;
        if (typeof data.confidence === 'number') {
          confValue = data.confidence;
        } else if (typeof data.confidence === 'string') {
          const parsed = Number.parseFloat(data.confidence);
          confValue = Number.isNaN(parsed) ? null : parsed;
        } else if (typeof textState.confidence === 'number') {
          confValue = textState.confidence;
        }
        if (confValue !== null) {
          confValue = Math.min(Math.max(confValue, 0), 1);
        }
        partialConfidence.value = confValue;

        if (typeof data.revision === 'number') {
          partialRevision.value = data.revision;
        } else if (typeof textState.revision === 'number') {
          partialRevision.value = textState.revision;
        } else {
          partialRevision.value = null;
        }

        if (typeof data.segment_id === 'string') {
          partialSegmentId.value = data.segment_id;
        } else if (typeof textState.segment_id === 'string') {
          partialSegmentId.value = textState.segment_id;
        } else {
          partialSegmentId.value = '';
        }

        const metaParts: string[] = [];
        if (partialSegmentId.value) metaParts.push(`seg ${partialSegmentId.value}`);
        if (partialRevision.value !== null) metaParts.push(`rev ${partialRevision.value}`);
        if (partialConfidence.value !== null) {
          metaParts.push(`conf ${Math.round(partialConfidence.value * 100)}%`);
        }

        const logCombined = combinedProcessed || partialCombinedText.value || '[空]';
        const metaLabel = metaParts.length ? ` (${metaParts.join(', ')})` : '';
        addLog('partial', `实时${metaLabel}: ${logCombined}`);
      }
      break;
    case 'final':
      if (data.text && data.text.trim()) {
        const finalProcessed = postProcessText(data.text.trim());
        const idx = typeof data.index === 'number' && data.index >= 0 ? data.index : finalSentences.value.length;
        if (finalSentences.value.length <= idx) {
          finalSentences.value.length = idx + 1;
        }
        finalSentences.value[idx] = finalProcessed;
        partialConfirmedText.value = '';
        partialCandidateText.value = '';
        partialConfidence.value = null;
        partialRevision.value = null;
        partialSegmentId.value = '';

        const metaParts: string[] = [];
        if (typeof data.segment_id === 'string' && data.segment_id) metaParts.push(`seg ${data.segment_id}`);
        if (typeof data.selected_source === 'string' && data.selected_source) metaParts.push(data.selected_source);
        const metaLabel = metaParts.length ? ` (${metaParts.join(' | ')})` : '';
        addLog('final', `确认(#${idx})${metaLabel}: ${finalProcessed}`);
      }
      break;
    case 'session_end':
      addLog('info', `会话结束: ${data.message || ''}`);
      break;
    case 'error':
      addLog('error', data.message || '识别错误');
      break;
    default:
      addLog('info', `未知消息: ${JSON.stringify(data)}`);
  }
}

async function startRealtime() {
  if (!websocket || websocket.readyState !== WebSocket.OPEN) {
    addLog('error', '请先连接WebSocket');
    return;
  }
  try {
    // 🌐 基于网络搜索的WebRTC标准优化配置
    mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        // 标准采样率配置
        sampleRate: { ideal: 16000, min: 8000, max: 48000 },
        channelCount: { ideal: 1, min: 1, max: 2 },

        // WebRTC DSP 可选禁用，最大化保留原音
        echoCancellation: !DISABLE_WEBRTC_DSP,
        noiseSuppression: !DISABLE_WEBRTC_DSP,
        autoGainControl: !DISABLE_WEBRTC_DSP,

        // Chrome 扩展键同理
        googEchoCancellation: !DISABLE_WEBRTC_DSP,
        googNoiseSuppression: !DISABLE_WEBRTC_DSP,
        googAutoGainControl: !DISABLE_WEBRTC_DSP,
        googHighpassFilter: !DISABLE_WEBRTC_DSP,
        googTypingNoiseDetection: !DISABLE_WEBRTC_DSP,

        // 低延迟偏好
        latency: { ideal: 0.01 },
        volume: { ideal: 1.0 },

        // 其他参数（不会影响音频数据本身）
        aspectRatio: 1.0,
        frameRate: { ideal: 50 }
      }
    });
    audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
    const source = audioContext.createMediaStreamSource(mediaStream);
    // 🔧 使用配置的chunk大小创建音频处理器
    scriptProcessor = audioContext.createScriptProcessor(chunkSamples.value, 1, 1);
    scriptProcessor.onaudioprocess = (event: AudioProcessingEvent) => {
      if (!isRealtimeRecording.value || !websocket || websocket.readyState !== WebSocket.OPEN) return;
      const input = event.inputBuffer.getChannelData(0);
      
      // 计算原始RMS
      let sum = 0;
      for (let i = 0; i < input.length; i++) sum += input[i] * input[i];
      const originalRMS = Math.sqrt(sum / input.length);
      
      // 🌐 自定义AGC（可选）
      const adaptiveGain = APPLY_CUSTOM_AGC.value ? calculateAdaptiveGain(originalRMS) : 1.0;
      let amplifiedRMS = originalRMS;
      let amplifiedInput = input;
      if (APPLY_CUSTOM_AGC.value) {
        const tmp = new Float32Array(input.length);
        let amplifiedSum = 0;
        for (let i = 0; i < input.length; i++) {
          tmp[i] = Math.max(-1, Math.min(1, input[i] * adaptiveGain));
          amplifiedSum += tmp[i] * tmp[i];
        }
        amplifiedInput = tmp;
        amplifiedRMS = Math.sqrt(amplifiedSum / amplifiedInput.length);
      }
      
      // 🔧 修复静音检测：放宽阈值，避免过滤有效语音
      const silenceThreshold = 0.0005; // 降低阈值，从0.001调整到0.0005
      if (DROP_SILENCE.value && amplifiedRMS < silenceThreshold) {
        console.log(`🔇 静音检测: 原始RMS=${originalRMS.toFixed(6)}, 增益=${adaptiveGain.toFixed(1)}x, 增益后RMS=${amplifiedRMS.toFixed(6)}`);
        return;
      }
      
      // 🔧 调试：记录通过静音检测的音频块
      console.log(`🎤 音频通过: RMS=${amplifiedRMS.toFixed(6)}, 音量=${volumePercent.value}%`);
      
      // 更新音量显示（基于增益后的RMS）
      volumePercent.value = Math.min(100, Math.max(0, Math.floor(amplifiedRMS * 100)));
      
      // 🔧 修复PCM编码：使用完整的16位范围
      const pcmData = new Int16Array(input.length);
      for (let i = 0; i < input.length; i++) {
        const sample = amplifiedInput[i];
        // 使用完整的16位范围，避免精度丢失
        pcmData[i] = Math.round(sample * (sample < 0 ? 32768 : 32767));
      }
      
      // 直接使用pcmData.buffer，避免额外的数据复制
      const buffer = pcmData.buffer;
      const u8 = new Uint8Array(buffer);
      const b64 = btoa(String.fromCharCode.apply(null, Array.from(u8) as any));
      
        try {
        websocket.send(JSON.stringify({ 
          type: 'chunk', 
          audio: b64, 
          format: 'pcm', 
          sample_rate: audioContext?.sampleRate || 16000,
          seq: (seq += 1),
          // 🌐 基于网络标准的调试信息
          debug: {
            original_rms: originalRMS.toFixed(6),
            amplified_rms: amplifiedRMS.toFixed(6),
            adaptive_gain: adaptiveGain.toFixed(2),
            gain_history: gainHistory.slice(-3).map(g => g.toFixed(1)).join(','),
            compliance: 'WebRTC-Standard',
            audio_size: b64.length,
            pcm_samples: input.length
          }
        }));
        
        // 增强的控制台调试输出 - 添加音频数据详情
        if (amplifiedRMS > silenceThreshold) {
          const avgGain = gainHistory.length > 0 ? 
            (gainHistory.reduce((a, b) => a + b, 0) / gainHistory.length).toFixed(1) : 'N/A';
          console.log(`🎤 发送音频: RMS=${originalRMS.toFixed(6)} -> ${amplifiedRMS.toFixed(6)}, 增益=${adaptiveGain.toFixed(1)}x (平均${avgGain}x), 数据=${b64.length}bytes, 样本=${input.length}`);
        }
      } catch (e: any) {
        addLog('error', `发送失败: ${e?.message || e}`);
      }
    };
    source.connect(scriptProcessor);
    scriptProcessor.connect(audioContext.destination);

    // 发送开始
    const startPayload: Record<string, any> = { type: 'start' };
    if (recordingPreferences.enableHotwords) {
      startPayload.hotwords = true;
    }
    if (recordingPreferences.enableSpeaker) {
      startPayload.speaker = true;
    }
    websocket.send(JSON.stringify(startPayload));
    isRealtimeRecording.value = true;
    startTs = Date.now();
    timer = window.setInterval(() => {
      const sec = Math.floor((Date.now() - startTs) / 1000);
      const mm = String(Math.floor(sec / 60)).padStart(2, '0');
      const ss = String(sec % 60).padStart(2, '0');
      displayTime.value = `${mm}:${ss}`;
    }, 1000) as unknown as number;
    partialConfirmedText.value = '';
    partialCandidateText.value = '';
    partialConfidence.value = null;
    partialRevision.value = null;
    partialSegmentId.value = '';
    addLog('success', '开始实时识别');
  } catch (e: any) {
    addLog('error', `启动失败: ${e?.message || e}`);
    cleanupAudio();
  }
}

function stopRealtime() {
  if (!isRealtimeRecording.value) return;
  try {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.send(JSON.stringify({ type: 'end' }));
    }
  } catch {}
  cleanupAudio();
  isRealtimeRecording.value = false;
  displayTime.value = '00:00';
  addLog('info', '已停止实时识别');
}

function cleanupAudio() {
  if (scriptProcessor) {
    try { scriptProcessor.disconnect(); } catch {}
    scriptProcessor.onaudioprocess = null as any;
    scriptProcessor = null;
  }
  if (audioContext) {
    try { if (audioContext.state !== 'closed') audioContext.close(); } catch {}
    audioContext = null;
  }
  if (mediaStream) {
    try { mediaStream.getTracks().forEach(t => t.stop()); } catch {}
    mediaStream = null;
  }
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
}

function clearResults() {
  partialConfirmedText.value = '';
  partialCandidateText.value = '';
  partialConfidence.value = null;
  partialRevision.value = null;
  partialSegmentId.value = '';
  finalSentences.value = [];
  addLog('info', '已清空结果');
}

function scheduleReconnect() {
  if (isRealtimeRecording.value) return; // 录音中不自动重连
  if (reconnectAttempts >= 5) return; // 最多重连5次
  const delay = Math.min(15000, 1000 * Math.pow(2, reconnectAttempts));
  reconnectAttempts++;
  addLog('info', `准备自动重连（第${reconnectAttempts}次），等待 ${Math.floor(delay / 1000)}s`);
  reconnectTimer = window.setTimeout(() => {
    if (!wsConnected.value && !wsConnecting.value) connectWS();
  }, delay) as unknown as number;
}

function startHeartbeat() {
  stopHeartbeat();
  lastPongTs = Date.now();
  heartbeatTimer = window.setInterval(() => {
    if (!websocket || websocket.readyState !== WebSocket.OPEN) return;
    try { websocket.send(JSON.stringify({ type: 'ping', ts: Date.now() })); } catch {}
    // 超时检测：30秒未收到pong，主动关闭以触发重连
    if (Date.now() - lastPongTs > 30000) {
      addLog('error', '心跳超时，断开重连');
      try { websocket.close(4000, 'heartbeat timeout'); } catch {}
    }
  }, 10000) as unknown as number;
}

function stopHeartbeat() {
  if (heartbeatTimer) {
    clearInterval(heartbeatTimer);
    heartbeatTimer = null;
  }
}

function downloadLogs() {
  if (!logs.value) return;
  const blob = new Blob([logs.value], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `realtime-logs-${new Date().toISOString().replace(/[:.]/g, '-')}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

async function copyLogs() {
  if (!logs.value) return;
  try {
    await navigator.clipboard.writeText(logs.value);
    addLog('success', '日志已复制到剪贴板');
  } catch (e: any) {
    addLog('error', `复制失败: ${e?.message || e}`);
  }
}

onBeforeUnmount(() => {
  if (isRealtimeRecording.value) stopRealtime();
  disconnectWS();
});
</script>

<style scoped>
.voice-identify-container {
  padding: 24px;
  background: var(--color-bg-1);
  min-height: calc(100vh - 120px);
}

.main-card {
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-1);
}

.control-section {
  margin-bottom: 32px;
  padding: 20px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 12px;
  border: 1px solid #e1f5fe;
}

.recording-section {
  margin-bottom: 32px;
}

.recording-controls {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.record-btn {
  background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(22, 119, 255, 0.3);
  transition: all 0.3s ease;
}

.record-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(22, 119, 255, 0.4);
}

.stop-btn {
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.stop-btn:hover {
  transform: translateY(-2px);
}

.recording-status {
  background: var(--color-bg-2);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--color-border);
}

.status-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
}

.timer-display {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: rgb(var(--blue-6));
}

.time {
  font-family: 'Monaco', 'Consolas', monospace;
}

.volume-meter {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  max-width: 300px;
}

.volume-label {
  font-size: 14px;
  color: var(--color-text-2);
  min-width: 32px;
}

.volume-bar {
  flex: 1;
  height: 8px;
  background: var(--color-fill-2);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.volume-fill {
  height: 100%;
  background: linear-gradient(90deg, #52c41a 0%, #73d13d 50%, #ffa940 80%, #ff4d4f 100%);
  border-radius: 4px;
  transition: width 0.2s ease;
  position: relative;
}

.volume-fill::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 2px;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 1px;
}

.volume-percent {
  font-size: 12px;
  color: #86909c;
  min-width: 36px;
  text-align: right;
}

.results-section {
  margin-bottom: 32px;
}

.results-card {
  border-radius: 12px;
  border: 1px solid var(--color-border);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.result-content {
  padding: 8px;
}

.partial-result,
.final-result {
  padding: 16px 0;
}

.result-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--color-text-1);
  margin-bottom: 12px;
}

.partial-text {
  font-size: 16px;
  min-height: 24px;
  line-height: 1.6;
  background: var(--color-fill-2);
  padding: 12px 16px;
  border-radius: 8px;
  border-left: 4px solid rgb(var(--blue-6));
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: baseline;
}

.partial-confirmed {
  color: var(--color-text-1);
  font-weight: 500;
}

.partial-candidate {
  color: rgb(var(--blue-6));
  font-style: italic;
  opacity: 0.85;
}

.partial-meta {
  margin-top: 8px;
  color: #86909c;
  font-size: 12px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.final-text {
  font-size: 16px;
  color: var(--color-text-1);
  min-height: 60px;
  line-height: 1.6;
  background: var(--color-bg-2);
  padding: 16px;
  border-radius: 8px;
  border: 1px solid var(--color-border);
  white-space: pre-wrap;
  word-wrap: break-word;
}

.final-sentence {
  margin: 0 0 8px;
}

.final-sentence:last-child {
  margin-bottom: 0;
}

.logs-section {
  margin-top: 24px;
}

.logs-header {
  margin-bottom: 16px;
}

.logs-card {
  border-radius: 12px;
  border: 1px solid var(--color-border);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.log-content {
  white-space: pre-wrap;
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 16px;
  border-radius: 8px;
  max-height: 300px;
  overflow-y: auto;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.4;
  border: 1px solid #333;
}

.log-content::-webkit-scrollbar {
  width: 6px;
}

.log-content::-webkit-scrollbar-track {
  background: #2d2d2d;
  border-radius: 3px;
}

.log-content::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 3px;
}

.log-content::-webkit-scrollbar-thumb:hover {
  background: #777;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .voice-identify-container {
    padding: 16px;
  }
  
  .status-info {
    flex-direction: column;
    gap: 16px;
  }
  
  .volume-meter {
    max-width: none;
  }
  
  .recording-controls :deep(.arco-space) {
    flex-wrap: wrap;
    justify-content: center;
  }
}

/* 动画效果 */
.partial-text {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.volume-fill {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

/* Dark theme overrides */
:deep(body[arco-theme="dark"]) .voice-identify-container .control-section {
  background: linear-gradient(135deg, var(--color-fill-2) 0%, var(--color-fill-3) 100%);
  border-color: var(--color-border);
}
:deep(body[arco-theme="dark"]) .voice-identify-container .recording-status {
  background: var(--color-bg-2);
  border-color: var(--color-border);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}
:deep(body[arco-theme="dark"]) .voice-identify-container .main-card {
  border-color: var(--color-border);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
}
:deep(body[arco-theme="dark"]) .voice-identify-container .results-card,
:deep(body[arco-theme="dark"]) .voice-identify-container .logs-card {
  border-color: var(--color-border);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}
:deep(body[arco-theme="dark"]) .voice-identify-container .volume-bar {
  background: var(--color-fill-3);
}

.config-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-item label {
  font-size: 14px;
  color: var(--color-text-2);
  min-width: 72px;
}

.config-summary {
  margin-top: 12px;
  background: var(--color-fill-2);
  border-radius: 8px;
  padding: 12px 16px;
  display: grid;
  gap: 6px;
  border: 1px dashed var(--color-border);
}

.summary-line {
  font-size: 13px;
  color: var(--color-text-2);
  display: flex;
  gap: 6px;
  align-items: center;
}

.summary-line strong {
  color: var(--color-text-1);
}

.config-summary .debug-json code {
  font-size: 12px;
  color: var(--color-text-3);
  background: rgba(0, 0, 0, 0.04);
  padding: 2px 6px;
  border-radius: 4px;
  word-break: break-all;
}
</style>