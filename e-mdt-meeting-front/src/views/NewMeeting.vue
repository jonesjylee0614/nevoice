<template>
  <div class="new-meeting-page">
    <!-- 顶部导航栏 -->
    <header class="top-header">
      <div class="header-content">
        <button class="back-btn" @click="goBack">
          <van-icon name="arrow-left" />
          <span>返回列表</span>
        </button>
        <div class="header-title">新建会议</div>
        <div class="header-placeholder"></div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 表单容器 -->
      <div class="form-container">
        <div class="form-header">
          <div class="header-icon">
            <van-icon name="edit" />
          </div>
          <div class="header-text">
            <h1>新建会议</h1>
            <p>填写会议基本信息，开始 MDT 会议纪要</p>
          </div>
        </div>

        <form class="meeting-form" @submit.prevent="onSubmit">
          <!-- 基本信息 -->
          <div class="form-section">
            <h3 class="section-title">
              <van-icon name="records" />
              基本信息
            </h3>
            
            <div class="form-group">
              <label class="form-label">
                会议标题
                <span class="label-hint">（选填，留空将自动生成）</span>
              </label>
              <input
                v-model="formData.title"
                type="text"
                placeholder="如：呼吸科多学科病例讨论"
                class="form-input"
              />
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">开始时间</label>
                <div 
                  class="datetime-picker"
                  @click="showStartPicker = true"
                >
                  <van-icon name="clock-o" />
                  <span :class="{ placeholder: !startTimeDisplay }">
                    {{ startTimeDisplay || '选择开始时间' }}
                  </span>
                  <van-icon name="arrow-down" class="arrow" />
                </div>
              </div>
              
              <div class="form-group">
                <label class="form-label">
                  结束时间
                  <span class="label-hint">（选填）</span>
                </label>
                <div 
                  class="datetime-picker"
                  @click="showEndPicker = true"
                >
                  <van-icon name="clock-o" />
                  <span :class="{ placeholder: !endTimeDisplay }">
                    {{ endTimeDisplay || '选择结束时间' }}
                  </span>
                  <van-icon name="arrow-down" class="arrow" />
                </div>
              </div>
            </div>
          </div>

          <!-- 详细信息 -->
          <div class="form-section">
            <h3 class="section-title">
              <van-icon name="description" />
              详细信息
            </h3>
            
            <div class="form-group">
              <label class="form-label">
                会议说明
                <span class="label-hint">（选填）</span>
              </label>
              <textarea
                v-model="formData.description"
                placeholder="填写会议重点、参会科室等辅助信息..."
                rows="4"
                class="form-textarea"
              ></textarea>
            </div>
            
            <div class="form-group">
              <label class="form-label">
                会议标签
                <span class="label-hint">（最多5个）</span>
              </label>
              <div class="tags-container">
                <div class="tags-list">
                  <span
                    v-for="(tag, index) in formData.tagList"
                    :key="index"
                    class="tag-item"
                  >
                    {{ tag }}
                    <van-icon name="cross" @click="removeTag(index)" />
                  </span>
                  <button 
                    v-if="formData.tagList.length < 5"
                    type="button"
                    class="add-tag-btn"
                    @click="showTagInput = true"
                  >
                    <van-icon name="plus" />
                    添加标签
                  </button>
                </div>
                <div class="quick-tags">
                  <span class="quick-tag-label">快速添加：</span>
                  <span 
                    v-for="tag in quickTags" 
                    :key="tag"
                    class="quick-tag"
                    :class="{ active: formData.tagList.includes(tag) }"
                    @click="toggleQuickTag(tag)"
                  >
                    {{ tag }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 提交按钮 -->
          <div class="form-actions">
            <button type="button" class="btn-cancel" @click="goBack">
              取消
            </button>
            <button type="submit" class="btn-submit" :disabled="submitting">
              <van-loading v-if="submitting" size="18px" color="#fff" />
              <template v-else>
                <van-icon name="checked" />
                创建会议
              </template>
            </button>
          </div>
        </form>
      </div>
    </main>

    <!-- 开始时间选择器 -->
    <van-popup v-model:show="showStartPicker" position="center" round class="picker-popup">
      <van-picker-group
        title="选择开始时间"
        :tabs="['选择日期', '选择时间']"
        @confirm="onStartConfirm"
        @cancel="showStartPicker = false"
      >
        <van-date-picker v-model="startDateValue" :min-date="minDate" />
        <van-time-picker v-model="startTimeValue" />
      </van-picker-group>
    </van-popup>

    <!-- 结束时间选择器 -->
    <van-popup v-model:show="showEndPicker" position="center" round class="picker-popup">
      <van-picker-group
        title="选择结束时间"
        :tabs="['选择日期', '选择时间']"
        @confirm="onEndConfirm"
        @cancel="showEndPicker = false"
      >
        <van-date-picker v-model="endDateValue" :min-date="minDate" />
        <van-time-picker v-model="endTimeValue" />
      </van-picker-group>
    </van-popup>

    <!-- 添加标签弹窗 -->
    <van-popup v-model:show="showTagInput" round position="center" class="tag-popup">
      <div class="popup-content">
        <h3>添加标签</h3>
        <input
          v-model="newTag"
          type="text"
          placeholder="请输入标签名称"
          class="tag-input"
          maxlength="10"
          @keyup.enter="addTag"
        />
        <div class="popup-actions">
          <button type="button" class="popup-cancel" @click="showTagInput = false">取消</button>
          <button type="button" class="popup-confirm" @click="addTag">确定</button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { showSuccessToast, showToast } from 'vant'
import { createMeeting } from '@/api/meeting'

const router = useRouter()

// 表单数据
const formData = reactive({
  title: '',
  description: '',
  startTime: '',
  endTime: '',
  tagList: [] as string[]
})

// 快速标签
const quickTags = ['MDT', '疑难病例', '术前讨论', '科研', '教学']

// 时间选择相关
const showStartPicker = ref(false)
const showEndPicker = ref(false)
const minDate = new Date()

// 初始化当前时间
const now = new Date()
const startDateValue = ref([
  now.getFullYear().toString(),
  (now.getMonth() + 1).toString().padStart(2, '0'),
  now.getDate().toString().padStart(2, '0')
])
const startTimeValue = ref([
  now.getHours().toString().padStart(2, '0'),
  now.getMinutes().toString().padStart(2, '0')
])
const endDateValue = ref([...startDateValue.value])
const endTimeValue = ref([...startTimeValue.value])

// 设置初始开始时间
formData.startTime = formatDateTime(startDateValue.value, startTimeValue.value)

// 格式化显示时间
const startTimeDisplay = computed(() => {
  return formData.startTime ? formatDisplayTime(formData.startTime) : ''
})

const endTimeDisplay = computed(() => {
  return formData.endTime ? formatDisplayTime(formData.endTime) : ''
})

// 格式化日期时间为 ISO 格式
function formatDateTime(dateArr: string[], timeArr: string[]): string {
  return `${dateArr[0]}-${dateArr[1]}-${dateArr[2]}T${timeArr[0]}:${timeArr[1]}`
}

// 格式化显示时间
function formatDisplayTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 确认开始时间
const onStartConfirm = () => {
  formData.startTime = formatDateTime(startDateValue.value, startTimeValue.value)
  showStartPicker.value = false
}

// 确认结束时间
const onEndConfirm = () => {
  formData.endTime = formatDateTime(endDateValue.value, endTimeValue.value)
  showEndPicker.value = false
}

// 标签相关
const showTagInput = ref(false)
const newTag = ref('')

const addTag = () => {
  if (newTag.value.trim()) {
    if (!formData.tagList.includes(newTag.value.trim())) {
      if (formData.tagList.length < 5) {
        formData.tagList.push(newTag.value.trim())
      } else {
        showToast('最多添加5个标签')
      }
    }
    newTag.value = ''
    showTagInput.value = false
  }
}

const removeTag = (index: number) => {
  formData.tagList.splice(index, 1)
}

// 快速添加标签
const toggleQuickTag = (tag: string) => {
  const index = formData.tagList.indexOf(tag)
  if (index > -1) {
    formData.tagList.splice(index, 1)
  } else {
    if (formData.tagList.length < 5) {
      formData.tagList.push(tag)
    } else {
      showToast('最多添加5个标签')
    }
  }
}

// 提交状态
const submitting = ref(false)

// 提交表单
const onSubmit = async () => {
  submitting.value = true
  
  try {
    let title = formData.title.trim()
    if (!title && formData.startTime) {
      const date = new Date(formData.startTime)
      title = `${date.getFullYear()}年${(date.getMonth() + 1).toString().padStart(2, '0')}月${date.getDate().toString().padStart(2, '0')}日 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')} 会议`
    }

    const { data } = await createMeeting({
      title,
      description: formData.description,
      startTime: formData.startTime,
      endTime: formData.endTime || undefined,
      tagList: formData.tagList.length > 0 ? formData.tagList : undefined
    })

    showSuccessToast('创建成功')
    router.replace(`/detail/${data.data.id}`)
  } catch (error) {
    console.error('创建会议失败:', error)
    showToast('创建会议失败')
  } finally {
    submitting.value = false
  }
}

// 返回
const goBack = () => {
  router.back()
}
</script>

<style lang="scss" scoped>
.new-meeting-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f4ff 0%, #fafbff 50%, #ffffff 100%);
}

// 顶部导航栏
.top-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-light);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary);
    color: var(--primary);
  }

  :deep(.van-icon) {
    font-size: 16px;
  }
}

.header-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-main);
}

.header-placeholder {
  width: 100px;
}

// 主内容区
.main-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 24px;
}

// 表单容器
.form-container {
  background: var(--surface);
  border-radius: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.form-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 32px;
  background: linear-gradient(135deg, var(--primary-light) 0%, rgba(139, 92, 246, 0.08) 100%);
  border-bottom: 1px solid var(--border-light);
}

.header-icon {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.35);

  :deep(.van-icon) {
    font-size: 30px;
    color: white;
  }
}

.header-text {
  h1 {
    font-size: 24px;
    font-weight: 700;
    color: var(--text-main);
    margin-bottom: 6px;
  }

  p {
    font-size: 14px;
    color: var(--text-secondary);
  }
}

// 表单
.meeting-form {
  padding: 32px;
}

.form-section {
  margin-bottom: 36px;

  &:last-of-type {
    margin-bottom: 0;
  }
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 24px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border-light);

  :deep(.van-icon) {
    font-size: 20px;
    color: var(--primary);
  }
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 12px;

  .label-hint {
    font-size: 12px;
    font-weight: 400;
    color: var(--text-tertiary);
    margin-left: 8px;
  }
}

.form-input {
  width: 100%;
  height: 52px;
  padding: 0 18px;
  border: 2px solid var(--border);
  border-radius: 14px;
  font-size: 15px;
  color: var(--text-main);
  background: var(--surface);
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 4px var(--primary-light);
  }

  &::placeholder {
    color: var(--text-tertiary);
  }
}

.form-textarea {
  width: 100%;
  padding: 16px 18px;
  border: 2px solid var(--border);
  border-radius: 14px;
  font-size: 15px;
  color: var(--text-main);
  background: var(--surface);
  resize: none;
  font-family: inherit;
  line-height: 1.7;
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 4px var(--primary-light);
  }

  &::placeholder {
    color: var(--text-tertiary);
  }
}

// 日期时间选择器
.datetime-picker {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 52px;
  padding: 0 18px;
  background: var(--surface);
  border: 2px solid var(--border);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary);
  }

  :deep(.van-icon) {
    font-size: 18px;
    color: var(--text-tertiary);
  }

  span {
    flex: 1;
    font-size: 15px;
    color: var(--text-main);

    &.placeholder {
      color: var(--text-tertiary);
    }
  }

  .arrow {
    font-size: 14px;
  }
}

// 标签
.tags-container {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  min-height: 42px;
  align-items: center;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 24px;
  font-size: 14px;
  font-weight: 600;

  :deep(.van-icon) {
    font-size: 14px;
    cursor: pointer;
    opacity: 0.7;

    &:hover {
      opacity: 1;
    }
  }
}

.add-tag-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: transparent;
  border: 2px dashed var(--border);
  border-radius: 24px;
  font-size: 14px;
  color: var(--text-secondary);
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

.quick-tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  padding-top: 18px;
  border-top: 1px solid var(--border-light);
}

.quick-tag-label {
  font-size: 13px;
  color: var(--text-tertiary);
}

.quick-tag {
  padding: 8px 16px;
  background: var(--surface-muted);
  border: 2px solid transparent;
  border-radius: 20px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary);
    color: var(--primary);
  }

  &.active {
    background: var(--primary-light);
    border-color: var(--primary);
    color: var(--primary);
    font-weight: 600;
  }
}

// 表单操作
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding-top: 36px;
  border-top: 1px solid var(--border-light);
  margin-top: 36px;
}

.btn-cancel {
  padding: 16px 32px;
  border: 2px solid var(--border);
  border-radius: 14px;
  background: var(--surface);
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--text-secondary);
    background: var(--surface-muted);
  }
}

.btn-submit {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px 36px;
  border: none;
  border-radius: 14px;
  background: var(--primary-gradient);
  font-size: 15px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.35);
  transition: all 0.3s ease;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(99, 102, 241, 0.45);
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  :deep(.van-icon) {
    font-size: 18px;
  }
}

// 弹窗
.picker-popup {
  :deep(.van-picker) {
    max-width: 500px;
    margin: 0 auto;
  }
}

.tag-popup {
  width: 420px;
  border-radius: 20px;
}

.popup-content {
  padding: 32px;

  h3 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-main);
    margin-bottom: 24px;
    text-align: center;
  }
}

.tag-input {
  width: 100%;
  height: 52px;
  padding: 0 18px;
  border: 2px solid var(--border);
  border-radius: 14px;
  font-size: 15px;
  color: var(--text-main);
  margin-bottom: 24px;

  &:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 4px var(--primary-light);
  }
}

.popup-actions {
  display: flex;
  gap: 14px;
}

.popup-cancel,
.popup-confirm {
  flex: 1;
  height: 48px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.popup-cancel {
  border: 2px solid var(--border);
  background: var(--surface);
  color: var(--text-main);

  &:hover {
    background: var(--surface-muted);
  }
}

.popup-confirm {
  border: none;
  background: var(--primary-gradient);
  color: white;

  &:hover {
    opacity: 0.9;
  }
}

// 响应式
@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .header-content {
    padding: 0 16px;
  }

  .main-content {
    padding: 16px;
  }

  .form-header {
    flex-direction: column;
    text-align: center;
    padding: 24px;
  }

  .meeting-form {
    padding: 24px;
  }

  .form-actions {
    flex-direction: column-reverse;
  }

  .btn-cancel,
  .btn-submit {
    width: 100%;
  }

  .tag-popup,
  .picker-popup {
    width: calc(100% - 32px);
  }
}

// 时间选择器弹框
.picker-popup {
  width: 400px;
  max-width: 90vw;
}
</style>
