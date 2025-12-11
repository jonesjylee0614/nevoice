<template>
  <div class="home-container">
    <!-- 顶部欢迎区域 -->
    <div class="hero-section">
      <div class="hero-bg"></div>
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">实时转写、多说话人分离、声纹注册与会议 AI 总结 </h1>
        </div>
        <div class="hero-visual">
          <div class="sound-wave">
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 核心功能卡片区 -->
    <div class="features-section">
      <div class="feature-cards">
        <div
          v-for="feature in features"
          :key="feature.id"
          class="feature-card"
          :style="{ '--accent-color': feature.color, '--accent-light': feature.lightColor }"
        >
          <div class="card-header">
            <div class="card-icon">
              <component :is="feature.icon" />
            </div>
            <h3 class="card-title">{{ feature.title }}</h3>
          </div>
          <p class="card-desc">{{ feature.description }}</p>
          <div class="card-actions">
            <AButton
              type="primary"
              size="small"
              :style="{ background: feature.color, borderColor: feature.color }"
              @click="navigateTo(feature.route)"
            >
              {{ feature.actionText }}
            </AButton>
            <AButton v-if="feature.secondaryRoute" size="small" @click="navigateTo(feature.secondaryRoute)">
              {{ feature.secondaryText }}
            </AButton>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计数据区 -->
    <div class="stats-section">
      <div class="stats-header">
        <h2 class="section-title">数据概览</h2>
      </div>
      <div class="stats-grid">
        <div v-for="stat in stats" :key="stat.label" class="stat-item">
          <div class="stat-icon" :style="{ background: stat.color }">
            <component :is="stat.icon" />
          </div>
          <div class="stat-info">
            <div class="stat-value">
              <AStatistic :value="stat.value" :precision="0" :value-from="0" animation show-group-separator />
              <span class="stat-suffix">{{ stat.suffix }}</span>
            </div>
            <span class="stat-label">{{ stat.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 快速入口区 -->
    <div class="quick-section">
      <div class="quick-header">
        <h2 class="section-title">快速入口</h2>
      </div>
      <div class="quick-grid">
        <div v-for="item in quickLinks" :key="item.name" class="quick-item" @click="navigateTo(item.route)">
          <div class="quick-icon" :style="{ background: item.bgColor }">
            <component :is="item.icon" :style="{ color: item.iconColor }" />
          </div>
          <span class="quick-name">{{ item.name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {
  IconCalendar,
  IconCheckCircle,
  IconClockCircle,
  IconFile,
  IconIdcard,
  IconRobot,
  IconSound,
  IconStorage,
  IconUser,
  IconVoice
} from '@arco-design/web-vue/es/icon';

defineOptions({
  name: 'Dashboard'
});

const router = useRouter();

// 核心功能配置
const features = ref([
  {
    id: 'recognition',
    title: '语音识别',
    description: '支持实时流式识别和离线文件转写，高准确率的中文语音识别服务',
    icon: IconSound,
    color: '#165DFF',
    lightColor: '#E8F3FF',
    route: 'voiceIdentify',
    actionText: '开始识别',
    secondaryRoute: 'voiceIdentifyOffline',
    secondaryText: '离线转写'
  },
  {
    id: 'voiceprint',
    title: '声纹管理',
    description: '声纹注册与识别，实现说话人身份识别，支持1:1验证和1:N识别',
    icon: IconIdcard,
    color: '#00B42A',
    lightColor: '#E8FFEA',
    route: 'voicePrint',
    actionText: '声纹注册',
    secondaryRoute: null,
    secondaryText: ''
  },
  {
    id: 'meeting',
    title: '会议转写',
    description: '会议音频自动转写，支持多人说话人分离识别，智能匹配参会者身份',
    icon: IconCalendar,
    color: '#722ED1',
    lightColor: '#F5E8FF',
    route: 'meetingOffline',
    actionText: '创建会议',
    secondaryRoute: 'meetingMdt',
    secondaryText: 'MDT会议'
  }
]);

// 统计数据
const stats = ref([
  {
    label: '注册声纹',
    value: 0,
    suffix: '个',
    icon: IconUser,
    color: 'linear-gradient(135deg, #165DFF 0%, #0E42D2 100%)'
  },
  {
    label: '今日识别',
    value: 0,
    suffix: '次',
    icon: IconVoice,
    color: 'linear-gradient(135deg, #F77234 0%, #E65C00 100%)'
  },
  {
    label: '会议总数',
    value: 0,
    suffix: '场',
    icon: IconCalendar,
    color: 'linear-gradient(135deg, #722ED1 0%, #5B1FB8 100%)'
  },
  {
    label: '微调任务',
    value: 0,
    suffix: '个',
    icon: IconRobot,
    color: 'linear-gradient(135deg, #00B42A 0%, #009A29 100%)'
  }
]);

// 快速入口（只保留实际可访问的菜单）
const quickLinks = ref([
  { name: '实时识别', icon: IconVoice, route: 'voiceIdentify', bgColor: '#E8F3FF', iconColor: '#165DFF' },
  { name: '声纹注册', icon: IconIdcard, route: 'voicePrint', bgColor: '#E8FFEA', iconColor: '#00B42A' },
  { name: '离线会议', icon: IconCalendar, route: 'meetingOffline', bgColor: '#F5E8FF', iconColor: '#722ED1' },
  { name: 'MDT会议', icon: IconClockCircle, route: 'meetingMdt', bgColor: '#FFF7E8', iconColor: '#F77234' },
  { name: '在线识别', icon: IconSound, route: 'voiceIdentifyOnline', bgColor: '#E8F7FF', iconColor: '#14C9C9' },
  { name: '模型微调', icon: IconRobot, route: 'finetuneTask', bgColor: '#FFECE8', iconColor: '#F53F3F' },
  { name: '微调语料', icon: IconStorage, route: 'finetuneAudio', bgColor: '#F2F3F5', iconColor: '#86909C' },
  { name: '离线转写', icon: IconCheckCircle, route: 'voiceIdentifyOffline', bgColor: '#E8F3FF', iconColor: '#165DFF' }
]);

// 路由路径映射（与服务端配置的菜单路径保持一致）
const routePathMap: Record<string, string> = {
  voiceIdentify: '/voice/identify',
  voiceIdentifyOnline: '/voice/identify/online',
  voiceIdentifyOffline: '/voice/identify/offline',
  voicePrint: '/voice/print',
  meetingOffline: '/meeting/offline',
  meetingMdt: '/meeting/mdt',
  finetuneTask: '/finetune/task',
  finetuneAudio: '/finetune/audio'
};

// 导航函数
const navigateTo = (routeName: string) => {
  const path = routePathMap[routeName];
  if (path) {
    router.push(path);
  } else {
    router.push({ name: routeName });
  }
};

// 加载统计数据
const loadStats = async () => {
  // TODO: 从后端获取实际统计数据
  stats.value[0].value = 128;
  stats.value[1].value = 1024;
  stats.value[2].value = 56;
  stats.value[3].value = 8;
};

onMounted(() => {
  loadStats();
});
</script>

<style lang="less" scoped>
.home-container {
  min-height: calc(100vh - 60px);
  background: #f7f8fa;
  padding-bottom: 32px;
}

// Hero 区域
.hero-section {
  position: relative;
  padding: 40px 32px;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #165dff 0%, #0e42d2 50%, #722ed1 100%);

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='50' cy='50' r='1' fill='rgba(255,255,255,0.1)'/%3E%3C/svg%3E");
  }
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hero-text {
  flex: 1;
}

.hero-title {
  font-size: 32px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 12px 0;
  letter-spacing: 1px;
}

.hero-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.85);
  margin: 0;
}

.hero-visual {
  margin-left: 40px;
}

.sound-wave {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 60px;

  span {
    display: block;
    width: 6px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 3px;
    animation: soundWave 1s ease-in-out infinite;

    &:nth-child(1) {
      height: 20px;
      animation-delay: 0s;
    }
    &:nth-child(2) {
      height: 35px;
      animation-delay: 0.1s;
    }
    &:nth-child(3) {
      height: 50px;
      animation-delay: 0.2s;
    }
    &:nth-child(4) {
      height: 60px;
      animation-delay: 0.3s;
    }
    &:nth-child(5) {
      height: 50px;
      animation-delay: 0.4s;
    }
    &:nth-child(6) {
      height: 35px;
      animation-delay: 0.5s;
    }
    &:nth-child(7) {
      height: 20px;
      animation-delay: 0.6s;
    }
  }
}

@keyframes soundWave {
  0%,
  100% {
    transform: scaleY(0.5);
    opacity: 0.5;
  }
  50% {
    transform: scaleY(1);
    opacity: 1;
  }
}

// 功能卡片区
.features-section {
  max-width: 1200px;
  margin: -20px auto 0;
  padding: 0 32px;
  position: relative;
  z-index: 2;
}

.feature-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.feature-card {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    transform: translateY(-4px);
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }

  .card-icon {
    width: 44px;
    height: 44px;
    border-radius: 8px;
    background: var(--accent-light);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    color: var(--accent-color);
  }

  .card-title {
    font-size: 18px;
    font-weight: 600;
    color: #1d2129;
    margin: 0;
  }

  .card-desc {
    font-size: 13px;
    color: #86909c;
    line-height: 1.6;
    margin: 0 0 16px 0;
    min-height: 42px;
  }

  .card-actions {
    display: flex;
    gap: 8px;
  }
}

// 统计区
.stats-section {
  max-width: 1200px;
  margin: 24px auto 0;
  padding: 0 32px;
}

.stats-header,
.quick-header {
  margin-bottom: 16px;

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: #1d2129;
    margin: 0;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-item {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 22px;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-value {
  display: flex;
  align-items: baseline;
  gap: 4px;

  :deep(.arco-statistic-value) {
    font-size: 28px;
    font-weight: 600;
    color: #1d2129;
  }
}

.stat-suffix {
  font-size: 14px;
  color: #86909c;
}

.stat-label {
  display: block;
  font-size: 13px;
  color: #86909c;
  margin-top: 4px;
}

// 快速入口区
.quick-section {
  max-width: 1200px;
  margin: 24px auto 0;
  padding: 0 32px;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 12px;
}

.quick-item {
  background: #fff;
  border-radius: 8px;
  padding: 16px 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);

    .quick-icon {
      transform: scale(1.1);
    }
  }
}

.quick-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  transition: all 0.3s ease;
}

.quick-name {
  font-size: 12px;
  color: #4e5969;
  font-weight: 500;
  text-align: center;
  white-space: nowrap;
}

// 响应式适配
@media (max-width: 1200px) {
  .feature-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .quick-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 32px 16px;
  }

  .hero-title {
    font-size: 24px;
  }

  .hero-subtitle {
    font-size: 14px;
  }

  .hero-visual {
    display: none;
  }

  .features-section,
  .stats-section,
  .quick-section {
    padding: 0 16px;
  }

  .feature-cards {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .quick-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
