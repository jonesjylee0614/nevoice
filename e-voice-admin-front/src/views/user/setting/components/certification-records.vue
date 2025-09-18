<template>
  <ACard class="general-card" :title="$t('userSetting.certification.title.record')" :header-style="{ border: 'none' }">
    <ATable v-if="renderData.length" :data="renderData">
      <template #columns>
        <ATableColumn :title="$t('userSetting.certification.columns.certificationType')">
          <template #cell>
            {{ $t('userSetting.certification.cell.certificationType') }}
          </template>
        </ATableColumn>
        <ATableColumn
          :title="$t('userSetting.certification.columns.certificationContent')"
          data-index="certificationContent"
        />
        <ATableColumn :title="$t('userSetting.certification.columns.status')">
          <template #cell="{ record }">
            <p v-if="record.status === 0">
              <span class="circle"></span>
              <span>{{ $t('userSetting.certification.cell.auditing') }}</span>
            </p>
            <p v-if="record.status === 1">
              <span class="circle pass"></span>
              <span>{{ $t('userSetting.certification.cell.pass') }}</span>
            </p>
          </template>
        </ATableColumn>
        <ATableColumn :title="$t('userSetting.certification.columns.time')" data-index="time" />
        <ATableColumn :title="$t('userSetting.certification.columns.operation')">
          <template #cell="{ record }">
            <ASpace>
              <AButton type="text">
                {{ $t('userSetting.certification.button.check') }}
              </AButton>
              <AButton v-if="record.status === 0" type="text">
                {{ $t('userSetting.certification.button.withdraw') }}
              </AButton>
            </ASpace>
          </template>
        </ATableColumn>
      </template>
    </ATable>
  </ACard>
</template>

<script lang="ts" setup>
import type { CertificationRecord } from '@/api/user-center';

interface Props {
  renderData?: CertificationRecord;
}

withDefaults(defineProps<Props>(), {
  renderData: [] as any
});
</script>

<style scoped lang="less">
:deep(.arco-table-th) {
  &:last-child {
    .arco-table-th-item-title {
      margin-left: 16px;
    }
  }
}
</style>
