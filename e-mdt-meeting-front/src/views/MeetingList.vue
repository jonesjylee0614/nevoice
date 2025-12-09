<template>
  <div class="meeting-list-page">
    <!-- 顶部导航栏 -->
    <header class="top-header">
      <div class="header-content">
        <div class="header-left">
          <div class="logo">
            <div class="logo-icon">
              <van-icon name="video-o" />
            </div>
            <div class="logo-info">
              <span class="logo-text">MDT 会议</span>
              <span class="logo-desc">多学科团队会议系统</span>
            </div>
          </div>
        </div>
        <div class="header-right">
          <div class="user-info" @click="showUserMenu = true">
            <div class="user-avatar">
              {{ userStore.userName.charAt(0) }}
            </div>
            <div class="user-detail">
              <span class="user-name">{{ userStore.userName }}</span>
              <span class="user-role">管理员</span>
            </div>
            <van-icon name="arrow-down" />
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 顶部工具栏 -->
      <div class="top-toolbar">
        <div class="toolbar-left">
          <span class="greeting">👋 {{ userStore.userName }}，{{ todayDate }}</span>
        </div>
        
        <!-- 统计数据 -->
        <div class="stats-inline">
          <div class="stat-item" :class="{ active: filterStatus === undefined }" @click="filterStatus = undefined">
            <span class="stat-num">{{ total }}</span>
            <span class="stat-name">全部</span>
          </div>
          <div class="stat-item" :class="{ active: filterStatus === 1 }" @click="filterStatus = 1">
            <span class="stat-num running">{{ runningCount }}</span>
            <span class="stat-name">进行中</span>
          </div>
          <div class="stat-item" :class="{ active: filterStatus === 2 }" @click="filterStatus = 2">
            <span class="stat-num completed">{{ completedCount }}</span>
            <span class="stat-name">已完成</span>
          </div>
          <div class="stat-item">
            <span class="stat-num summary">{{ summaryCount }}</span>
            <span class="stat-name">已总结</span>
          </div>
        </div>
      </div>

      <!-- 搜索和筛选栏 -->
      <div class="toolbar">
        <div class="search-box">
          <van-icon name="search" />
          <input 
            v-model="searchKeyword"
            type="text"
            placeholder="搜索会议标题..."
            @keyup.enter="handleSearch"
          />
          <van-icon 
            v-if="searchKeyword" 
            name="clear" 
            class="clear-btn"
            @click="searchKeyword = ''; handleSearch()"
          />
        </div>
        
        <!-- 时间筛选 -->
        <div class="date-filter" @click="showDateFilter = true">
          <van-icon name="calendar-o" />
          <span>{{ filterDateText }}</span>
          <van-icon name="arrow-down" class="arrow" />
        </div>
        
        <div class="toolbar-actions">
          <button 
            v-if="filterStatus !== undefined || filterDateRange" 
            class="btn-clear-filter"
            @click="clearFilters"
          >
            <van-icon name="close" />
            清除筛选
          </button>
          <button class="btn-new-meeting" @click="goToNewMeeting">
            <van-icon name="plus" />
            <span>新建会议</span>
          </button>
          <button class="btn-icon" title="刷新" @click="onRefresh">
            <van-icon name="replay" :class="{ spinning: refreshing }" />
          </button>
        </div>
      </div>

      <!-- 会议列表 -->
      <div class="meeting-list">
        <!-- 加载状态 -->
        <div v-if="loading && meetings.length === 0" class="loading-state">
          <van-loading size="36px" vertical>
            <template #icon>
              <div class="loading-icon">
                <van-icon name="video-o" />
              </div>
            </template>
            正在加载会议...
          </van-loading>
        </div>

        <!-- 空状态 -->
        <div v-else-if="!loading && filteredMeetings.length === 0" class="empty-state">
          <div class="empty-illustration">
            <div class="empty-icon">
              <van-icon name="notes-o" />
            </div>
            <div class="empty-rings">
              <div class="ring ring-1"></div>
              <div class="ring ring-2"></div>
              <div class="ring ring-3"></div>
            </div>
          </div>
          <h3>{{ filterStatus !== undefined ? '没有找到符合条件的会议' : '暂无会议记录' }}</h3>
          <p>{{ filterStatus !== undefined ? '尝试清除筛选条件或创建新会议' : '点击下方按钮创建您的第一个 MDT 会议' }}</p>
          <button class="btn-create" @click="filterStatus !== undefined ? (filterStatus = undefined) : goToNewMeeting()">
            <van-icon :name="filterStatus !== undefined ? 'replay' : 'plus'" />
            <span>{{ filterStatus !== undefined ? '清除筛选' : '新建会议' }}</span>
          </button>
        </div>

        <!-- 会议卡片列表 -->
        <TransitionGroup name="card-list" tag="div" class="cards-container" v-else>
          <div 
            v-for="(meeting, index) in filteredMeetings" 
            :key="meeting.id"
            class="meeting-card"
            :style="{ animationDelay: `${index * 0.05}s` }"
            @click="goToDetail(meeting.id)"
          >
            <!-- 状态指示条 -->
            <div class="card-indicator" :class="statusClass(meeting.status)"></div>
            
            <div class="card-main">
              <div class="card-header">
                <div class="title-row">
                  <h3 class="meeting-title">{{ meeting.title || '未命名会议' }}</h3>
                  <!-- 优先显示总结状态，避免"进行中"和"已总结"同时显示 -->
                  <span v-if="meeting.summaryStatus === 2" class="status-badge status-summarized">
                    <span class="status-dot"></span>
                    已总结
                  </span>
                  <span v-else-if="meeting.summaryStatus === 1" class="status-badge status-summarizing">
                    <span class="status-dot"></span>
                    生成中
                  </span>
                  <span v-else class="status-badge" :class="statusClass(meeting.status)">
                    <span class="status-dot"></span>
                    {{ statusText(meeting.status) }}
                  </span>
                </div>
              </div>
              
              <div class="card-meta">
                <span class="meta-item">
                  <van-icon name="clock-o" />
                  {{ formatTime(meeting.startTime, meeting.endTime) }}
                </span>
                <span class="meta-divider">·</span>
                <span class="meta-item">
                  <van-icon name="chat-o" />
                  {{ meeting.dialogCount || 0 }} 条对话
                </span>
              </div>

              <div class="card-tags" v-if="meeting.tagList?.length">
                <span v-for="tag in meeting.tagList.slice(0, 2)" :key="tag" class="tag">{{ tag }}</span>
                <span v-if="meeting.tagList.length > 2" class="tag tag-more">+{{ meeting.tagList.length - 2 }}</span>
              </div>
            </div>

            <div class="card-actions">
              <button class="action-btn view" title="查看详情" @click.stop="goToDetail(meeting.id)">
                <van-icon name="eye-o" />
              </button>
              <button class="action-btn delete" title="删除" @click.stop="handleDelete(meeting)">
                <van-icon name="delete-o" />
              </button>
            </div>
          </div>
        </TransitionGroup>
      </div>

      <!-- 分页 -->
      <div class="pagination" v-if="filteredMeetings.length > 0">
        <span class="page-info">
          <van-icon name="list-switch" />
          共 {{ total }} 条记录
        </span>
        <div class="page-controls">
          <button 
            class="page-btn" 
            :disabled="page === 1"
            @click="changePage(page - 1)"
          >
            <van-icon name="arrow-left" />
            上一页
          </button>
          <span class="page-current">{{ page }}</span>
          <button 
            class="page-btn"
            :disabled="finished"
            @click="changePage(page + 1)"
          >
            下一页
            <van-icon name="arrow" />
          </button>
        </div>
      </div>
    </main>

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

    <!-- 新建会议弹框 -->
    <van-popup
      v-model:show="showCreateModal"
      round
      position="center"
      class="create-modal"
      :style="{ width: '520px', maxWidth: '90vw' }"
    >
      <div class="modal-content">
        <div class="modal-header">
          <h3>新建会议</h3>
          <van-icon name="cross" @click="showCreateModal = false" />
        </div>
        
        <form class="create-form" @submit.prevent="onCreateSubmit">
          <div class="form-group">
            <label>会议标题 <span class="hint">（选填）</span></label>
            <input
              v-model="createForm.title"
              type="text"
              placeholder="如：呼吸科多学科病例讨论"
              class="form-input"
            />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>开始时间</label>
              <div class="datetime-input" @click="showStartPicker = true">
                <van-icon name="clock-o" />
                <span :class="{ placeholder: !createForm.startTime }">
                  {{ formatDisplayTime(createForm.startTime) || '选择时间' }}
                </span>
              </div>
            </div>
            <div class="form-group">
              <label>结束时间 <span class="hint">（选填）</span></label>
              <div class="datetime-input" @click="showEndPicker = true">
                <van-icon name="clock-o" />
                <span :class="{ placeholder: !createForm.endTime }">
                  {{ formatDisplayTime(createForm.endTime) || '选择时间' }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <label>会议说明 <span class="hint">（选填）</span></label>
            <textarea
              v-model="createForm.description"
              placeholder="填写会议重点、参会科室等..."
              rows="2"
              class="form-textarea"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>快速标签</label>
            <div class="quick-tags">
              <span
                v-for="tag in quickTags"
                :key="tag"
                class="quick-tag"
                :class="{ active: createForm.tagList.includes(tag) }"
                @click="toggleTag(tag)"
              >{{ tag }}</span>
            </div>
          </div>
          
          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="showCreateModal = false">取消</button>
            <button type="submit" class="btn-submit" :disabled="creating">
              <van-loading v-if="creating" size="16px" color="#fff" />
              <span>{{ creating ? '创建中...' : '创建会议' }}</span>
            </button>
          </div>
        </form>
      </div>
    </van-popup>

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

    <!-- 日期筛选弹框 -->
    <van-popup v-model:show="showDateFilter" position="center" round class="date-filter-popup">
      <div class="date-filter-content">
        <div class="filter-header">
          <h3>选择时间范围</h3>
          <van-icon name="cross" @click="showDateFilter = false" />
        </div>
        <div class="filter-presets">
          <button 
            v-for="preset in datePresets" 
            :key="preset.label"
            :class="{ active: selectedPreset === preset.label }"
            @click="selectDatePreset(preset)"
          >{{ preset.label }}</button>
        </div>
        <div class="filter-custom">
          <div class="custom-label">自定义范围</div>
          <div class="custom-inputs">
            <div class="date-input" @click="showFilterStartDate = true">
              <van-icon name="calendar-o" />
              <span>{{ filterStartDate || '开始日期' }}</span>
            </div>
            <span class="date-separator">至</span>
            <div class="date-input" @click="showFilterEndDate = true">
              <van-icon name="calendar-o" />
              <span>{{ filterEndDate || '结束日期' }}</span>
            </div>
          </div>
        </div>
        <div class="filter-actions">
          <button class="btn-reset" @click="resetDateFilter">重置</button>
          <button class="btn-apply" @click="applyDateFilter">应用筛选</button>
        </div>
      </div>
    </van-popup>

    <!-- 筛选开始日期选择器 -->
    <van-popup v-model:show="showFilterStartDate" position="center" round class="picker-popup">
      <van-date-picker 
        v-model="filterStartDateValue" 
        title="选择开始日期"
        @confirm="onFilterStartConfirm"
        @cancel="showFilterStartDate = false"
      />
    </van-popup>

    <!-- 筛选结束日期选择器 -->
    <van-popup v-model:show="showFilterEndDate" position="center" round class="picker-popup">
      <van-date-picker 
        v-model="filterEndDateValue"
        title="选择结束日期"
        @confirm="onFilterEndConfirm"
        @cancel="showFilterEndDate = false"
      />
    </van-popup>

  </div>
</template>

<script setup lang="ts">
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
import type { Meeting, MeetingStatus } from '@/api/types'
import { getList, deleteMeeting, createMeeting } from '@/api/meeting'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 状态
const searchKeyword = ref('')
const meetings = ref<Meeting[]>([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const page = ref(1)
const pageSize = 12
const total = ref(0)
const filterStatus = ref<MeetingStatus | undefined>(undefined)

// 日期筛选相关
const showDateFilter = ref(false)
const showFilterStartDate = ref(false)
const showFilterEndDate = ref(false)
const filterStartDate = ref('')
const filterEndDate = ref('')
const filterDateRange = ref('')
const selectedPreset = ref('')

const filterStartDateValue = ref([
  new Date().getFullYear().toString(),
  (new Date().getMonth() + 1).toString().padStart(2, '0'),
  new Date().getDate().toString().padStart(2, '0')
])
const filterEndDateValue = ref([...filterStartDateValue.value])

// 日期预设选项
const datePresets = [
  { label: '今天', days: 0 },
  { label: '近7天', days: 7 },
  { label: '近30天', days: 30 },
  { label: '本月', days: -1 },
  { label: '上月', days: -2 }
]

// 筛选日期显示文本
const filterDateText = computed(() => {
  if (selectedPreset.value) return selectedPreset.value
  if (filterDateRange.value) {
    const [start, end] = filterDateRange.value.split(',')
    return `${start} - ${end}`
  }
  return '选择时间'
})

// 选择日期预设
const selectDatePreset = (preset: { label: string; days: number }) => {
  selectedPreset.value = preset.label
  const today = new Date()
  let start: Date
  let end = new Date()
  
  if (preset.days === 0) {
    // 今天
    start = new Date(today)
  } else if (preset.days === -1) {
    // 本月
    start = new Date(today.getFullYear(), today.getMonth(), 1)
  } else if (preset.days === -2) {
    // 上月
    start = new Date(today.getFullYear(), today.getMonth() - 1, 1)
    end = new Date(today.getFullYear(), today.getMonth(), 0)
  } else {
    // 近 N 天
    start = new Date(today.getTime() - preset.days * 24 * 60 * 60 * 1000)
  }
  
  filterStartDate.value = formatDate2(start)
  filterEndDate.value = formatDate2(end)
}

// 格式化日期为 YYYY-MM-DD
const formatDate2 = (date: Date) => {
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

// 确认筛选开始日期
const onFilterStartConfirm = ({ selectedValues }: { selectedValues: string[] }) => {
  filterStartDate.value = selectedValues.join('-')
  showFilterStartDate.value = false
  selectedPreset.value = ''
}

// 确认筛选结束日期
const onFilterEndConfirm = ({ selectedValues }: { selectedValues: string[] }) => {
  filterEndDate.value = selectedValues.join('-')
  showFilterEndDate.value = false
  selectedPreset.value = ''
}

// 重置日期筛选
const resetDateFilter = () => {
  filterStartDate.value = ''
  filterEndDate.value = ''
  filterDateRange.value = ''
  selectedPreset.value = ''
}

// 应用日期筛选
const applyDateFilter = () => {
  if (filterStartDate.value && filterEndDate.value) {
    filterDateRange.value = `${filterStartDate.value},${filterEndDate.value}`
  } else {
    filterDateRange.value = ''
  }
  showDateFilter.value = false
  page.value = 1
  fetchMeetings()
}

// 清除所有筛选
const clearFilters = () => {
  filterStatus.value = undefined
  resetDateFilter()
  page.value = 1
  fetchMeetings()
}

// 用户菜单
const showUserMenu = ref(false)
const userMenuActions = [
  { name: '个人设置', icon: 'setting-o' },
  { name: '退出登录', icon: 'revoke', color: '#ee0a24' }
]

// 今天日期
const todayDate = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日 ${['周日', '周一', '周二', '周三', '周四', '周五', '周六'][now.getDay()]}`
})

// 统计数据
const runningCount = computed(() => meetings.value.filter(m => m.status === 1).length)
const completedCount = computed(() => meetings.value.filter(m => m.status === 2).length)
const summaryCount = computed(() => meetings.value.filter(m => m.summaryStatus === 2).length)

// 过滤后的会议列表
const filteredMeetings = computed(() => {
  if (filterStatus.value === undefined) {
    return meetings.value
  }
  return meetings.value.filter(m => m.status === filterStatus.value)
})

// 获取会议列表
const fetchMeetings = async (isRefresh = false) => {
  if (isRefresh) {
    page.value = 1
    finished.value = false
  }

  loading.value = true
  try {
    const { data } = await getList({
      page: page.value,
      pageSize,
      title: searchKeyword.value || undefined,
      createdTime: filterDateRange.value || undefined
    })
    
    const result = data.data
    meetings.value = result.items || []
    total.value = result.total || 0
    
    if (meetings.value.length >= total.value) {
      finished.value = true
    }
  } catch (error) {
    console.error('获取会议列表失败:', error)
    showToast('获取会议列表失败')
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

// 换页
const changePage = (newPage: number) => {
  page.value = newPage
  fetchMeetings()
}

// 刷新
const onRefresh = () => {
  refreshing.value = true
  fetchMeetings(true)
}

// 搜索
const handleSearch = () => {
  fetchMeetings(true)
}

// 删除会议
const handleDelete = async (meeting: Meeting) => {
  try {
    await showConfirmDialog({
      title: '删除确认',
      message: `确定要删除会议"${meeting.title || '未命名会议'}"吗？\n此操作不可恢复！`,
    })
    await deleteMeeting([meeting.id])
    showToast('删除成功')
    fetchMeetings(true)
  } catch {
    // 用户取消
  }
}

// 新建会议弹框相关
const showCreateModal = ref(false)
const creating = ref(false)
const createForm = reactive({
  title: '',
  description: '',
  startTime: '',
  endTime: '',
  tagList: [] as string[]
})
const quickTags = ['MDT', '疑难病例', '术前讨论', '科研', '教学']

// 时间选择器
const showStartPicker = ref(false)
const showEndPicker = ref(false)
const minDate = new Date()
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

// 格式化显示时间
const formatDisplayTime = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 确认开始时间
const onStartConfirm = () => {
  createForm.startTime = `${startDateValue.value.join('-')}T${startTimeValue.value.join(':')}`
  showStartPicker.value = false
}

// 确认结束时间
const onEndConfirm = () => {
  createForm.endTime = `${endDateValue.value.join('-')}T${endTimeValue.value.join(':')}`
  showEndPicker.value = false
}

// 切换标签
const toggleTag = (tag: string) => {
  const index = createForm.tagList.indexOf(tag)
  if (index > -1) {
    createForm.tagList.splice(index, 1)
  } else if (createForm.tagList.length < 5) {
    createForm.tagList.push(tag)
  } else {
    showToast('最多添加5个标签')
  }
}

// 打开新建会议弹框
const goToNewMeeting = () => {
  // 重置表单
  createForm.title = ''
  createForm.description = ''
  createForm.startTime = `${startDateValue.value.join('-')}T${startTimeValue.value.join(':')}`
  createForm.endTime = ''
  createForm.tagList = []
  showCreateModal.value = true
}

// 提交新建会议
const onCreateSubmit = async () => {
  creating.value = true
  
  try {
    let title = createForm.title.trim()
    if (!title && createForm.startTime) {
      const date = new Date(createForm.startTime)
      title = `${date.getFullYear()}年${(date.getMonth() + 1).toString().padStart(2, '0')}月${date.getDate().toString().padStart(2, '0')}日 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')} 会议`
    }

    const { data } = await createMeeting({
      title,
      description: createForm.description,
      startTime: createForm.startTime,
      endTime: createForm.endTime || undefined,
      tagList: createForm.tagList.length > 0 ? createForm.tagList : undefined
    })

    showSuccessToast('创建成功')
    showCreateModal.value = false
    router.push(`/detail/${data.data.id}`)
  } catch (error) {
    console.error('创建会议失败:', error)
    showToast('创建会议失败')
  } finally {
    creating.value = false
  }
}

// 跳转到会议详情
const goToDetail = (id: number) => {
  router.push(`/detail/${id}`)
}

// 用户菜单选择
const onUserMenuSelect = async (action: { name: string }) => {
  if (action.name === '退出登录') {
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

// 格式化时间范围
const formatTime = (start: string, end: string) => {
  if (!start) return '时间待定'
  const startDate = new Date(start)
  const month = (startDate.getMonth() + 1).toString().padStart(2, '0')
  const day = startDate.getDate().toString().padStart(2, '0')
  const startTime = startDate.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  
  if (!end) return `${month}/${day} ${startTime}`
  
  const endDate = new Date(end)
  const endTime = endDate.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  return `${month}/${day} ${startTime} - ${endTime}`
}

// 格式化日期
const formatDate = (date: string) => {
  if (!date) return '-'
  const d = new Date(date)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  
  // 1分钟内
  if (diff < 60000) return '刚刚'
  // 1小时内
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  // 24小时内
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  // 7天内
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`
  
  const month = (d.getMonth() + 1).toString().padStart(2, '0')
  const day = d.getDate().toString().padStart(2, '0')
  return `${month}/${day}`
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

// 状态样式
const statusClass = (status: MeetingStatus) => {
  const map: Record<number, string> = {
    0: 'status-pending',
    1: 'status-running',
    2: 'status-completed'
  }
  return map[status] || ''
}

// 初始化
onMounted(() => {
  fetchMeetings(true)
})
</script>

<style lang="scss" scoped>
.meeting-list-page {
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 14px;
}

.logo-icon {
  width: 44px;
  height: 44px;
  background: var(--primary-gradient);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35);

  :deep(.van-icon) {
    font-size: 24px;
    color: #fff;
  }
}

.logo-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main);
}

.logo-desc {
  font-size: 12px;
  color: var(--text-tertiary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px 8px 8px;
  background: var(--surface-muted);
  border-radius: 28px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--surface-hover);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--primary-gradient);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
}

.user-detail {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
}

.user-role {
  font-size: 11px;
  color: var(--text-tertiary);
}

// 主内容区
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 24px;
}

// 顶部工具栏（合并欢迎和统计）
.top-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: var(--surface);
  border-radius: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid var(--border-light);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.greeting {
  font-size: 14px;
  color: var(--text-secondary);
}


// 内联统计
.stats-inline {
  display: flex;
  gap: 6px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--surface-muted);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;

  &:hover {
    background: var(--surface-hover);
  }
  
  &.active {
    background: var(--primary-light);
    border-color: var(--primary);
  }
}

.stat-num {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main);
  
  &.running { color: var(--warning); }
  &.completed { color: var(--success); }
  &.summary { color: var(--info); }
}

.stat-name {
  font-size: 12px;
  color: var(--text-secondary);
}

// 兼容原有的 btn-create
.btn-create {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--primary-gradient);
  color: #fff;
  border: none;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  transition: all 0.2s ease;

  &:hover {
    box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
  }

  :deep(.van-icon) {
    font-size: 26px;
  }
}


// 工具栏
.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  max-width: 300px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 0 14px;
  height: 40px;
  transition: all 0.2s ease;

  &:focus-within {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px var(--primary-light);
  }

  :deep(.van-icon) {
    font-size: 16px;
    color: var(--text-tertiary);
  }

  input {
    flex: 1;
    border: none;
    outline: none;
    background: transparent;
    font-size: 13px;
    color: var(--text-main);
    
    &::placeholder {
      color: var(--text-tertiary);
    }
  }

  .clear-btn {
    cursor: pointer;
    transition: color 0.2s;
    
    &:hover {
      color: var(--text-secondary);
    }
  }
}

// 日期筛选按钮
.date-filter {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 14px;
  height: 40px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: var(--primary);
  }
  
  :deep(.van-icon) {
    font-size: 16px;
    color: var(--text-tertiary);
    
    &.arrow {
      font-size: 12px;
    }
  }
  
  span {
    font-size: 13px;
    color: var(--text-secondary);
  }
}

// 清除筛选按钮
.btn-clear-filter {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background: var(--danger-light);
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  color: var(--danger);
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--danger);
    color: #fff;
  }
  
  :deep(.van-icon) {
    font-size: 12px;
  }
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.btn-new-meeting {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 18px;
  height: 40px;
  background: var(--primary-gradient);
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
    transform: translateY(-1px);
  }
  
  :deep(.van-icon) {
    font-size: 16px;
  }
}

.btn-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-secondary);

  &:hover {
    border-color: var(--primary);
    color: var(--primary);
    background: var(--primary-light);
  }

  :deep(.van-icon) {
    font-size: 18px;
    
    &.spinning {
      animation: spin 1s linear infinite;
    }
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

// 会议列表
.meeting-list {
  min-height: 350px;
}

.cards-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

// 列表动画
.card-list-enter-active,
.card-list-leave-active {
  transition: all 0.4s ease;
}

.card-list-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.card-list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

// 会议卡片
.meeting-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--surface);
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  border: 1px solid var(--border-light);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: card-slide-in 0.5s ease forwards;
  opacity: 0;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
    border-color: rgba(99, 102, 241, 0.3);
  }
}

@keyframes card-slide-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-indicator {
  height: 4px;
  width: 100%;
  
  &.status-pending {
    background: var(--text-tertiary);
  }
  
  &.status-running {
    background: linear-gradient(90deg, var(--warning) 0%, #fbbf24 100%);
  }
  
  &.status-completed {
    background: linear-gradient(90deg, var(--success) 0%, #34d399 100%);
  }
}

.card-main {
  flex: 1;
  padding: 14px 16px 10px;
  min-width: 0;
}

.card-header {
  margin-bottom: 8px;
}

.title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}

.meeting-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.35;
  flex: 1;
  margin: 0;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;

  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
  }

  &.status-pending {
    background: var(--surface-muted);
    color: var(--text-secondary);
    
    .status-dot {
      background: var(--text-tertiary);
    }
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
    
    .status-dot {
      background: var(--success);
    }
  }

  // 已总结状态 - 青绿色调，与"已结束"区分
  &.status-summarized {
    background: linear-gradient(135deg, #e0f7f4 0%, #d1f5ef 100%);
    color: #0d9488;
    border: 1px solid rgba(13, 148, 136, 0.2);
    
    .status-dot {
      background: #0d9488;
    }
  }

  // 生成中状态 - 蓝色调，带动画
  &.status-summarizing {
    background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
    color: #0284c7;
    border: 1px solid rgba(2, 132, 199, 0.2);
    
    .status-dot {
      background: #0284c7;
      animation: pulse 1.5s infinite;
    }
  }
}

// 卡片元信息（时间、对话数）
.card-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-secondary);
  
  :deep(.van-icon) {
    font-size: 12px;
    color: var(--text-tertiary);
  }
}

.meta-divider {
  color: var(--text-tertiary);
  font-size: 10px;
}

.meta-badge {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  margin-left: auto;
  
  &.success {
    background: var(--success-light);
    color: var(--success);
  }
  
  &.pending {
    background: var(--warning-light);
    color: var(--warning);
  }

  :deep(.van-icon) {
    font-size: 10px;
  }
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag {
  padding: 2px 6px;
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;

  &.tag-more {
    background: var(--surface-muted);
    color: var(--text-secondary);
  }
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
  padding: 0 16px 12px;
}

.action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-muted);
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-secondary);

  :deep(.van-icon) {
    font-size: 16px;
  }

  &.view:hover {
    background: var(--primary-light);
    border-color: var(--primary);
    color: var(--primary);
  }
  
  &.delete:hover {
    background: var(--danger-light);
    border-color: var(--danger);
    color: var(--danger);
  }
}

// 空状态
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-illustration {
  position: relative;
  margin-bottom: 32px;
}

.empty-icon {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-light) 0%, rgba(139, 92, 246, 0.1) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 2;

  :deep(.van-icon) {
    font-size: 56px;
    color: var(--primary);
    opacity: 0.7;
  }
}

.empty-rings {
  position: absolute;
  inset: -20px;
  pointer-events: none;
}

.ring {
  position: absolute;
  border: 2px solid var(--primary);
  border-radius: 50%;
  opacity: 0;
  animation: ring-pulse 3s infinite;
  
  &.ring-1 {
    inset: 10px;
    animation-delay: 0s;
  }
  
  &.ring-2 {
    inset: -10px;
    animation-delay: 1s;
  }
  
  &.ring-3 {
    inset: -30px;
    animation-delay: 2s;
  }
}

@keyframes ring-pulse {
  0% {
    opacity: 0.6;
    transform: scale(0.8);
  }
  100% {
    opacity: 0;
    transform: scale(1.2);
  }
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 10px;
}

.empty-state p {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 28px;
}

// 加载状态
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;
}

.loading-icon {
  width: 60px;
  height: 60px;
  background: var(--primary-gradient);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: loading-pulse 1.5s ease-in-out infinite;
  
  :deep(.van-icon) {
    font-size: 30px;
    color: #fff;
  }
}

@keyframes loading-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

// 分页
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28px 0;

  .page-info {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: var(--text-secondary);
    
    :deep(.van-icon) {
      font-size: 16px;
    }
  }

  .page-controls {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .page-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 12px 20px;
    background: var(--surface);
    border: 2px solid var(--border);
    border-radius: 12px;
    font-size: 14px;
    font-weight: 500;
    color: var(--text-main);
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover:not(:disabled) {
      border-color: var(--primary);
      color: var(--primary);
      background: var(--primary-light);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    :deep(.van-icon) {
      font-size: 14px;
    }
  }

  .page-current {
    min-width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--primary);
    color: #fff;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 600;
  }
}

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

// 时间选择器弹框
.picker-popup {
  width: 400px;
  max-width: 90vw;
}

// 日期筛选弹框
.date-filter-popup {
  width: 400px;
  max-width: 90vw;
}

.date-filter-content {
  padding: 24px;
  background: #ffffff;
  color: var(--text-main);
}

.filter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  
  h3 {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-main);
    margin: 0;
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

.filter-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
  
  button {
    padding: 8px 16px;
    background: var(--surface-muted);
    border: 1px solid var(--border);
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
    }
  }
}

.filter-custom {
  .custom-label {
    font-size: 12px;
    color: var(--text-tertiary);
    margin-bottom: 10px;
  }
  
  .custom-inputs {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .date-input {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    background: var(--surface-muted);
    border: 1px solid var(--border);
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
      border-color: var(--primary);
    }
    
    :deep(.van-icon) {
      font-size: 16px;
      color: var(--text-tertiary);
    }
    
    span {
      font-size: 13px;
      color: var(--text-main);
    }
  }
  
  .date-separator {
    font-size: 13px;
    color: var(--text-tertiary);
  }
}

.filter-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border-light);
}

.btn-reset,
.btn-apply {
  flex: 1;
  padding: 12px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-reset {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text-main);
  
  &:hover {
    background: var(--surface-muted);
  }
}

.btn-apply {
  background: var(--primary-gradient);
  border: none;
  color: #fff;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  
  &:hover {
    box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
  }
}

// 新建会议弹框
.create-modal {
  .modal-content {
    padding: 24px;
    background: #ffffff;
    color: var(--text-main);
  }
  
  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    
    h3 {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-main);
      margin: 0;
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
}

.create-form {
  .form-group {
    margin-bottom: 16px;
    
    label {
      display: block;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-main);
      margin-bottom: 6px;
      
      .hint {
        font-weight: 400;
        color: var(--text-tertiary);
        font-size: 12px;
      }
    }
  }
  
  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  
  .form-input,
  .form-textarea {
    width: 100%;
    padding: 10px 14px;
    border: 1px solid var(--border);
    border-radius: 10px;
    font-size: 14px;
    color: var(--text-main);
    background: var(--surface);
    transition: all 0.2s ease;
    
    &:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px var(--primary-light);
    }
    
    &::placeholder {
      color: var(--text-tertiary);
    }
  }
  
  .form-textarea {
    resize: none;
    font-family: inherit;
  }
  
  .datetime-input {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    border: 1px solid var(--border);
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
      border-color: var(--primary);
    }
    
    :deep(.van-icon) {
      font-size: 16px;
      color: var(--text-tertiary);
    }
    
    span {
      font-size: 14px;
      color: var(--text-main);
      
      &.placeholder {
        color: var(--text-tertiary);
      }
    }
  }
  
  .quick-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .quick-tag {
    padding: 6px 12px;
    background: var(--surface-muted);
    border: 1px solid var(--border);
    border-radius: 16px;
    font-size: 12px;
    font-weight: 500;
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
    }
  }
  
  .modal-actions {
    display: flex;
    gap: 12px;
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid var(--border-light);
  }
  
  .btn-cancel,
  .btn-submit {
    flex: 1;
    padding: 12px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .btn-cancel {
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text-main);
    
    &:hover {
      background: var(--surface-muted);
    }
  }
  
  .btn-submit {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    background: var(--primary-gradient);
    border: none;
    color: #fff;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    
    &:hover:not(:disabled) {
      box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
    }
    
    &:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }
  }
}

// 动画
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

// 响应式
@media (max-width: 1200px) {
  .cards-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .top-toolbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .stats-inline {
    width: 100%;
    justify-content: space-between;
  }
  
  .toolbar {
    flex-wrap: wrap;
  }
  
  .search-box {
    max-width: none;
    flex: 1 0 200px;
  }
  
  .date-filter {
    flex: 1 0 150px;
  }
}

@media (max-width: 768px) {
  .cards-container {
    grid-template-columns: 1fr;
  }
  
  .user-detail {
    display: none;
  }
  
  .greeting {
    display: none;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 16px;
  }
  
  .top-toolbar {
    padding: 12px 14px;
  }
  
  .stats-inline {
    gap: 4px;
  }
  
  .stat-item {
    padding: 6px 10px;
    
    .stat-num {
      font-size: 14px;
    }
    
    .stat-name {
      display: none;
    }
  }
  
  .logo-info {
    display: none;
  }
}
</style>
