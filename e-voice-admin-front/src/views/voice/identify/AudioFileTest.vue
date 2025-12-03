<template>
  <div class="audio-file-test">
    <!-- 文件拖放区 -->
    <div
      class="drop-zone"
      :class="{ dragover: isDragOver, 'has-file': audioBuffer }"
      @click="triggerFileInput"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
    >
      <div class="drop-icon">{{ audioBuffer ? '📄' : '📁' }}</div>
      <div class="drop-text">
        {{ audioBuffer ? fileName : '拖放音频文件到这里，或点击选择' }}
      </div>
      <div v-if="!audioBuffer" class="drop-hint">支持 WAV, MP3, M4A, FLAC 等格式</div>
      <input ref="fileInputRef" type="file" accept="audio/*" style="display: none" @change="handleFileSelect" />
    </div>

    <!-- 文件信息 -->
    <div v-if="audioBuffer" class="file-info">
      <div class="file-name">{{ fileName }}</div>
      <div class="file-details">
        <span class="detail-item">⏱️ {{ formatTime(fileDuration) }}</span>
        <span class="detail-item">📊 {{ fileSampleRate }} Hz</span>
        <span class="detail-item">📦 {{ (fileSize / 1024).toFixed(1) }} KB</span>
      </div>
    </div>

    <!-- 配置选项 -->
    <div class="config-section">
      <div class="config-row">
        <label>识别模式:</label>
        <ARadioGroup v-model="recognizeMode" :disabled="isStreaming">
          <ARadio value="2pass">2pass (推荐)</ARadio>
          <ARadio value="online">仅在线</ARadio>
          <ARadio value="offline">仅离线</ARadio>
        </ARadioGroup>
      </div>
      <div class="config-row">
        <ACheckbox v-model="enableItn" :disabled="isStreaming">启用 ITN</ACheckbox>
        <label style="margin-left: 16px">帧大小:</label>
        <ASelect v-model="chunkSize" :disabled="isStreaming" style="width: 140px">
          <AOption :value="960">960 (60ms)</AOption>
          <AOption :value="640">640 (40ms)</AOption>
          <AOption :value="1280">1280 (80ms)</AOption>
        </ASelect>
      </div>
      <div class="speed-control">
        <label>发送速度:</label>
        <ASlider v-model="sendSpeed" :min="0.5" :max="10" :step="0.5" :disabled="isStreaming" style="width: 160px" />
        <span class="speed-value">{{ sendSpeed }}x</span>
        <span class="speed-hint">(1x = 实时, >1x = 加速)</span>
      </div>
    </div>

    <!-- 波形显示 -->
    <div ref="waveformRef" class="waveform-container">
      <div class="waveform-position" :style="{ left: `${waveformProgress * 100}%` }"></div>
    </div>

    <!-- 进度条 -->
    <div v-if="isStreaming || progress > 0" class="progress-container">
      <AProgress :percent="Math.round(progress * 100)" :show-text="false" />
      <div class="progress-text">
        <span>{{ formatTime(currentTime) }} / {{ formatTime(fileDuration) }}</span>
        <span>{{ Math.round(progress * 100) }}%</span>
      </div>
    </div>

    <!-- 控制按钮 -->
    <div class="controls">
      <AButton type="primary" :disabled="!audioBuffer || isStreaming" status="success" @click="startStreaming">
        <template #icon><icon-play-arrow /></template>
        开始流式发送
      </AButton>
      <AButton status="danger" :disabled="!isStreaming" @click="stopStreaming">
        <template #icon><icon-record-stop /></template>
        停止
      </AButton>
      <AButton :disabled="isStreaming" @click="resetTest">
        <template #icon><icon-refresh /></template>
        重置
      </AButton>
      <AButton style="margin-left: auto" @click="clearStoredAudio">
        <template #icon><icon-delete /></template>
        清除缓存
      </AButton>
    </div>

    <!-- 统计指标 -->
    <div class="metric-grid">
      <div class="metric-card purple">
        <div class="metric-value">{{ stats.chunksSent }}</div>
        <div class="metric-label">发送帧数</div>
      </div>
      <div class="metric-card green">
        <div class="metric-value">{{ stats.avgLatency > 0 ? stats.avgLatency.toFixed(0) : '-' }}</div>
        <div class="metric-label">响应延迟 (ms)</div>
      </div>
      <div class="metric-card orange">
        <div class="metric-value">{{ (stats.bytesSent / 1024).toFixed(1) }}</div>
        <div class="metric-label">发送字节 (KB)</div>
      </div>
      <div class="metric-card blue">
        <div class="metric-value">{{ stats.partialCount }}</div>
        <div class="metric-label">partial 结果</div>
      </div>
    </div>

    <!-- 识别结果 -->
    <ACard title="🎯 实时识别（在线流式）" class="result-card">
      <div class="result-panel live">
        <template v-if="textState.text_print_2pass_offline || textState.text_print_2pass_online">
          <span v-if="textState.text_print_2pass_online" class="tag-mode tag-online">实时</span>
          <span v-else class="tag-mode tag-offline">已确认</span>
          <span class="text-confirmed">{{ textState.text_print_2pass_offline.slice(-100) }}</span>
          <span v-if="textState.text_print_2pass_online" class="text-candidate">
            {{ textState.text_print_2pass_online }}
          </span>
        </template>
        <em v-else class="placeholder">{{ isStreaming ? '接收中...' : '等待开始...' }}</em>
      </div>
    </ACard>

    <ACard title="📝 会议纪要（语义分段）" class="result-card">
      <div class="result-panel final">
        <ul v-if="semanticSegments.length || textState.text_print_2pass_online" class="segment-list">
          <li v-for="(segment, index) in semanticSegments" :key="index" class="segment-item">
            <span class="segment-number">{{ index + 1 }}</span>
            {{ segment }}
          </li>
          <li v-if="textState.text_print_2pass_online" class="segment-item segment-pending">
            <span class="segment-number">⏳</span>
            {{ textState.text_print_2pass_online }}
          </li>
        </ul>
        <em v-else class="placeholder">等待离线纠错结果...</em>
      </div>
    </ACard>

    <!-- 事件日志 -->
    <ACard class="log-card">
      <template #title>
        <div class="log-header">
          <span>
            <icon-file-text />
            事件日志
          </span>
          <ASpace>
            <ACheckbox v-model="autoScroll">自动滚动</ACheckbox>
            <AButton size="small" @click="clearLog">清空日志</AButton>
          </ASpace>
        </div>
      </template>
      <div ref="logBoxRef" class="log-box">
        <div v-for="(log, index) in logs" :key="index" class="log-line" :class="[`log-${log.level}`]">
          [{{ log.time }}] {{ log.message }}
        </div>
      </div>
    </ACard>
  </div>
</template>

<script lang="ts" setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue';

const SAMPLE_RATE = 16000;
const STORAGE_KEY = 'evoice_last_audio';
const MAX_STORAGE_SIZE = 5 * 1024 * 1024;

// WebSocket 配置
const wsHost = (import.meta as any).env.VITE_API_PY_WS_HOST || 'ws://localhost:8210';

// 文件输入引用
const fileInputRef = ref<HTMLInputElement | null>(null);
const waveformRef = ref<HTMLElement | null>(null);
const logBoxRef = ref<HTMLElement | null>(null);

// 状态
const isDragOver = ref(false);
const audioBuffer = ref<AudioBuffer | null>(null);
const pcmData = ref<ArrayBuffer | null>(null);
const fileName = ref('');
const fileDuration = ref(0);
const fileSampleRate = ref(0);
const fileSize = ref(0);

// 配置
const recognizeMode = ref('2pass');
const enableItn = ref(true);
const chunkSize = ref(960);
const sendSpeed = ref(1);

// 流式状态
const isStreaming = ref(false);
const progress = ref(0);
const currentTime = ref(0);
const waveformProgress = ref(0);

// 统计
const stats = reactive({
  chunksSent: 0,
  bytesSent: 0,
  partialCount: 0,
  latencies: [] as number[],
  avgLatency: 0,
  lastSendTime: 0
});

// 文本状态
const textState = reactive({
  text_print_2pass_online: '',
  text_print_2pass_offline: ''
});

// 语义分段
const semanticSegments = computed(() => {
  if (!textState.text_print_2pass_offline) return [];
  return splitByPunctuation(textState.text_print_2pass_offline);
});

// 日志
const logs = ref<Array<{ time: string; level: string; message: string }>>([]);
const autoScroll = ref(true);

// WebSocket 和定时器
let websocket: WebSocket | null = null;
let streamingInterval: ReturnType<typeof setInterval> | null = null;
let audioContext: AudioContext | null = null;

// 工具函数
function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function splitByPunctuation(text: string): string[] {
  const pattern = /([。！？!?]+)/g;
  const parts = text.split(pattern);
  const segments: string[] = [];
  let current = '';
  for (const part of parts) {
    if (/^[。！？!?]+$/.test(part)) {
      current += part;
      if (current.trim()) {
        segments.push(current.trim());
      }
      current = '';
    } else {
      current += part;
    }
  }
  if (current.trim()) {
    segments.push(current.trim());
  }
  return segments;
}

function addLog(level: 'info' | 'success' | 'warning' | 'error', message: string) {
  const time = new Date().toLocaleTimeString();
  logs.value.push({ time, level, message });
  if (autoScroll.value && logBoxRef.value) {
    nextTick(() => {
      if (logBoxRef.value) {
        logBoxRef.value.scrollTop = logBoxRef.value.scrollHeight;
      }
    });
  }
}

function clearLog() {
  logs.value = [];
  addLog('info', '日志已清空');
}

// 文件处理
function triggerFileInput() {
  fileInputRef.value?.click();
}

function handleDragOver() {
  isDragOver.value = true;
}

function handleDragLeave() {
  isDragOver.value = false;
}

function handleDrop(e: DragEvent) {
  isDragOver.value = false;
  const files = e.dataTransfer?.files;
  if (files && files.length > 0 && files[0].type.startsWith('audio/')) {
    loadAudioFile(files[0]);
  } else {
    addLog('error', '请拖放音频文件');
  }
}

function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0];
  if (file) {
    loadAudioFile(file);
  }
}

async function loadAudioFile(file: File, arrayBuffer?: ArrayBuffer) {
  addLog('info', `加载文件: ${file.name}`);

  try {
    if (!audioContext) {
      audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    }

    const buffer = arrayBuffer || (await file.arrayBuffer());

    // 保存到本地存储
    if (!arrayBuffer && buffer.byteLength <= MAX_STORAGE_SIZE) {
      saveAudioToStorage(file, buffer);
    }

    // 解码音频
    const decoded = await audioContext.decodeAudioData(buffer.slice(0));
    audioBuffer.value = decoded;

    // 转换为 PCM
    pcmData.value = convertToPCM(decoded);

    // 更新文件信息
    fileName.value = file.name;
    fileDuration.value = decoded.duration;
    fileSampleRate.value = decoded.sampleRate;
    fileSize.value = pcmData.value.byteLength;

    // 绘制波形
    drawWaveform(pcmData.value);

    addLog(
      'success',
      `音频加载完成: ${decoded.duration.toFixed(2)}s, ${(pcmData.value.byteLength / 1024).toFixed(1)}KB`
    );
  } catch (e: any) {
    addLog('error', `加载失败: ${e.message}`);
  }
}

function convertToPCM(buffer: AudioBuffer): ArrayBuffer {
  let channelData = buffer.getChannelData(0);

  // 重采样到 16kHz
  if (buffer.sampleRate !== SAMPLE_RATE) {
    const ratio = SAMPLE_RATE / buffer.sampleRate;
    const newLength = Math.floor(channelData.length * ratio);
    const resampled = new Float32Array(newLength);

    for (let i = 0; i < newLength; i++) {
      const srcIndex = i / ratio;
      const srcIndexFloor = Math.floor(srcIndex);
      const srcIndexCeil = Math.min(srcIndexFloor + 1, channelData.length - 1);
      const t = srcIndex - srcIndexFloor;
      resampled[i] = channelData[srcIndexFloor] * (1 - t) + channelData[srcIndexCeil] * t;
    }
    channelData = resampled;
  }

  // 转换为 Int16
  const pcm = new Int16Array(channelData.length);
  for (let i = 0; i < channelData.length; i++) {
    const s = Math.max(-1, Math.min(1, channelData[i]));
    pcm[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }

  return pcm.buffer;
}

function drawWaveform(pcmBuffer: ArrayBuffer) {
  const container = waveformRef.value;
  if (!container) return;

  const width = container.offsetWidth;
  const numBars = Math.min(200, width / 3);

  // 清除旧波形
  const oldBars = container.querySelectorAll('.waveform-bar');
  oldBars.forEach(bar => bar.remove());

  const samples = new Int16Array(pcmBuffer);
  const samplesPerBar = Math.floor(samples.length / numBars);

  for (let i = 0; i < numBars; i++) {
    let sum = 0;
    for (let j = 0; j < samplesPerBar; j++) {
      sum += Math.abs(samples[i * samplesPerBar + j] || 0);
    }
    const avg = sum / samplesPerBar / 32768;
    const height = Math.max(2, avg * 55);

    const bar = document.createElement('div');
    bar.className = 'waveform-bar';
    bar.style.left = `${(i / numBars) * 100}%`;
    bar.style.height = `${height}px`;
    container.appendChild(bar);
  }
}

// 本地存储
function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

function base64ToArrayBuffer(base64: string): ArrayBuffer {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}

function saveAudioToStorage(file: File, arrayBuffer: ArrayBuffer) {
  try {
    const base64 = arrayBufferToBase64(arrayBuffer);
    const audioData = {
      name: file.name,
      type: file.type || 'audio/wav',
      size: arrayBuffer.byteLength,
      data: base64,
      savedAt: Date.now()
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(audioData));
    addLog('info', `音频已保存到本地存储: ${file.name}`);
  } catch (e: any) {
    addLog('warning', `保存到本地存储失败: ${e.message}`);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {}
  }
}

function loadAudioFromStorage() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return null;

    const audioData = JSON.parse(stored);
    if (!audioData.data || !audioData.name) return null;

    const arrayBuffer = base64ToArrayBuffer(audioData.data);
    return {
      name: audioData.name,
      type: audioData.type,
      size: audioData.size,
      arrayBuffer,
      savedAt: audioData.savedAt
    };
  } catch (e: any) {
    addLog('warning', `从本地存储加载失败: ${e.message}`);
    return null;
  }
}

function clearStoredAudio() {
  try {
    localStorage.removeItem(STORAGE_KEY);
    addLog('info', '已清除本地存储的音频');
  } catch {}
}

// WebSocket 流式发送
async function startStreaming() {
  if (!pcmData.value) {
    addLog('error', '请先选择音频文件');
    return;
  }

  if (isStreaming.value) {
    addLog('warning', '已在发送中');
    return;
  }

  const wsUrl = `${wsHost}/ws/recognize`;
  addLog('info', `连接到: ${wsUrl}`);

  try {
    websocket = new WebSocket(wsUrl);
    websocket.binaryType = 'arraybuffer';

    websocket.onopen = () => {
      addLog('success', 'WebSocket 连接成功');
      beginStreaming();
    };

    websocket.onmessage = event => {
      handleMessage(JSON.parse(event.data));
    };

    websocket.onerror = () => {
      addLog('error', 'WebSocket 错误');
    };

    websocket.onclose = e => {
      addLog('warning', `连接关闭: code=${e.code}`);
      stopStreaming();
    };
  } catch (e: any) {
    addLog('error', `连接失败: ${e.message}`);
  }
}

function beginStreaming() {
  isStreaming.value = true;

  // 重置统计
  stats.chunksSent = 0;
  stats.bytesSent = 0;
  stats.partialCount = 0;
  stats.latencies = [];
  stats.avgLatency = 0;
  stats.lastSendTime = 0;

  // 重置文本状态
  textState.text_print_2pass_online = '';
  textState.text_print_2pass_offline = '';

  // 发送配置
  const config = {
    chunk_size: [5, 10, 5],
    chunk_interval: 10,
    wav_name: 'file-test',
    is_speaking: true,
    mode: recognizeMode.value,
    itn: enableItn.value,
    sample_rate: SAMPLE_RATE
  };
  websocket?.send(JSON.stringify(config));
  addLog('info', `发送配置: mode=${recognizeMode.value}`);

  // 开始流式发送
  const chunkBytes = chunkSize.value * 2;
  const intervalMs = ((chunkSize.value / SAMPLE_RATE) * 1000) / sendSpeed.value;

  const pcmArray = new Uint8Array(pcmData.value!);
  const totalChunks = Math.ceil(pcmArray.length / chunkBytes);
  let currentChunk = 0;

  addLog('info', `开始发送: ${totalChunks} 帧, 间隔 ${intervalMs.toFixed(1)}ms, 速度 ${sendSpeed.value}x`);

  streamingInterval = setInterval(() => {
    if (!isStreaming.value || !websocket || websocket.readyState !== WebSocket.OPEN) {
      stopStreaming();
      return;
    }

    if (currentChunk >= totalChunks) {
      // 发送停止信号
      const stopMsg = {
        is_speaking: false,
        mode: recognizeMode.value
      };
      websocket.send(JSON.stringify(stopMsg));
      addLog('info', '发送完成，等待最终结果...');

      if (streamingInterval) {
        clearInterval(streamingInterval);
        streamingInterval = null;
      }

      // 等待最终结果后关闭
      setTimeout(() => {
        if (websocket && websocket.readyState === WebSocket.OPEN) {
          websocket.close(1000, 'streaming complete');
        }
        stopStreaming();
      }, 3000);
      return;
    }

    // 发送音频块
    const start = currentChunk * chunkBytes;
    const end = Math.min(start + chunkBytes, pcmArray.length);
    const chunk = pcmArray.slice(start, end);

    stats.lastSendTime = Date.now();
    websocket.send(chunk.buffer);

    stats.chunksSent++;
    stats.bytesSent += chunk.length;
    currentChunk++;

    // 更新进度
    progress.value = currentChunk / totalChunks;
    currentTime.value = (currentChunk * chunkSize.value) / SAMPLE_RATE;
    waveformProgress.value = progress.value;
  }, intervalMs);
}

function stopStreaming() {
  isStreaming.value = false;

  if (streamingInterval) {
    clearInterval(streamingInterval);
    streamingInterval = null;
  }

  addLog('info', `发送结束: ${stats.chunksSent} 帧, ${(stats.bytesSent / 1024).toFixed(1)} KB`);
}

function handleMessage(data: any) {
  // 计算延迟
  if (stats.lastSendTime > 0) {
    const latency = Date.now() - stats.lastSendTime;
    stats.latencies.push(latency);
    if (stats.latencies.length > 50) stats.latencies.shift();
    stats.avgLatency = stats.latencies.reduce((a, b) => a + b, 0) / stats.latencies.length;
  }

  const mode = data.mode || '';
  const text = data.text || '';
  const type = data.type || '';

  // 参考 FunASR 处理逻辑
  if (mode === 'online') {
    textState.text_print_2pass_online += text;
  } else if (mode === 'offline') {
    textState.text_print_2pass_offline += text;
  } else if (mode === '2pass-online') {
    stats.partialCount++;
    textState.text_print_2pass_online += text;
  } else if (mode === '2pass-offline') {
    textState.text_print_2pass_online = '';
    textState.text_print_2pass_offline += text;
  }

  if (type === 'error') {
    addLog('error', data.message || '未知错误');
  }

  if (text) {
    addLog('info', `[${mode || type}] ${text.substring(0, 50)}${text.length > 50 ? '...' : ''}`);
  }
}

function resetTest() {
  stopStreaming();
  if (websocket) {
    websocket.close();
    websocket = null;
  }

  stats.chunksSent = 0;
  stats.bytesSent = 0;
  stats.partialCount = 0;
  stats.latencies = [];
  stats.avgLatency = 0;
  stats.lastSendTime = 0;

  textState.text_print_2pass_online = '';
  textState.text_print_2pass_offline = '';

  progress.value = 0;
  currentTime.value = 0;
  waveformProgress.value = 0;

  addLog('info', '测试已重置');
}

// 生命周期
onMounted(async () => {
  addLog('info', '页面初始化完成');

  // 尝试加载上次保存的音频
  const storedAudio = loadAudioFromStorage();
  if (storedAudio) {
    const savedTime = new Date(storedAudio.savedAt).toLocaleString();
    addLog('info', `发现上次保存的音频: ${storedAudio.name} (保存于 ${savedTime})`);

    try {
      const file = {
        name: storedAudio.name,
        type: storedAudio.type,
        size: storedAudio.size
      } as File;
      await loadAudioFile(file, storedAudio.arrayBuffer);
      addLog('success', '已自动加载上次的音频文件');
    } catch (e: any) {
      addLog('warning', `加载上次音频失败: ${e.message}`);
      clearStoredAudio();
    }
  }
});

onBeforeUnmount(() => {
  stopStreaming();
  if (websocket) {
    websocket.close(1001, 'page unload');
  }
});
</script>

<style scoped>
.audio-file-test {
  padding: 16px;
}

.drop-zone {
  border: 3px dashed var(--color-border-2);
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  background: linear-gradient(135deg, var(--color-fill-1) 0%, var(--color-fill-2) 100%);
  transition: all 0.3s ease;
  cursor: pointer;
  margin-bottom: 20px;
}

.drop-zone:hover,
.drop-zone.dragover {
  border-color: rgb(var(--primary-6));
  background: linear-gradient(135deg, rgb(var(--primary-1)) 0%, rgb(var(--primary-2)) 100%);
}

.drop-zone.has-file {
  border-color: rgb(var(--success-6));
  background: linear-gradient(135deg, rgb(var(--success-1)) 0%, rgb(var(--success-2)) 100%);
}

.drop-icon {
  font-size: 3rem;
  margin-bottom: 12px;
}

.drop-text {
  font-size: 1.1rem;
  color: var(--color-text-2);
}

.drop-hint {
  font-size: 0.85rem;
  color: var(--color-text-3);
  margin-top: 8px;
}

.file-info {
  background: var(--color-fill-2);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 20px;
}

.file-name {
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 8px;
}

.file-details {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  font-size: 0.9rem;
  color: var(--color-text-2);
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.config-section {
  background: var(--color-fill-1);
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 20px;
}

.config-row {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.config-row label {
  font-size: 0.9rem;
  color: var(--color-text-2);
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

.speed-value {
  min-width: 40px;
  text-align: center;
  font-weight: 600;
  color: rgb(var(--primary-6));
}

.speed-hint {
  font-size: 0.85rem;
  color: var(--color-text-3);
}

.waveform-container {
  height: 60px;
  background: var(--color-fill-4);
  border-radius: 6px;
  margin-bottom: 12px;
  position: relative;
  overflow: hidden;
}

.waveform-bar {
  position: absolute;
  bottom: 0;
  width: 2px;
  background: rgb(var(--primary-6));
  border-radius: 1px 1px 0 0;
  transition: height 0.05s ease;
}

.waveform-position {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  background: rgb(var(--warning-6));
  z-index: 10;
}

.progress-container {
  margin-bottom: 16px;
}

.progress-text {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: var(--color-text-2);
  margin-top: 8px;
}

.controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.metric-card {
  padding: 14px;
  border-radius: 10px;
  color: white;
  text-align: center;
}

.metric-card.purple {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.metric-card.green {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.metric-card.orange {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.metric-card.blue {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.metric-value {
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: 4px;
}

.metric-label {
  font-size: 0.8rem;
  opacity: 0.9;
}

.result-card {
  margin-bottom: 16px;
}

.result-panel {
  min-height: 80px;
  padding: 16px;
  border-radius: 10px;
  font-size: 1.05rem;
  line-height: 1.7;
}

.result-panel.live {
  border: 2px solid rgb(var(--primary-6));
  background: linear-gradient(to bottom, rgb(var(--primary-1)), var(--color-bg-1));
}

.result-panel.final {
  border: 2px solid rgb(var(--success-6));
  background: linear-gradient(to bottom, rgb(var(--success-1)), var(--color-bg-1));
  max-height: 400px;
  overflow-y: auto;
}

.tag-mode {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  margin-right: 6px;
}

.tag-online {
  background: rgb(var(--primary-2));
  color: rgb(var(--primary-6));
}

.tag-offline {
  background: rgb(var(--success-2));
  color: rgb(var(--success-6));
}

.text-confirmed {
  color: rgb(var(--success-6));
}

.text-candidate {
  color: rgb(var(--primary-6));
  font-style: italic;
}

.placeholder {
  color: var(--color-text-3);
}

.segment-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.segment-item {
  padding: 8px 12px;
  margin-bottom: 8px;
  border-radius: 6px;
  background: var(--color-fill-2);
  border-left: 3px solid rgb(var(--success-6));
  font-size: 0.95rem;
  line-height: 1.6;
}

.segment-item:last-child {
  margin-bottom: 0;
}

.segment-number {
  display: inline-block;
  min-width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
  background: rgb(var(--success-6));
  color: white;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 600;
  margin-right: 8px;
}

.segment-pending {
  border-left-color: rgb(var(--warning-6));
  background: rgb(var(--warning-1));
}

.segment-pending .segment-number {
  background: rgb(var(--warning-6));
}

.log-card {
  margin-top: 20px;
}

.log-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.log-box {
  height: 180px;
  overflow-y: auto;
  font-family: 'Menlo', 'Consolas', monospace;
  font-size: 0.8rem;
  background: #1e293b;
  color: #e2e8f0;
  padding: 12px;
  border-radius: 8px;
}

.log-line {
  margin-bottom: 2px;
}

.log-info {
  color: #93c5fd;
}

.log-success {
  color: #86efac;
}

.log-warning {
  color: #fcd34d;
}

.log-error {
  color: #fca5a5;
}

/* 响应式 */
@media (max-width: 768px) {
  .config-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .controls {
    flex-wrap: wrap;
  }

  .metric-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
