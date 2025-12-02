<template>
  <van-nav-bar
      title="录音列表"
      left-text="返回"
      left-arrow
      @click-left="onClickLeft"
  />

  <div class="voice-list">
    <van-cell-group inset class="list">
      <van-cell v-for="item in sentences"
                :key="item.id"
                class="list-item sentence"
                @click="goToRecord(item.id)" :title="item.text" :value="item.id" is-link/>
    </van-cell-group>

    <van-button type="success" size="large">提交</van-button>
  </div>

</template>

<script setup>

import {getUserInfo} from "@/views/api/voice.js";

const router = useRouter()
const sentences = ref([
  {
    id: 1,
    text: '例句1'
  },
  {
    id: 2,
    text: '例句2'
  },
  // 更多示例句子...
])

const goToRecord = (id) => {
  router.push(`/voice-record/${id}`)
}

const onClickLeft = () => history.back();

// 判断url中是否有token参数，有的话就获取参数并请求用户信息
if (router.currentRoute.value.query.token) {
    const token = router.currentRoute.value.query.token
    const data = await getUserInfo(token)
    console.log(data)
}

</script>

<style scoped>
.voice-list {
  padding: 0.3rem;
  box-sizing: border-box;
}

.page-title {
  font-size: 1.5rem;
  margin: 1rem 0;
  padding: 0 0.5rem;
  color: #333;
}

.list {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 1rem;
}

.list-item {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: background-color 0.3s;
  -webkit-tap-highlight-color: transparent;
}

.list-item:last-child {
  border-bottom: none;
}

.sentence {
  flex: 1;
  font-size: 1rem;
  color: #333;
}

.arrow {
  font-size: 1.5rem;
  color: #999;
  margin-left: 1rem;
}

.list-item:active {
  background-color: #f5f5f5;
}

@media (hover: hover) {
  .list-item:hover {
    background-color: #f5f5f5;
  }
}

@media (max-width: 480px) {
  .voice-list {
    padding: 0.2rem;
  }

  .list {
    border-radius: 8px;
  }

  .page-title {
    font-size: 1.25rem;
  }
}
</style> 