<template>
  <div class="container">
    <Breadcrumb :items="['会议管理', 'MDT会议', '会议详情']" />

    <!-- 顶部操作栏 -->
    <div class="back-bar">
      <AButton @click="goBack">
        <template #icon><icon-left /></template>
        返回列表
      </AButton>
      <ASpace style="margin-left: auto">
        <!-- 实时录音按钮 -->
        <AButton
          v-if="meeting?.status !== 2"
          :type="recording ? 'outline' : 'primary'"
          :status="recording ? 'danger' : 'normal'"
          :loading="connecting"
          @click="toggleRecording"
        >
          <template #icon>
            <icon-record v-if="!recording" />
            <icon-record-stop v-if="recording" />
          </template>
          {{ recording ? '停止录音' : '开始录音' }}
        </AButton>
        <AButton v-if="meeting?.status === 0" type="primary" @click="handleStartMeeting">开始会议</AButton>
        <AButton v-if="meeting?.status === 1" status="warning" @click="handleEndMeeting">结束会议</AButton>
      </ASpace>
    </div>

    <!-- 会议基本信息 -->
    <ACard class="general-card" title="会议信息" :loading="loading">
      <ADescriptions :column="3" bordered>
        <ADescriptionsItem label="会议标题">{{ meeting?.title || '-' }}</ADescriptionsItem>
        <ADescriptionsItem label="主持人">{{ meeting?.hostName || '-' }}</ADescriptionsItem>
        <ADescriptionsItem label="状态">
          <ATag :color="meetingStatusMap[meeting?.status]?.color || 'gray'">
            {{ meetingStatusMap[meeting?.status]?.text || '未知' }}
          </ATag>
        </ADescriptionsItem>
        <ADescriptionsItem label="开始时间">{{ meeting?.startTime || '-' }}</ADescriptionsItem>
        <ADescriptionsItem label="结束时间">{{ meeting?.endTime || '-' }}</ADescriptionsItem>
        <ADescriptionsItem label="对话数">{{ meeting?.dialogCount || 0 }}</ADescriptionsItem>
        <ADescriptionsItem label="会议说明" :span="3">
          {{ meeting?.description || '-' }}
        </ADescriptionsItem>
        <ADescriptionsItem label="标签" :span="3">
          <ASpace v-if="meeting?.tagList?.length">
            <ATag v-for="tag in meeting.tagList" :key="tag" color="arcoblue">{{ tag }}</ATag>
          </ASpace>
          <span v-else>-</span>
        </ADescriptionsItem>
      </ADescriptions>
    </ACard>

    <!-- 音频文件上传测试 -->
    <AudioFileUpload
      :meeting-id="meetingId"
      @dialog-received="handleFileDialogReceived"
    />

    <!-- 内容区域 -->
    <ARow :gutter="16" style="margin-top: 16px">
      <!-- 对话记录 -->
      <ACol :span="14">
        <ACard class="general-card dialog-card" title="会议语音识别记录">
          <template #extra>
            <AButton size="small" @click="copyDialogs">
              <template #icon><icon-copy /></template>
              复制文字记录
            </AButton>
          </template>

          <!-- 实时识别预览 -->
          <div v-if="recording || runningText" class="realtime-preview">
            <div class="realtime-header">
              <span class="realtime-dot" :class="{ active: recording }"></span>
              <span>{{ recording ? '正在识别...' : '识别预览' }}</span>
            </div>
            <div class="realtime-text">{{ runningText || '等待语音输入...' }}</div>
          </div>

          <!-- 错误提示 -->
          <AAlert v-if="recordingError" type="error" :content="recordingError" closable style="margin-bottom: 16px" />

          <div v-if="meeting?.dialogs?.length" class="dialog-list">
            <div v-for="dialog in meeting.dialogs" :key="dialog.id || dialog.seq" class="dialog-item">
              <div class="dialog-meta">
                <span class="time">{{ formatTime(dialog.speakTime) }}</span>
                <!-- 时间偏移显示 -->
                <span v-if="dialog.startOffset || dialog.endOffset" class="time-offset">
                  [{{ formatOffsetTime(dialog.startOffset) }} - {{ formatOffsetTime(dialog.endOffset) }}]
                </span>
                <ATag v-if="dialog.recognized" :color="recognizedStatusMap[dialog.recognized]?.color">
                  {{ dialog.speakerName }}
                </ATag>
                <AButton v-else size="mini" type="outline" @click="openAssignModal(dialog)">
                  <template #icon><icon-plus /></template>
                  指定发言人
                </AButton>
                <span class="role">{{ dialog.speakerRole || '角色待标注' }}</span>
                <span class="recognition-note">{{ dialog.recognitionNote }}</span>
              </div>
              <!-- 文本显示/编辑 -->
              <div v-if="editingDialogId !== dialog.id" class="dialog-text" @dblclick="startEditDialog(dialog)">
                {{ dialog.text }}
                <AButton class="edit-btn" size="mini" type="text" @click="startEditDialog(dialog)">
                  <template #icon><icon-edit /></template>
                </AButton>
              </div>
              <div v-else class="dialog-edit">
                <ATextarea v-model="editingText" :auto-size="{ minRows: 2 }" placeholder="编辑识别文本" />
                <div class="edit-actions">
                  <AButton size="mini" type="primary" @click="saveDialogText(dialog)">保存</AButton>
                  <AButton size="mini" @click="cancelEditDialog">取消</AButton>
                </div>
              </div>
              <!-- 音频播放 -->
              <div v-if="dialog.audioPath" class="audio-action">
                <audio :src="dialog.audioPath" controls preload="metadata" />
              </div>
            </div>
          </div>
          <AEmpty v-else description="暂无语音识别结果" />
        </ACard>
      </ACol>

      <!-- AI总结 -->
      <ACol :span="10">
        <ACard class="general-card summary-card" title="AI会议总结">
          <template #extra>
            <AButton size="small" :disabled="!meeting?.summary" @click="copySummary">
              <template #icon><icon-copy /></template>
              复制总结
            </AButton>
          </template>
          <div class="summary-controls">
            <AButton
              type="primary"
              :loading="summaryLoading"
              :disabled="meeting?.summaryStatus === 1"
              @click="handleGenerateSummary"
            >
              <template #icon><icon-robot /></template>
              一键生成总结
            </AButton>
            <span class="summary-hint">
              {{ summaryStatusMap[meeting?.summaryStatus]?.text || '点击按钮生成AI总结' }}
            </span>
          </div>
          <div v-if="meeting?.summary" class="summary-content">
            <pre>{{ meeting.summary }}</pre>
          </div>
          <AEmpty v-else description="暂无会议总结，请点击上方按钮生成" />
        </ACard>
      </ACol>
    </ARow>

    <!-- 指定发言人弹窗 -->
    <AModal
      v-model:visible="assignModalVisible"
      title="指定发言人"
      :width="500"
      @ok="handleAssignSpeaker"
      @cancel="assignModalVisible = false"
    >
      <AForm :model="assignForm">
        <AFormItem label="搜索">
          <AInput v-model="assignForm.keyword" placeholder="输入姓名或科室搜索" allow-clear />
        </AFormItem>
        <div class="staff-list">
          <div
            v-for="staff in filteredStaffList"
            :key="staff.userId"
            class="staff-item"
            :class="{ active: assignForm.speakerId === staff.userId }"
            @click="selectStaff(staff)"
          >
            <div class="staff-main">
              <strong>{{ staff.userName }}</strong>
              <span>{{ staff.role }} · {{ staff.department }}</span>
            </div>
            <ATag v-if="assignForm.speakerId === staff.userId" color="arcoblue">已选择</ATag>
          </div>
          <AEmpty v-if="!filteredStaffList.length" description="未找到匹配人员" />
        </div>
      </AForm>
    </AModal>
  </div>
</template>

<script lang="ts" setup>
import { useRoute, useRouter } from 'vue-router';
import { Message } from '@arco-design/web-vue';
import useLoading from '@/hooks/loading';
import { meetingStatusMap, recognizedStatusMap, summaryStatusMap } from './data';
import { assignSpeaker, endMeeting, generateSummary, getDetail, startMeeting, updateDialog } from './api';
import type { MeetingDetail, MeetingDialog, Participant } from './api/types';
import { useRecording } from './composables/useRecording';
import AudioFileUpload from './components/AudioFileUpload.vue';

// 编辑对话文本
const editingDialogId = ref<number | null>(null);
const editingText = ref('');

const route = useRoute();
const router = useRouter();

const { loading, setLoading } = useLoading(true);
const { loading: summaryLoading, setLoading: setSummaryLoading } = useLoading(false);

const meeting = ref<MeetingDetail | null>(null);
const assignModalVisible = ref(false);
const currentDialog = ref<MeetingDialog | null>(null);

// 实时录音
const meetingId = computed(() => Number(route.query.id) || 0);
const {
  recording,
  connecting,
  errorMsg: recordingError,
  runningText,
  toggleRecording,
  cleanup: cleanupRecording
} = useRecording({
  meetingId: meetingId.value,
  onDialogReceived: dialog => {
    // 实时添加到对话列表
    if (meeting.value) {
      meeting.value.dialogs = [...(meeting.value.dialogs || []), dialog as MeetingDialog];
      meeting.value.dialogCount = meeting.value.dialogs.length;
    }
  }
});

// 处理文件上传测试的对话
const handleFileDialogReceived = (dialog: Partial<MeetingDialog>) => {
  if (meeting.value) {
    meeting.value.dialogs = [...(meeting.value.dialogs || []), dialog as MeetingDialog];
    meeting.value.dialogCount = meeting.value.dialogs.length;
  }
};

// 指定发言人表单
const assignForm = reactive({
  keyword: '',
  speakerId: 0,
  speakerName: '',
  speakerRole: ''
});

// 模拟人员列表（实际应该从后端获取）
const staffList = ref<Participant[]>([
  { userId: 1, userName: '张主任', department: '呼吸与危重症医学科', role: '科室主任' },
  { userId: 2, userName: '王专家', department: '影像科', role: '主任医师' },
  { userId: 3, userName: '刘医生', department: '重症医学科', role: '主治医师' },
  { userId: 4, userName: '李护士长', department: '呼吸治疗护理组', role: '护理组长' },
  { userId: 5, userName: '陈教授', department: '胸外科特聘专家', role: '特聘教授' }
]);

// 过滤人员列表
const filteredStaffList = computed(() => {
  const keyword = assignForm.keyword.toLowerCase();
  if (!keyword) return staffList.value;
  return staffList.value.filter(
    s =>
      s.userName.toLowerCase().includes(keyword) ||
      s.department.toLowerCase().includes(keyword) ||
      s.role.toLowerCase().includes(keyword)
  );
});

// 获取会议详情
const fetchData = async () => {
  const id = route.query.id as string;
  if (!id) {
    Message.error('缺少会议ID');
    return;
  }

  setLoading(true);
  try {
    const data = await getDetail(Number(id));
    meeting.value = data;
  } catch (error) {
    Message.error('获取会议详情失败');
  } finally {
    setLoading(false);
  }
};

// 返回列表
const goBack = () => {
  router.push('/meeting/mdt');
};

// 格式化时间
const formatTime = (time: string) => {
  if (!time) return '-';
  return time.split(' ')[1] || time;
};

// 格式化时间偏移（毫秒转 mm:ss 格式）
const formatOffsetTime = (offsetMs: number | undefined) => {
  if (!offsetMs && offsetMs !== 0) return '--:--';
  const totalSeconds = Math.floor(offsetMs / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
};

// 开始编辑对话
const startEditDialog = (dialog: MeetingDialog) => {
  if (!dialog.id) {
    Message.warning('此对话记录尚未保存，无法编辑');
    return;
  }
  editingDialogId.value = dialog.id;
  editingText.value = dialog.text;
};

// 取消编辑
const cancelEditDialog = () => {
  editingDialogId.value = null;
  editingText.value = '';
};

// 保存对话文本
const saveDialogText = async (dialog: MeetingDialog) => {
  if (!dialog.id || !editingText.value.trim()) {
    Message.warning('文本不能为空');
    return;
  }
  
  try {
    await updateDialog(dialog.id, editingText.value.trim());
    Message.success('保存成功');
    // 更新本地数据
    dialog.text = editingText.value.trim();
    cancelEditDialog();
  } catch (error) {
    Message.error('保存失败');
  }
};

// 复制对话记录
const copyDialogs = () => {
  if (!meeting.value?.dialogs?.length) {
    Message.warning('暂无对话记录');
    return;
  }
  const text = meeting.value.dialogs.map(d => `[${d.speakTime}] ${d.speakerName}: ${d.text}`).join('\n');
  navigator.clipboard.writeText(text);
  Message.success('已复制到剪贴板');
};

// 复制总结
const copySummary = () => {
  if (!meeting.value?.summary) {
    Message.warning('暂无总结');
    return;
  }
  navigator.clipboard.writeText(meeting.value.summary);
  Message.success('已复制到剪贴板');
};

// 生成AI总结
const handleGenerateSummary = async () => {
  if (!meeting.value?.id) return;

  setSummaryLoading(true);
  try {
    await generateSummary(meeting.value.id);
    Message.success('AI正在生成总结，请稍后刷新查看');
    // 轮询检查状态
    checkSummaryStatus();
  } catch (error) {
    Message.error('生成总结失败');
  } finally {
    setSummaryLoading(false);
  }
};

// 轮询检查总结状态
const checkSummaryStatus = () => {
  const timer = setInterval(async () => {
    if (!meeting.value?.id) {
      clearInterval(timer);
      return;
    }
    await fetchData();
    if (meeting.value?.summaryStatus !== 1) {
      clearInterval(timer);
      if (meeting.value?.summaryStatus === 2) {
        Message.success('总结生成完成');
      }
    }
  }, 3000);
};

// 打开指定发言人弹窗
const openAssignModal = (dialog: MeetingDialog) => {
  // 检查 dialog 是否已保存到数据库
  if (!dialog.id) {
    Message.warning('此对话记录尚未保存，请先刷新页面');
    return;
  }
  currentDialog.value = dialog;
  assignForm.keyword = '';
  assignForm.speakerId = 0;
  assignForm.speakerName = '';
  assignForm.speakerRole = '';
  assignModalVisible.value = true;
};

// 选择人员
const selectStaff = (staff: Participant) => {
  assignForm.speakerId = staff.userId;
  assignForm.speakerName = staff.userName;
  assignForm.speakerRole = `${staff.department} · ${staff.role}`;
};

// 确认指定发言人
const handleAssignSpeaker = async () => {
  if (!currentDialog.value || !assignForm.speakerId) {
    Message.warning('请选择发言人');
    return;
  }

  try {
    await assignSpeaker({
      dialogId: currentDialog.value.id,
      speakerId: assignForm.speakerId,
      speakerName: assignForm.speakerName,
      speakerRole: assignForm.speakerRole
    });
    Message.success('指定成功');
    assignModalVisible.value = false;
    fetchData();
  } catch (error) {
    Message.error('指定失败');
  }
};

// 开始会议
const handleStartMeeting = async () => {
  if (!meeting.value?.id) return;
  try {
    await startMeeting(meeting.value.id);
    Message.success('会议已开始');
    fetchData();
  } catch (error) {
    Message.error('操作失败');
  }
};

// 结束会议
const handleEndMeeting = async () => {
  if (!meeting.value?.id) return;
  // 先停止录音
  if (recording.value) {
    toggleRecording();
  }
  try {
    await endMeeting(meeting.value.id);
    Message.success('会议已结束');
    fetchData();
  } catch (error) {
    Message.error('操作失败');
  }
};

// 初始化
onMounted(() => {
  fetchData();
});

// 清理
onUnmounted(() => {
  cleanupRecording();
});
</script>

<style scoped lang="less">
.container {
  padding: 16px;
}

.back-bar {
  margin-bottom: 16px;
}

.dialog-card {
  height: calc(100vh - 350px);
  overflow: hidden;
  display: flex;
  flex-direction: column;

  :deep(.arco-card-body) {
    flex: 1;
    overflow: auto;
  }
}

.dialog-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dialog-item {
  border: 1px solid var(--color-border-2);
  border-radius: 8px;
  padding: 16px;
  background: var(--color-fill-1);
}

.dialog-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
  color: var(--color-text-3);

  .time {
    font-weight: 500;
    color: var(--color-text-2);
  }

  .role {
    color: var(--color-text-3);
  }

  .recognition-note {
    font-size: 12px;
    color: var(--color-text-4);
  }

  .time-offset {
    font-family: monospace;
    font-size: 12px;
    color: rgb(var(--primary-6));
    background: var(--color-fill-2);
    padding: 2px 6px;
    border-radius: 4px;
  }
}

.dialog-text {
  font-size: 15px;
  line-height: 1.7;
  color: var(--color-text-1);
  position: relative;
  cursor: text;
  padding-right: 30px;

  &:hover .edit-btn {
    opacity: 1;
  }

  .edit-btn {
    position: absolute;
    right: 0;
    top: 0;
    opacity: 0;
    transition: opacity 0.2s;
  }
}

.dialog-edit {
  .edit-actions {
    margin-top: 8px;
    display: flex;
    gap: 8px;
  }
}

.audio-action {
  margin-top: 8px;

  audio {
    height: 32px;
    width: 100%;
    max-width: 300px;
  }
}

.summary-card {
  height: calc(100vh - 350px);
  overflow: hidden;
  display: flex;
  flex-direction: column;

  :deep(.arco-card-body) {
    flex: 1;
    overflow: auto;
  }
}

.summary-controls {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  border-radius: 8px;
  background: var(--color-fill-2);
  margin-bottom: 16px;

  .summary-hint {
    font-size: 12px;
    color: var(--color-text-3);
  }
}

.summary-content {
  pre {
    margin: 0;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: inherit;
    font-size: 14px;
    line-height: 1.8;
    color: var(--color-text-1);
  }
}

.staff-list {
  max-height: 300px;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.staff-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border: 1px solid var(--color-border-2);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: rgb(var(--primary-6));
    background: var(--color-fill-2);
  }

  &.active {
    border-color: rgb(var(--primary-6));
    background: var(--color-primary-light-1);
  }

  .staff-main {
    display: flex;
    flex-direction: column;
    gap: 4px;

    strong {
      font-size: 15px;
    }

    span {
      font-size: 12px;
      color: var(--color-text-3);
    }
  }
}

// 实时识别预览
.realtime-preview {
  margin-bottom: 16px;
  padding: 16px;
  border-radius: 8px;
  background: var(--color-success-light-1);
  border: 1px solid rgb(var(--success-6));

  .realtime-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    font-size: 13px;
    color: rgb(var(--success-6));
    font-weight: 500;
  }

  .realtime-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--color-text-4);

    &.active {
      background: rgb(var(--success-6));
      animation: pulse 1.5s infinite;
    }
  }

  .realtime-text {
    font-size: 15px;
    line-height: 1.6;
    color: var(--color-text-1);
    min-height: 24px;
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}
</style>
