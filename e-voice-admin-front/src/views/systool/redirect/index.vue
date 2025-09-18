<template>
  <div></div>
</template>

<script lang="ts" setup>
const router = useRouter();
const route = useRoute();

const gotoPath = route.params.path as string;

router.replace({ path: gotoPath });
</script>

<style scoped lang="less"></style>
