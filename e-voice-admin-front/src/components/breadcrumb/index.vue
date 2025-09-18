<template>
  <ABreadcrumb class="container-breadcrumb">
    <ABreadcrumbItem>
      <icon-apps />
    </ABreadcrumbItem>
    <ABreadcrumbItem v-for="item in items" :key="item">
      {{ $t(item) }}
    </ABreadcrumbItem>
  </ABreadcrumb>
</template>

<script lang="ts" setup>
interface Props {
  items: string[];
}
defineProps<Props>();
</script>

<style scoped lang="less">
.container-breadcrumb {
  margin: 16px 0;
  :deep(.arco-breadcrumb-item) {
    color: rgb(var(--gray-6));
    &:last-child {
      color: rgb(var(--gray-8));
    }
  }
}
</style>
