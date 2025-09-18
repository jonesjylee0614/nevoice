<template>
  <div class="container">
    <Breadcrumb :items="['menu.user', 'menu.user.setting']" />
    <ARow style="margin-bottom: 16px">
      <ACol :span="24">
        <UserPanel :loading="loading" :form-data="formData" />
      </ACol>
    </ARow>
    <ARow class="wrapper">
      <ACol :span="24">
        <ATabs default-active-key="1" type="rounded">
          <ATabPane key="1" title="基础设置">
            <BasicInformation :loading="loading" :form-data="formData" />
          </ATabPane>
          <ATabPane key="2" title="安全设置">
            <SecuritySettings :loading="loading" :form-data="formData" />
          </ATabPane>
          <ATabPane key="3" title="APPKEY管理">
            <ApiSettings :loading="loading" :form-data="formData" />
          </ATabPane>
          <!--          <ATabPane key="4" title="SDK">-->
          <!--            <SdkView :loading="loading" :form-data="formData" />-->
          <!--          </ATabPane>-->
          <!--
 <a-tab-pane key="3" :title="$t('userSetting.tab.certification')">
            <Certification />
          </a-tab-pane>
-->
        </ATabs>
      </ACol>
    </ARow>
  </div>
</template>

<script lang="ts" setup>
import type { BasicInfoModel } from '@/api/user-center';
import { getUser } from '@/api/user-center';
import useLoading from '@/hooks/loading';
import ApiSettings from '@/views/user/setting/components/api-settings.vue';
import SdkView from '@/views/user/setting/components/sdk-view.vue';
import UserPanel from './components/user-panel.vue';
import BasicInformation from './components/basic-information.vue';
import SecuritySettings from './components/security-settings.vue';
defineOptions({
  name: 'Setting'
});

const formData = ref<BasicInfoModel>({
  id: 0,
  nickname: '',
  email: '',
  mobile: '',
  remark: '',
  company: '',
  country: '',
  province: '',
  city: '',
  area: '',
  address: '',
  createTime: ''
});
const { loading, setLoading } = useLoading(true);
const fetchData = async () => {
  try {
    formData.value = await getUser();
  } catch (err) {
    // you can report use errorHandler or other
  } finally {
    setLoading(false);
  }
};
fetchData();
</script>

<style scoped lang="less">
.wrapper {
  padding: 20px;
  min-height: 580px;
  background-color: var(--color-bg-2);
  border-radius: 4px;
}

:deep(.section-title) {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 14px;
}
</style>
