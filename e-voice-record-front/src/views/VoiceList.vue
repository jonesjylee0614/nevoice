<template>
<!--    <van-nav-bar-->
<!--            title="录音列表"-->
<!--            left-text="返回"-->
<!--            left-arrow-->
<!--            @click-left="onClickLeft"-->
<!--    />-->

    <van-nav-bar
            title="录音列表"
    />

  <div class="voice-list">
    <van-cell-group inset class="list">
      <van-cell v-for="item in sentences"
                :key="item.id"
                class="list-item sentence"
                 :title="item.txt" is-link/>
    </van-cell-group>

    <van-button type="success" size="large" @click="goToRecord()">新增</van-button>

<!--    <van-button type="success" size="large">提交</van-button>-->
  </div>

</template>

<script setup>

import { setLimitedToken } from '@/service/request'
import {getUserInfo, getUserPrints} from "@/views/api/voice.js";

const router = useRouter()
const sentences = ref([])

const goToRecord = (id) => {
  router.push(`/voice-record/rec`)
}

const loadSentences = async (userId) => {
  const {data} = await getUserPrints(userId)
    console.log(data)
  sentences.value = data.data.items
}

const onClickLeft = () => history.back();

onMounted(async () => {
    // 检查URL中是否有token参数
    const token = router.currentRoute.value.query.token
    if (token) {
        // 设置全局token
        setLimitedToken(token)
    }

  // 获取用户信息
    try {
        const {data} = await getUserInfo()
        console.log(data)
        if  (data.data.userId){
           await loadSentences(data.data.userId)
        }

    }catch(e){
        console.log(e)
    }


})

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