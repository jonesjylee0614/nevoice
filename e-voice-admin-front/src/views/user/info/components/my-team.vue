<template>
  <ACard
    class="general-card"
    :title="$t('userInfo.tab.title.team')"
    :header-style="{ paddingBottom: '18px' }"
    :body-style="{ paddingBottom: '12px' }"
  >
    <AList :bordered="false">
      <AListItem v-for="team in teamList" :key="team.id" action-layout="horizontal">
        <ASkeleton v-if="loading" :loading="loading" :animation="true">
          <ARow :gutter="6">
            <ACol :span="6">
              <ASkeletonShape shape="circle" />
            </ACol>
            <ACol :span="16">
              <ASkeletonLine :widths="['100%', '40%']" :rows="2" />
            </ACol>
          </ARow>
        </ASkeleton>
        <AListItemMeta v-else :title="team.name">
          <template #avatar>
            <AAvatar>
              <img :src="team.avatar" alt="" />
            </AAvatar>
          </template>
          <template #description>共{{ team.peopleNumber }}人</template>
        </AListItemMeta>
      </AListItem>
    </AList>
  </ACard>
</template>

<script lang="ts" setup>
import type { MyTeamRecord } from '@/api/user-center';
import { queryMyTeamList } from '@/api/user-center';
import useRequest from '@/hooks/request';

const defaultValue: MyTeamRecord[] = Array.from({ length: 4 }).fill({});
const { loading, response: teamList } = useRequest<MyTeamRecord[]>(queryMyTeamList, defaultValue);
</script>

<style scoped lang="less">
.general-card {
  height: 356px;
  .arco-list-item {
    height: 72px;
    padding-left: 0;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--color-neutral-3);
    &:last-child {
      border-bottom: none;
    }
    .arco-list-item-meta {
      padding: 0;
    }
  }
}
</style>
