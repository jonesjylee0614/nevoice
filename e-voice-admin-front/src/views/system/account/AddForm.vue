<template>
  <BasicModal
    v-bind="attrs"
    :loading="loading"
    help-message="编辑和修改菜单"
    width="800px"
    :min-height="420"
    :title="getTitle"
    @register="registerModal"
    @ok="handleSubmit"
  >
    <AForm ref="formRef" :model="formData" auto-label-width>
      <ARow :gutter="16">
        <ACol :span="12">
          <AFormItem
            field="name"
            label="用户姓名"
            validate-trigger="input"
            :rules="[{ required: true, message: '请填写姓名' }]"
            style="margin-bottom: 15px"
          >
            <AInput v-model="formData.name" placeholder="请填用户姓名" />
          </AFormItem>
        </ACol>
        <ACol :span="12">
          <AFormItem field="nickname" label="昵称" validate-trigger="input" style="margin-bottom: 15px">
            <AInput v-model="formData.nickname" placeholder="请填写昵称" />
          </AFormItem>
        </ACol>
        <ACol :span="12">
          <AFormItem label="选择角色" field="pid" style="margin-bottom: 15px">
            <ATreeSelect
              v-model="formData.roleid"
              allow-search
              allow-clear
              placeholder="选择角色"
              :data="roleList"
              :field-names="{
                key: 'id',
                title: 'name',
                children: 'children'
              }"
              multiple
            ></ATreeSelect>
          </AFormItem>
        </ACol>
        <ACol :span="12">
          <AFormItem field="dept_id" label="选择部门" style="margin-bottom: 15px">
            <ATreeSelect
              v-model="formData.dept_id"
              placeholder="选择部门"
              :data="deptList"
              :field-names="{
                key: 'id',
                title: 'name',
                children: 'children'
              }"
            ></ATreeSelect>
          </AFormItem>
        </ACol>
        <ACol :span="12">
          <AFormItem
            field="username"
            label="登录账号"
            style="margin-bottom: 15px"
            :rules="[{ required: true, message: '请填写账号' }, ...usernameRules]"
            :validate-trigger="['change', 'blur']"
          >
            <AInput v-model="formData.username" placeholder="请填登录账号" />
          </AFormItem>
        </ACol>
        <ACol :span="12">
          <AFormItem field="password" label="登录密码" style="margin-bottom: 15px">
            <AInput v-model="formData.password" placeholder="登录密码(不修改则为空，默认密码123456)" />
          </AFormItem>
        </ACol>
        <ACol :span="12">
          <AFormItem field="mobile" label="手机号码" style="margin-bottom: 15px">
            <AInput v-model="formData.mobile" placeholder="请填手机号码" />
          </AFormItem>
        </ACol>
        <ACol :span="12">
          <AFormItem field="tel" label="座机" style="margin-bottom: 15px">
            <AInput v-model="formData.tel" placeholder="请填座机" />
          </AFormItem>
        </ACol>
        <ACol :span="12">
          <AFormItem field="email" label="邮箱" style="margin-bottom: 15px">
            <AInput v-model="formData.email" placeholder="请填邮箱" />
          </AFormItem>
        </ACol>
        <ACol :span="12">
          <AFormItem field="address" label="地址" style="margin-bottom: 15px">
            <AInput v-model="formData.address" placeholder="请填地址" />
          </AFormItem>
        </ACol>
        <ACol :span="12">
          <AFormItem field="city" label="城市" style="margin-bottom: 15px">
            <AInput v-model="formData.city" placeholder="请填城市" />
          </AFormItem>
        </ACol>
        <ACol :span="12">
          <AFormItem field="company" label="公司" style="margin-bottom: 15px">
            <AInput v-model="formData.company" placeholder="请填公司" />
          </AFormItem>
        </ACol>
        <ACol :span="12">
          <AFormItem field="remark" label="备注" style="margin-bottom: 15px">
            <ATextarea v-model="formData.remark" placeholder="请填备注" />
          </AFormItem>
        </ACol>
        <ACol :span="12">
          <AFormItem field="avatar" label="头像" style="margin-bottom: 15px">
            <AvatarUpload v-model="formData.avatar" />
          </AFormItem>
        </ACol>
      </ARow>
    </AForm>
  </BasicModal>
</template>

<script lang="ts" setup>
import { cloneDeep } from 'lodash-es';
import type { FormInstance } from '@arco-design/web-vue';
import { Message } from '@arco-design/web-vue';
import { randomStr } from '@antfu/utils';
import type { DataItem } from '@/api/system/account';
import { getRole, isAccountexist, save } from '@/api/system/account';
import { getParent } from '@/api/system/dept';
import useLoading from '@/hooks/loading';
import { generateRandomString } from '@/utils/string';
import { BasicModal, useModalInner } from '@/components/Modal';
import AvatarUpload from '@/components/upload/AvatarUpload.vue';

const attrs = useAttrs();
const emit = defineEmits(['success']);
const isUpdate = ref(false);
const roleList = ref<DataItem[]>([]);
const deptList = ref<DataItem[]>([]);
// 表单
const formRef = ref<FormInstance>();
// 表单字段
const basedata = {
  id: 0,
  name: '',
  nickname: '',
  dept_id: 0,
  roleid: [],
  username: '',
  password: '',
  avatar: '',
  tel: '',
  mobile: '', // 手机
  email: '', // 邮箱
  address: '', // 地址
  city: '', // 城市
  remark: '', // 备注
  company: '', // 公司
  appkey: '',
  appKeySecret: ''
};
const formData = ref(basedata);
const [registerModal, { setModalProps, closeModal }] = useModalInner(async data => {
  formRef.value?.resetFields();
  setModalProps({ confirmLoading: false });
  const resultdata = await getRole();
  if (resultdata) {
    roleList.value = resultdata;
  } else {
    roleList.value = [];
  }
  const deptdata = await getParent();
  const parntList_df: any = [{ id: 0, name: '未选部门', pid: 0 }];
  if (deptdata) {
    deptList.value = parntList_df.concat(deptdata);
  } else {
    deptList.value = parntList_df;
  }
  isUpdate.value = Boolean(data?.isUpdate);
  if (unref(isUpdate)) {
    formData.value = cloneDeep(data.record);
  } else {
    formData.value = cloneDeep(basedata);
  }
});
const getTitle = computed(() => (!unref(isUpdate) ? '新增管理账号' : '编辑管理账号'));
// 点击确认
const { loading, setLoading } = useLoading();
const handleSubmit = async () => {
  try {
    const res = await formRef.value?.validate();
    if (!res) {
      setLoading(true);
      if (!unref(isUpdate) && formData.value.password == '') {
        formData.value.password = '123456';
      }
      if (!formData.value.appkey) {
        formData.value.appkey = generateRandomString(16);
      }
      if (!formData.value.appKeySecret) {
        formData.value.appKeySecret = generateRandomString(30);
      }

      await save(unref(formData));
      Message.success({ content: '更新成功', id: 'upStatus' });
      closeModal();
      emit('success');
      setLoading(false);
    }
  } catch (error) {
    setLoading(false);
  }
};
// 验证账号唯一性
const usernameRules = [
  {
    validator: (value: any, cb: any) => {
      return new Promise(async resolve => {
        if (!value) {
          cb('请填写登录账号');
        } else {
          let sdata = { username: value };
          if (formData.value.id > 0) {
            sdata = { ...sdata, id: formData.value.id } as any;
          }
          const resData = await isAccountexist(sdata);
          if (resData.code == 1) {
            cb(resData.message);
          }
        }
        resolve(true);
      });
    }
  }
];
</script>
