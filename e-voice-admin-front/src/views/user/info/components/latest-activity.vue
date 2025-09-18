<template>
  <ACard class="general-card" :title="$t('userInfo.title.latestActivity')">
    <template #extra>
      <ALink>{{ $t('userInfo.viewAll') }}</ALink>
    </template>
    <AList :bordered="false">
      <AListItem v-for="activity in activityList" :key="activity.id" action-layout="horizontal">
        <ASkeleton v-if="loading" :loading="loading" :animation="true" class="skeleton-item">
          <ARow :gutter="6">
            <ACol :span="2">
              <ASkeletonShape shape="circle" />
            </ACol>
            <ACol :span="22">
              <ASkeletonLine :widths="['40%', '100%']" :rows="2" />
            </ACol>
          </ARow>
        </ASkeleton>
        <AListItemMeta v-else :title="activity.title" :description="activity.description">
          <template #avatar>
            <AAvatar>
              <img :src="activity.avatar" alt="" />
            </AAvatar>
          </template>
        </AListItemMeta>
      </AListItem>
    </AList>
  </ACard>
</template>

<script lang="ts" setup>
import type { LatestActivity } from '@/api/user-center';
import { queryLatestActivity } from '@/api/user-center';
import useLoading from '@/hooks/loading';

const { loading, setLoading } = useLoading(true);
const fill = Array.from({ length: 7 }).fill({}) as any;
const activityList = ref<LatestActivity[]>(fill);
const fetchData = async () => {
  try {
    activityList.value = await queryLatestActivity();
  } catch (err) {
    // you can report use errorHandler or other
  } finally {
    setLoading(false);
  }
};
fetchData();
</script>

<style scoped lang="less">
.latest-activity {
  &-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
}
.general-card :deep(.arco-list-item) {
  padding-left: 0;
  border-bottom: none;
  .arco-list-item-meta-content {
    flex: 1;
    padding-bottom: 27px;
    border-bottom: 1px solid var(--color-neutral-3);
  }
  .arco-list-item-meta-avatar {
    padding-bottom: 27px;
  }
  .skeleton-item {
    margin-top: 10px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--color-neutral-3);
  }
}
</style>
