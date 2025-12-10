<template>
  <div class="voice-identify-container">
    <ACard class="main-card">
      <template #title>
        <div class="card-header">
          <icon-sound size="24" style="color: rgb(var(--blue-6))" />
          <span class="title">实时语音识别</span>
          <ATag v-if="activeTab === 'microphone'" :color="wsConnected ? 'green' : 'red'" size="small">
            {{ wsConnected ? '已连接' : '未连接' }}
          </ATag>
        </div>
      </template>

      <!-- Tab 切换 -->
      <ATabs v-model:active-key="activeTab" type="rounded" class="identify-tabs">
        <ATabPane key="microphone" title="🎤 麦克风录音">
          <template #title>
            <span>
              <icon-record style="margin-right: 4px" />
              麦克风录音
            </span>
          </template>
        </ATabPane>
        <ATabPane key="file" title="📂 文件上传测试">
          <template #title>
            <span>
              <icon-folder style="margin-right: 4px" />
              文件上传测试
            </span>
          </template>
        </ATabPane>
      </ATabs>

      <!-- 文件上传测试模式 -->
      <AudioFileTest v-if="activeTab === 'file'" />

      <!-- 麦克风录音模式 -->
      <template v-if="activeTab === 'microphone'">
        <!-- 连接控制区域 -->
        <div class="control-section">
          <ASpace size="medium">
            <AButton type="primary" :loading="wsConnecting" :disabled="wsConnected" @click="connectWS">
              <template #icon><icon-wifi /></template>
              {{ wsConnecting ? '连接中...' : '连接服务' }}
            </AButton>

            <AButton :disabled="!wsConnected" @click="disconnectWS">
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
                class="record-btn"
                @click="startRealtime"
              >
                <template #icon><icon-record size="20" /></template>
                开始识别
              </AButton>

              <AButton
                status="danger"
                size="large"
                :disabled="!isRealtimeRecording"
                class="stop-btn"
                @click="stopRealtime"
              >
                <template #icon><icon-record-stop size="20" /></template>
                停止识别
              </AButton>

              <AButton :disabled="isRealtimeRecording" @click="clearResults">
                <template #icon><icon-delete /></template>
                清空结果
              </AButton>
            </ASpace>
          </div>

          <!-- 录音状态显示 -->
          <div v-if="isRealtimeRecording || displayTime !== '00:00'" class="recording-status">
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
                <div v-if="hasPartialText || partialConfidence !== null" class="partial-meta">
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
                  <template v-else>暂无识别结果</template>
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
                    :disabled="true"
                    style="width: 180px"
                    @change="onChunkIntervalChange"
                  >
                    <AOption :value="DEMO_CHUNK_MS">固定 60ms（对齐 Demo）</AOption>
                  </ASelect>
                </div>

                <div class="config-item">
                  <ACheckbox v-model="DROP_SILENCE" :disabled="isRealtimeRecording">启用静音检测</ACheckbox>
                </div>

                <div class="config-item">
                  <ACheckbox v-model="APPLY_CUSTOM_AGC" :disabled="isRealtimeRecording">自适应增益控制</ACheckbox>
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
                    {{ chunkIntervalMs }}ms 间隔 ({{ chunkSamples }} 样本/块)，静音检测{{
                      DROP_SILENCE ? '开启' : '关闭'
                    }}，自适应增益{{ APPLY_CUSTOM_AGC ? '开启' : '关闭' }}，热词{{
                      recordingPreferences.enableHotwords ? '开启' : '关闭'
                    }}，声纹{{ recordingPreferences.enableSpeaker ? '开启' : '关闭' }}
                  </span>
                </div>
                <div v-if="showLogs" class="summary-line debug-json">
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
              <div>
                连接: {{ wsConnected ? '已连接' : '未连接' }} | 会话数: {{ status.counters.active_connections || 0 }}
              </div>
              <div>
                消息: {{ status.counters.total_messages || 0 }} | 块: {{ status.counters.total_chunks || 0 }} | 实时:
                {{ status.counters.total_partials || 0 }} | 最终: {{ status.counters.total_finals || 0 }}
              </div>
              <div v-if="(status.active_sessions || []).length">
                活跃会话: {{ (status.active_sessions || []).length }}
              </div>
            </div>
          </ACard>
        </div>
      </template>
    </ACard>
  </div>
</template>

<script lang="ts" setup>
import { computed, onBeforeUnmount, reactive, ref } from 'vue';
import { defHttp } from '@/utils/http';
import AudioFileTest from './AudioFileTest.vue';

// Tab 切换
const activeTab = ref('microphone');

const wsHost = (import.meta as any).env.VITE_API_PY_WS_HOST || 'ws://localhost:8210';
const httpHost = wsHost.replace(/^wss:/, 'https:').replace(/^ws:/, 'http:');

const DEMO_CHUNK_MS = 60; // demo 目标：每块约 60ms（960 样本）
const DEMO_CHUNK_INTERVAL = 10; // 与 demo 一致：10 块触发一次在线 ASR
const DEMO_CHUNK_SIZE = [5, 10, 5]; // 与 demo 一致：encoder/lookback 设置
const DEMO_WAV_NAME = 'h5'; // 与 demo 客户端一致的来源标识
const DEMO_PCM_SAMPLES = 960; // 每次发送 960 样本 (16kHz -> ~60ms)
const PROCESSOR_BUFFER_SIZE = 1024; // 浏览器要求 2 的幂回调尺寸，内部再切 960 样本发送

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
let sentChunkCount = 0;

const wsConnected = ref(false);
const wsConnecting = ref(false);
const isRealtimeRecording = ref(false);
const finalSentences = ref<string[]>([]);
const finalDisplaySentences = computed(() => finalSentences.value.filter(Boolean));
// Demo 风格的展示：一行实时文本 + 最终文本累积，避免频繁闪烁/覆盖
const liveText = ref(''); // 实时正在说的内容（累积）
const partialConfirmedText = ref(''); // 保留旧字段用于显示，但逻辑与 liveText 同步
const partialCandidateText = ref('');
const partialCombinedText = computed(
  () => liveText.value || `${partialConfirmedText.value}${partialCandidateText.value}`
);
const hasPartialText = computed(() =>
  Boolean(liveText.value || partialConfirmedText.value || partialCandidateText.value)
);
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
const gainHistory: number[] = [];
let currentGain = 15.0; // 默认增益（网络推荐范围内）

// 🔧 可配置的音频处理参数
const chunkIntervalMs = ref(DEMO_CHUNK_MS); // 固定 ~60ms
const chunkSamples = ref(DEMO_PCM_SAMPLES); // 实际发送 960 样本
const APPLY_CUSTOM_AGC = ref(false); // 是否应用自定义AGC
const DROP_SILENCE = ref(true); // 默认开启静音过滤，减少无效音频推送
const DISABLE_WEBRTC_DSP = true; // 关闭浏览器内置回声/降噪/自动增益
const seq = 0; // 分片序号，用于排查丢包乱序
let pendingPcm: number[] = []; // 缓冲 960 样本对齐发送

// 🎯 增强静音检测状态（智能 VAD 前置）
let consecutiveSilenceChunks = 0; // 连续静音块计数
let consecutiveSpeechChunks = 0; // 连续语音块计数
let isInSpeech = false; // 当前是否处于语音状态
// 阈值说明：RMS 范围通常在 0.0001（静音）到 0.3（大声说话）之间
// 背景噪音一般在 0.001-0.01，正常说话在 0.02-0.15
const SILENCE_THRESHOLD = 0.01; // 静音 RMS 阈值（低于此值认为是静音）
const SPEECH_THRESHOLD = 0.02; // 语音 RMS 阈值（高于此值认为是语音）
const SILENCE_CHUNKS_TO_END = 20; // 连续多少个静音块后认为语音结束（约 1.2 秒）
const SPEECH_CHUNKS_TO_START = 3; // 连续多少个语音块后认为语音开始（约 180ms）
let silenceSkippedCount = 0; // 被跳过的静音块统计
let totalChunksReceived = 0; // 总共收到的音频块数

// 重置静音检测状态
function resetVadState() {
  consecutiveSilenceChunks = 0;
  consecutiveSpeechChunks = 0;
  isInSpeech = false;
  silenceSkippedCount = 0;
  totalChunksReceived = 0;
}

// 🔧 根据时间间隔计算采样数
function calculateChunkSamples(intervalMs: number): number {
  // 对齐 demo 固定 960 样本发送
  return DEMO_PCM_SAMPLES;
}

// 🔧 chunk间隔变化处理
function onChunkIntervalChange() {
  chunkSamples.value = calculateChunkSamples(chunkIntervalMs.value);
  addLog('info', `音频块配置更新: ${chunkIntervalMs.value}ms (${chunkSamples.value}样本)`);
}

function calculateAdaptiveGain(rms: number): number {
  // 网络标准：1-32倍增益范围，目标RMS: 0.01-0.1
  const TARGET_RMS = 0.05; // 目标RMS（-26dB）
  const MIN_GAIN = 1.0; // 最小增益（网络标准）
  const MAX_GAIN = 32.0; // 最大增益（网络标准）
  const ADAPTATION_SPEED = 0.1; // 适应速度

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
  const prefix =
    level === 'error'
      ? '❌'
      : level === 'success'
        ? '✅'
        : level === 'partial'
          ? '🗣️'
          : level === 'final'
            ? '🏁'
            : 'ℹ️';
  logs.value += `[${ts}] ${prefix} ${message}\n`;
}

// 文本后处理：大小写、规范化等
function postProcessText(input: string): string {
  if (!input) return input;
  let t = input;
  // 统一将 ipo -> IPO（大小写规范化）
  t = t.replace(/\bipo\b/gi, 'IPO');
  // 兼容带标点的 IPO.
  t = t.replace(/\bipo(?=[\u4E00-\u9FA5\w]?\.|\s|$)/gi, 'IPO');
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
    logs.value += `\n===== 服务器关键日志 =====\n${txt}\n==========================\n`;
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
    websocket.binaryType = 'arraybuffer';
    websocket.onopen = () => {
      wsConnected.value = true;
      wsConnecting.value = false;
      reconnectAttempts = 0;
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
      }
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
      if (statusTimer) {
        clearInterval(statusTimer);
        statusTimer = null;
      }
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
        try {
          websocket.send(JSON.stringify({ type: 'end' }));
        } catch {}
      }
      websocket.close(1000, '用户主动断开');
    } catch {}
    websocket = null;
  }
}

function sendConfig() {
  if (!websocket || websocket.readyState !== WebSocket.OPEN) return;
  // 与官方 FunASR Demo (funasr_wss_server.py) 配置格式完全对齐
  // 官方 demo 客户端在连接后立即发送配置 JSON
  const payload: Record<string, any> = {
    // 与官方 demo 一致的配置字段（不使用 type 字段，纯 FunASR 风格）
    mode: '2pass',
    chunk_interval: DEMO_CHUNK_INTERVAL, // 与 demo 一致：10 块触发一次在线 ASR
    chunk_size: DEMO_CHUNK_SIZE, // 与 demo 一致：[5, 10, 5]
    encoder_chunk_look_back: DEMO_CHUNK_SIZE[0], // 与 demo 一致
    decoder_chunk_look_back: DEMO_CHUNK_SIZE[2], // 与 demo 一致
    is_speaking: true, // 开始时设置为正在说话
    itn: true, // 启用 ITN
    wav_name: DEMO_WAV_NAME // 来源标识
  };
  try {
    websocket.send(JSON.stringify(payload));
    addLog(
      'info',
      `下发配置 (FunASR demo 对齐): mode=2pass, chunk_interval=${DEMO_CHUNK_INTERVAL}, chunk_size=${JSON.stringify(DEMO_CHUNK_SIZE)}, ITN=on, is_speaking=true`
    );
  } catch (e: any) {
    addLog('error', `配置下发失败: ${e?.message || e}`);
  }
}

function handleWSMessage(data: any) {
  // 兼容官方 FunASR Demo 格式和 nevoice 扩展格式
  // 官方格式: {mode, text, wav_name, is_final}
  // nevoice 格式: {type, text, text_state, session_id, segment_id, mode, is_final, is_speaking, ...}

  // 如果没有 type 字段但有 mode 字段，可能是官方 demo 格式
  // 根据 mode 推断 type
  if (!data.type && data.mode) {
    if (data.mode.includes('online')) {
      data.type = 'partial';
    } else if (data.mode.includes('offline')) {
      data.type = 'correction';
    }
  }

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
        const rawText =
          typeof data.text === 'string' && data.text
            ? data.text
            : typeof textState.full_text === 'string'
              ? textState.full_text
              : '';
        const processed = rawText ? postProcessText(rawText) : '';
        if (processed) {
          // Demo 风格：直接累积实时文本，不做分段覆盖
          liveText.value += processed;
          partialConfirmedText.value = '';
          partialCandidateText.value = liveText.value;
          const modeStr = data.mode ? ` [${data.mode}]` : '';
          const metaLabel = data.segment_id ? ` (seg ${data.segment_id}${modeStr})` : modeStr;
          addLog('partial', `实时${metaLabel}: ${processed}`);
        }
        // 置信度/修订号按需记录
        partialRevision.value = typeof data.revision === 'number' ? data.revision : null;
        partialSegmentId.value = typeof data.segment_id === 'string' ? data.segment_id : '';
        if (typeof data.confidence === 'number') partialConfidence.value = data.confidence;
      }
      break;
    case 'correction':
      // 离线二次纠错结果（带标点和ITN）
      {
        const textState = data?.text_state ?? {};
        const correctedText = typeof data.text === 'string' ? data.text : '';
        const correctedProcessed = correctedText ? postProcessText(correctedText) : '';

        if (correctedProcessed) {
          // Demo 风格：将当前实时文本+纠错一起落地到最终文本，并清空实时区
          finalSentences.value.push(correctedProcessed);
          liveText.value = '';
          partialConfirmedText.value = '';
          partialCandidateText.value = '';
          syncConfirmedSentencesFromState(correctedProcessed);
        }

        const metaParts: string[] = [];
        if (typeof data.segment_id === 'string' && data.segment_id) metaParts.push(`seg ${data.segment_id}`);
        if (typeof data.mode === 'string' && data.mode) metaParts.push(data.mode);
        if (typeof data.revision === 'number') metaParts.push(`rev ${data.revision}`);
        // 显示 is_speaking 状态（官方 demo 语义）
        if (typeof data.is_speaking === 'boolean') metaParts.push(data.is_speaking ? 'speaking' : 'stopped');
        const metaLabel = metaParts.length ? ` (${metaParts.join(' | ')})` : '';
        addLog('success', `纠错${metaLabel}: ${correctedProcessed || '[空]'}`);

        // 如果是 final 或 is_speaking=false，清空 partial 状态
        if (data.is_final || data.is_speaking === false) {
          partialConfidence.value = null;
          partialRevision.value = null;
          partialSegmentId.value = '';
        }
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
        liveText.value = '';
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
    // 下发 FunASR 兼容配置
    sendConfig();

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
    // 🔧 重置缓存对齐 960 样本
    pendingPcm = [];
    sentChunkCount = 0;
    
    // 🎯 重置静音检测状态（重要！）
    resetVadState();
    addLog('info', `静音检测已重置，阈值: 静音<${SILENCE_THRESHOLD} 语音>${SPEECH_THRESHOLD}`);

    // 🔧 使用配置的chunk大小创建音频处理器
    scriptProcessor = audioContext.createScriptProcessor(PROCESSOR_BUFFER_SIZE, 1, 1);
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

      // 🎯 增强静音检测：智能 VAD 前置过滤
      // 核心思路：不是简单的能量阈值，而是基于状态机的智能判断
      // - 语音开始需要连续 N 个高能量块确认
      // - 语音结束需要连续 M 个低能量块确认
      // - 这样可以避免误删有效语音，同时大幅减少无效静音推送
      
      totalChunksReceived++;
      
      if (DROP_SILENCE.value) {
        const isSilentChunk = amplifiedRMS < SILENCE_THRESHOLD;
        const isSpeechChunk = amplifiedRMS >= SPEECH_THRESHOLD;
        
        // 🔍 每 50 个块输出一次当前状态（约 3 秒）
        if (totalChunksReceived % 50 === 0) {
          addLog('info', 
            `📊 VAD状态: RMS=${amplifiedRMS.toFixed(4)}, ` +
            `isInSpeech=${isInSpeech}, ` +
            `静音块=${consecutiveSilenceChunks}, 语音块=${consecutiveSpeechChunks}, ` +
            `已发送=${sentChunkCount}, 已跳过=${silenceSkippedCount}`
          );
        }
        
        if (isSpeechChunk) {
          // 明确的语音能量
          consecutiveSpeechChunks++;
          consecutiveSilenceChunks = 0;
          
          if (!isInSpeech && consecutiveSpeechChunks >= SPEECH_CHUNKS_TO_START) {
            // 状态转换：静音 → 语音
            isInSpeech = true;
            addLog('info', `🎤 检测到语音开始 (RMS=${amplifiedRMS.toFixed(4)}, 跳过了 ${silenceSkippedCount} 个静音块)`);
            silenceSkippedCount = 0;
          }
        } else if (isSilentChunk) {
          // 明确的静音
          consecutiveSilenceChunks++;
          consecutiveSpeechChunks = 0;
          
          if (isInSpeech && consecutiveSilenceChunks >= SILENCE_CHUNKS_TO_END) {
            // 状态转换：语音 → 静音
            isInSpeech = false;
            addLog('info', `🔇 检测到语音结束 (${consecutiveSilenceChunks} 个连续静音块, 已发送 ${sentChunkCount} 块)`);
          }
        } else {
          // 中间能量（SILENCE_THRESHOLD <= RMS < SPEECH_THRESHOLD）
          // 如果已经在说话中，认为是语音的一部分（避免轻声被切断）
          // 如果还没开始说话，保持静音状态（避免背景噪音触发）
          if (isInSpeech) {
            consecutiveSilenceChunks = 0;
            consecutiveSpeechChunks = 0; // 重置，需要重新确认语音
          } else {
            // 中间能量但还没开始说话，算作静音
            consecutiveSilenceChunks++;
            consecutiveSpeechChunks = 0;
          }
        }
        
        // 如果当前不在语音状态，跳过发送
        if (!isInSpeech) {
          silenceSkippedCount++;
          // 每跳过 100 个块记录一次（约 6 秒）
          if (silenceSkippedCount % 100 === 0) {
            addLog('info', `🔕 静音过滤中... 已跳过 ${silenceSkippedCount} 块 (当前RMS=${amplifiedRMS.toFixed(4)})`);
          }
          // 更新音量显示但不发送
          volumePercent.value = Math.min(100, Math.max(0, Math.floor(amplifiedRMS * 500)));
          return;
        }
      }

      // 更新音量显示（基于增益后的RMS）
      volumePercent.value = Math.min(100, Math.max(0, Math.floor(amplifiedRMS * 100)));

      // 🔧 修复PCM编码：使用完整的16位范围，并按 960 样本分片对齐 demo
      const pcmData = new Int16Array(input.length);
      for (let i = 0; i < input.length; i++) {
        const sample = amplifiedInput[i];
        pcmData[i] = Math.round(sample * (sample < 0 ? 32768 : 32767));
        pendingPcm.push(pcmData[i]);
      }

      // 按 960 样本切片发送，保持与 demo 完全一致
      while (pendingPcm.length >= DEMO_PCM_SAMPLES) {
        const chunk = pendingPcm.slice(0, DEMO_PCM_SAMPLES);
        pendingPcm = pendingPcm.slice(DEMO_PCM_SAMPLES);

        sentChunkCount += 1;
        if (sentChunkCount === 1) {
          addLog('info', `首包已发送，长度=${DEMO_PCM_SAMPLES} 样本 (~${(DEMO_PCM_SAMPLES / 16).toFixed(1)}ms)`);
        } else if (sentChunkCount % 50 === 0) {
          addLog(
            'info',
            `累计发送 ${sentChunkCount} 包，队列余量=${pendingPcm.length}，最近 RMS=${amplifiedRMS.toFixed(4)}`
          );
        }

        try {
          websocket.send(Int16Array.from(chunk).buffer);
        } catch (e: any) {
          addLog('error', `发送失败: ${e?.message || e}`);
        }
      }

      // 若缓冲异常膨胀，记录日志避免卡顿
      if (pendingPcm.length > DEMO_PCM_SAMPLES * 5) {
        addLog('info', `缓冲积压 ${pendingPcm.length} 样本，可能存在发送阻塞`);
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
      // 与官方 FunASR Demo 完全对齐：发送 is_speaking=false 配置消息
      // 官方 demo 在停止时只发送 is_speaking=false，由服务端触发最终的离线纠错
      websocket.send(JSON.stringify({ is_speaking: false }));
      addLog('info', '已发送 is_speaking=false，等待服务端输出最终结果');
      // 保留 legacy end 消息以兼容旧实现
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
    try {
      scriptProcessor.disconnect();
    } catch {}
    scriptProcessor.onaudioprocess = null as any;
    scriptProcessor = null;
  }
  if (audioContext) {
    try {
      if (audioContext.state !== 'closed') audioContext.close();
    } catch {}
    audioContext = null;
  }
  if (mediaStream) {
    try {
      mediaStream.getTracks().forEach(t => t.stop());
    } catch {}
    mediaStream = null;
  }
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
  sentChunkCount = 0;
  pendingPcm = [];
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
  const delay = Math.min(15000, 1000 * 2 ** reconnectAttempts);
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
    try {
      websocket.send(JSON.stringify({ type: 'ping', ts: Date.now() }));
    } catch {}
    // 超时检测：30秒未收到pong，主动关闭以触发重连
    if (Date.now() - lastPongTs > 30000) {
      addLog('error', '心跳超时，断开重连');
      try {
        websocket.close(4000, 'heartbeat timeout');
      } catch {}
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
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

/* Dark theme overrides */
:deep(body[arco-theme='dark']) .voice-identify-container .control-section {
  background: linear-gradient(135deg, var(--color-fill-2) 0%, var(--color-fill-3) 100%);
  border-color: var(--color-border);
}
:deep(body[arco-theme='dark']) .voice-identify-container .recording-status {
  background: var(--color-bg-2);
  border-color: var(--color-border);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}
:deep(body[arco-theme='dark']) .voice-identify-container .main-card {
  border-color: var(--color-border);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
}
:deep(body[arco-theme='dark']) .voice-identify-container .results-card,
:deep(body[arco-theme='dark']) .voice-identify-container .logs-card {
  border-color: var(--color-border);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}
:deep(body[arco-theme='dark']) .voice-identify-container .volume-bar {
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

.identify-tabs {
  margin-bottom: 24px;
}

.identify-tabs :deep(.arco-tabs-nav-tab) {
  font-size: 15px;
  font-weight: 500;
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
