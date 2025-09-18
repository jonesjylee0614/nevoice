<template>
  <ACard v-if="formData" class="general-card contentcard">
    <template #title>配置附件地址</template>
    <ARow :gutter="80">
      <ACol :span="18">
        <AFormItem
          label="附件请求路径前缀"
          field="keyvalue"
          extra="示例地址：https://youdomain.cn/common/uploadfile/get_image?url="
        >
          <AInput v-model="formData.keyvalue" placeholder="填写附件请求路径前缀" allow-clear />
        </AFormItem>
      </ACol>
      <ACol :span="24">
        <AFormItem>
          <div class="frombtn">
            <AButton type="primary" html-type="submit" style="width: 120px" @click="submitEmail">保存</AButton>
          </div>
        </AFormItem>
      </ACol>
    </ARow>
  </ACard>
</template>

<script lang="ts" setup>
import { Message } from '@arco-design/web-vue';
import { getConfig, saveConfig } from '@/api/datacenter/common_config';

// 数据配置
const formData = ref({
  keyname: '',
  keyvalue: ''
});
// 保存邮箱
const submitEmail = async () => {
  await saveConfig(formData.value);
  Message.success({ content: '保存成功', id: 'upStatus', duration: 2000 });
};
// 组件挂载完成后执行的函数
onMounted(() => {
  InitData();
});
// 加载数据
const InitData = async () => {
  const emaildata = await getConfig({ keyname: 'rooturl' });
  formData.value = { ...formData.value, ...emaildata };
};
</script>

<style scoped lang="less">
.contentcard {
  overflow: hidden;
}
:deep(.general-card > .arco-card-header) {
  padding: 10px 16px;
}

.frombtn {
  width: 100%;
  text-align: center;
}
</style>
