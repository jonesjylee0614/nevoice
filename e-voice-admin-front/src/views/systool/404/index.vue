<template>
  <div class="container">
    <Breadcrumb :items="['menu.exception', 'menu.exception.404']" />
    <div class="content">
      <AResult class="result" status="404" :subtitle="$t('exception.result.404.description')"></AResult>
      <div class="operation-row">
        <AButton key="again" style="margin-right: 16px" @click="reflast">
          {{ $t('exception.result.404.retry') }}
        </AButton>
        <AButton key="back" type="primary" @click="onback">
          {{ $t('exception.result.404.back') }}
        </AButton>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
defineOptions({
  name: '404'
});

const router = useRouter();
const reload = inject('reload');
// 刷新
const reflast = () => {
  if (typeof reload === 'function') reload();
};
// 返回
const onback = () => {
  router.go(-1);
};
</script>

<style scoped lang="less">
.container {
  padding: 0 20px 20px 20px;
  height: calc(100% - 40px);
  :deep(.content) {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
    background-color: var(--color-bg-1);
    border-radius: 4px;
  }
}
</style>
