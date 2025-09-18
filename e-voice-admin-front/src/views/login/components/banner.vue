<template>
  <div class="banner">
    <div class="banner-inner">
      <ACarousel class="carousel" animation-name="fade" :auto-play="{ interval: 5000, hoverToPause: true }">
        <ACarouselItem v-for="item in carouselItem" :key="item.title">
          <div :key="item.title" class="carousel-item">
            <div class="carousel-title">{{ item.title }}</div>
            <div class="carousel-sub-title">{{ item.des }}</div>
            <img class="carousel-image" :src="getDomain() + item.image" />
          </div>
        </ACarouselItem>
      </ACarousel>
    </div>
  </div>
</template>

<script lang="ts" setup>
// api
import { getlogininfo } from '@/api/user';
interface LoginInfo {
  title: string;
  des: string;
  image: string;
}
const carouselItem = ref<LoginInfo[]>([]);
onMounted(async () => {
  carouselItem.value = await getlogininfo({});
});

function getDomain() {
  return import.meta.env.VITE_API_HOST;
}
</script>

<style lang="less" scoped>
.banner {
  display: flex;
  align-items: center;
  justify-content: center;

  &-inner {
    flex: 1;
    height: 100%;
  }
}

.carousel {
  height: 100%;

  &-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
  }

  &-title {
    color: var(--color-fill-1);
    font-weight: 500;
    font-size: 20px;
    line-height: 28px;
  }

  &-sub-title {
    margin-top: 8px;
    color: var(--color-text-3);
    font-size: 14px;
    line-height: 22px;
    padding: 0 15px;
  }

  &-image {
    width: 320px;
    margin-top: 30px;
  }
}
</style>
