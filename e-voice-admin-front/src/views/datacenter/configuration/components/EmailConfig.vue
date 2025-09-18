<template>
  <ACard class="general-card contentcard">
    <template #title>配置邮箱</template>
    <ARow :gutter="80">
      <ACol :span="12">
        <AFormItem label="发送者邮箱" field="sender_email">
          <AInput v-model="formEmail.sender_email" placeholder="填写发送者邮箱" allow-clear />
        </AFormItem>
      </ACol>
      <ACol :span="12">
        <AFormItem label="邮箱授权码" field="auth_code">
          <AInput v-model="formEmail.auth_code" placeholder="填写邮箱授权码" allow-clear />
        </AFormItem>
      </ACol>
      <ACol :span="12">
        <AFormItem label="邮件服务器" field="service_host">
          <AInput v-model="formEmail.service_host" placeholder="填写邮件服务器" allow-clear />
        </AFormItem>
      </ACol>
      <ACol :span="12">
        <AFormItem label="邮件服务器端口" field="service_port">
          <AInput v-model="formEmail.service_port" placeholder="填写邮件服务器端口" allow-clear />
        </AFormItem>
      </ACol>
      <ADivider orientation="center" style="width: 100%">发送邮箱验证码</ADivider>
      <ACol :span="16">
        <AFormItem label="（验证码）邮件标题" field="mail_title">
          <AInput v-model="formEmail.mail_title" placeholder="填写邮件标题" allow-clear />
        </AFormItem>
      </ACol>
      <ACol :span="24">
        <AFormItem label="（验证码）邮件内容" field="mail_body" extra="{code} 会替换成动态验证码">
          <ATextarea
            v-model="formEmail.mail_body"
            placeholder="填写邮件内容"
            allow-clear
            :auto-size="{ minRows: 3, maxRows: 5 }"
          />
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
import { getEmail, saveEmail } from '@/api/datacenter/configuration';

// 邮箱配置
const formEmail = ref({
  sender_email: '',
  auth_code: '',
  mail_title: '',
  mail_body: '',
  service_host: '',
  service_port: ''
});
// 保存邮箱
const submitEmail = async () => {
  await saveEmail(formEmail.value);
  Message.success({ content: '保存邮箱成功', id: 'upStatus', duration: 2000 });
};
// 组件挂载完成后执行的函数
onMounted(() => {
  InitData();
});
// 加载数据
const InitData = async () => {
  const emaildata = await getEmail({});
  formEmail.value = { ...formEmail.value, ...emaildata };
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
