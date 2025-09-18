<template>
  <RouterView v-slot="{ Component, route }">
    <Transition name="fade" mode="out-in" appear>
      <component :is="Component" v-if="route.meta.ignoreCache" :key="route.fullPath" />
      <KeepAlive v-else :include="cacheList">
        <component :is="Component" :key="route.fullPath" />
      </KeepAlive>
    </Transition>
  </RouterView>
</template>

<script lang="ts" setup>
import { useTabBarStore } from '@/store';

const tabBarStore = useTabBarStore();

const cacheList = computed(() => tabBarStore.getCacheList);
</script>

<style scoped lang="less"></style>
