<template>
  <ACard :bordered="false">
    <ASpace :size="54">
      <AvatarUpload v-model="userStore.avatar!" @success="saveAvatar" />
      <ADescriptions
        :data="renderData"
        :column="2"
        align="right"
        layout="inline-horizontal"
        :label-style="{
          width: '140px',
          fontWeight: 'normal',
          color: 'rgb(var(--gray-8))'
        }"
        :value-style="{
          width: '200px',
          paddingLeft: '8px',
          textAlign: 'left'
        }"
      >
        <template #label="{ label }">{{ $t(label) }} :</template>
        <template #value="{ value, data }">
          <ATag v-if="data.label === 'userSetting.label.certification'" color="green" size="small">已认证</ATag>
          <span v-else-if="data.label == 'userSetting.label.phone'">
            {{ phoneFilter(value) }}
          </span>
          <span v-else>{{ value }}</span>
        </template>
      </ADescriptions>
    </ASpace>
  </ACard>
</template>

<script lang="ts" setup>
import type { DescData } from '@arco-design/web-vue/es/descriptions/interface';
import type { BasicInfoModel } from '@/api/user-center';
import { saveInfo } from '@/api/user-center';
import { useUserStore } from '@/store';
import AvatarUpload from '@/components/upload/AvatarUpload.vue';

interface Props {
  formData?: BasicInfoModel;
}
const props = withDefaults(defineProps<Props>(), {
  formData: {} as any
});
const userStore = useUserStore();

const renderData = ref();
watch(
  () => props.formData,
  () => {
    renderData.value = [
      {
        label: 'userSetting.label.name',
        value: userStore.name
      },
      {
        label: 'userSetting.label.certification',
        value: 1
      },
      {
        label: 'userSetting.label.accountId',
        value: props.formData.id
      },
      {
        label: 'userSetting.label.phone',
        value: props.formData.mobile
      },
      {
        label: 'userSetting.label.registrationDate',
        value: props.formData.createTime
        // value:props.formData.createTime,
      }
    ] as DescData[];
  }
);
// 手机号过滤器
const phoneFilter = (val: string) => {
  const reg = /^(.{3}).*(.{4})$/;
  return val.replace(reg, '$1****$2');
};

const saveAvatar = async (url: string) => {
  await saveInfo({ avatar: url });
};
</script>

<style scoped lang="less">
.arco-card {
  padding: 14px 0 4px 4px;
  border-radius: 4px;
}
:deep(.arco-avatar-trigger-icon-button) {
  width: 32px;
  height: 32px;
  line-height: 32px;
  background-color: #e8f3ff;
  .arco-icon-camera {
    margin-top: 8px;
    color: rgb(var(--arcoblue-6));
    font-size: 14px;
  }
}
</style>
