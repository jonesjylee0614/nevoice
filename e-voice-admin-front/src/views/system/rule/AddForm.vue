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
      <AFormItem field="type" label="菜单类型" style="margin-bottom: 15px">
        <ARadioGroup v-model="formData.type" type="button" @change="handleChangeType">
          <ARadio :value="0">目录</ARadio>
          <ARadio :value="1">菜单</ARadio>
          <ARadio :value="2">按钮</ARadio>
        </ARadioGroup>
      </AFormItem>
      <ARow :gutter="16">
        <ACol :span="12">
          <AFormItem
            field="title"
            label="菜单名称"
            validate-trigger="input"
            :rules="[{ required: true, message: '请填写菜单名称' }]"
            style="margin-bottom: 15px"
          >
            <AInput v-model="formData.title" placeholder="请填写菜单名称" />
          </AFormItem>
        </ACol>
        <ACol :span="12">
          <AFormItem field="locale" label="多语言标识" validate-trigger="input" style="margin-bottom: 15px">
            <AInput v-model="formData.locale" placeholder="请填写菜单名称" />
          </AFormItem>
        </ACol>
        <ACol :span="12">
          <AFormItem label="上级菜单" field="pid" style="margin-bottom: 15px">
            <ATreeSelect
              v-model="formData.pid"
              placeholder="选择上级菜单"
              :data="parntList"
              :field-names="{
                key: 'id',
                title: 'title',
                children: 'children'
              }"
            ></ATreeSelect>
          </AFormItem>
        </ACol>
        <ACol :span="12">
          <AFormItem label="排序" field="orderNo" style="margin-bottom: 15px">
            <AInputNumber v-model="formData.orderNo" placeholder="请填排序" />
          </AFormItem>
        </ACol>
        <ACol v-if="formData.type != 2" :span="12">
          <AFormItem label="图标" field="icon" style="margin-bottom: 15px">
            <AInputSearch v-model="formData.icon" placeholder="选择图标/填写" search-button>
              <template v-if="formData.icon" #prefix>
                <Icon :icon="formData.icon" :size="23" />
              </template>
              <template #button-icon>
                <APopover position="bl" trigger="click">
                  <icon-apps />
                  <template #content>
                    <IconPicker
                      @change="
                        (icon: any) => {
                          formData.icon = icon;
                        }
                      "
                    ></IconPicker>
                  </template>
                </APopover>
              </template>
            </AInputSearch>
          </AFormItem>
        </ACol>
        <ACol v-if="formData.type != 2" :span="12">
          <AFormItem
            field="routePath"
            label="路由地址"
            validate-trigger="input"
            :rules="[{ required: true, message: '请填写路由地址' }]"
            style="margin-bottom: 15px"
          >
            <AInput v-model="formData.routePath" placeholder="路由地址，如果为外链请填写http://xxx.xxx.xxx" />
          </AFormItem>
        </ACol>
        <ACol v-if="formData.type != 2" :span="12">
          <AFormItem
            field="routeName"
            label="路由名称"
            validate-trigger="input"
            :rules="[{ required: true, message: '请填写路由名称' }]"
            style="margin-bottom: 15px"
          >
            <AInput v-model="formData.routeName" placeholder="路由名称（name）" />
          </AFormItem>
        </ACol>
        <ACol v-if="formData.type == 0" :span="12">
          <AFormItem
            field="redirect"
            label="重定向地址"
            validate-trigger="input"
            :rules="[{ required: true, message: '请填写重定向地址' }]"
          >
            <AInput v-model="formData.redirect" placeholder="重定向地址（redirect）" />
          </AFormItem>
        </ACol>
        <ACol v-if="formData.type == 1" :span="12">
          <AFormItem
            field="component"
            label="组件路径"
            validate-trigger="input"
            :rules="[{ required: true, message: '请填写组件路径' }]"
          >
            <AInput v-model="formData.component" placeholder="组件路径（component）" />
          </AFormItem>
        </ACol>
        <ACol v-if="formData.type == 2" :span="12">
          <AFormItem
            field="permission"
            label="权限标识"
            validate-trigger="input"
            :rules="[{ required: true, message: '请填写权限标识' }]"
          >
            <AInput v-model="formData.permission" :placeholder="permPlaceholder" />
          </AFormItem>
        </ACol>
        <ACol v-if="formData.type != 2" :span="12">
          <AFormItem field="isExt" label="是否外链" style="margin-bottom: 5px">
            <ARadioGroup v-model="formData.isExt" :options="OYoptions" />
          </AFormItem>
        </ACol>
        <ACol v-if="formData.type != 2" :span="12">
          <AFormItem field="keepalive" label="是否缓存" style="margin-bottom: 5px">
            <ARadioGroup v-model="formData.keepalive" :options="OYoptions" />
          </AFormItem>
        </ACol>
        <ACol v-if="formData.type != 2" :span="12">
          <AFormItem field="hideInMenu" label="左侧菜单中隐藏" style="margin-bottom: 5px">
            <ARadioGroup v-model="formData.hideInMenu" :options="OYoptions" />
          </AFormItem>
        </ACol>
        <ACol v-if="formData.type != 2" :span="12">
          <AFormItem field="hideChildrenInMenu" label="隐藏子菜单" style="margin-bottom: 5px">
            <ARadioGroup v-model="formData.hideChildrenInMenu" :options="OYoptions" />
          </AFormItem>
        </ACol>
        <ACol v-if="formData.type != 2" :span="12">
          <AFormItem field="noAffix" label="添加到标签中" style="margin-bottom: 5px">
            <ARadioGroup v-model="formData.noAffix" :options="OYoptions" />
          </AFormItem>
        </ACol>
        <ACol v-if="formData.type != 2" :span="12">
          <AFormItem field="activeMenu" label="高亮设置的菜单" style="margin-bottom: 5px">
            <ARadioGroup v-model="formData.activeMenu" :options="OYoptions" />
          </AFormItem>
        </ACol>
        <ACol v-if="formData.type != 2" :span="12">
          <AFormItem field="requiresAuth" label="是否需要登录鉴权" style="margin-bottom: 5px">
            <ARadioGroup v-model="formData.requiresAuth" :options="OYoptions" />
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
import type { RuleItem } from '@/api/system/rule';
import { getParent, save } from '@/api/system/rule';
import useLoading from '@/hooks/loading';
import { BasicModal, useModalInner } from '@/components/Modal';
import { Icon, IconPicker } from '@/components/Icon';

const attrs = useAttrs();

const permPlaceholder = `权限标识（ v-permission="['admin','guest']" 或 v-perm="['admin']" ）`;
const emit = defineEmits(['success']);

const isUpdate = ref(false);
const parntList = ref<RuleItem[]>([]);
// 表单
const formRef = ref<FormInstance>();
// 表单字段
const basedata = {
  id: 0,
  title: '',
  locale: '',
  orderNo: 1,
  type: 0,
  pid: 0,
  icon: '',
  status: 0,
  routePath: '', // path
  routeName: '', // name
  component: '', // 外部layar、import
  redirect: '', // 重定向
  permission: '', // 页面内权限 roles
  isExt: 0, // 是否外链
  keepalive: 0, // 是否缓存 0=否1=是
  requiresAuth: 1, // 是否需要登录鉴权 默认false
  hideInMenu: 0, // 是否在左侧菜单中隐藏该项
  hideChildrenInMenu: 0, // 强制在左侧菜单中显示单项
  activeMenu: 0, // 高亮设置的菜单项
  noAffix: 0 // 如果设置为true，标签将不会添加到tab-bar中
};
const formData = ref(basedata);
const m_component = ref('');
const [registerModal, { setModalProps, closeModal }] = useModalInner(async data => {
  formRef.value?.resetFields();
  setModalProps({ confirmLoading: false });
  isUpdate.value = Boolean(data?.isUpdate);
  const resultdata = await getParent({
    id: unref(isUpdate) ? data.record.id : 0
  });
  const parntList_df: any = [{ id: 0, title: '一级菜单', pid: 0, locale: '' }];
  if (resultdata) {
    parntList.value = parntList_df.concat(resultdata);
  } else {
    parntList.value = parntList_df;
  }
  if (isUpdate.value) {
    m_component.value = data.record.component;
    formData.value = cloneDeep(data.record);
  } else {
    m_component.value = '';
    const r = cloneDeep(basedata);
    if (data.record) {
      Object.assign(r, data.record);
    }
    formData.value = r;
  }
});
const getTitle = computed(() => (!unref(isUpdate) ? '新增系统菜单' : '编辑系统菜单'));
// 点击确认
const { loading, setLoading } = useLoading();
const handleSubmit = async () => {
  try {
    const res = await formRef.value?.validate();
    if (!res) {
      setLoading(true);
      if (formData.value.type == 0 && formData.value.component == '') {
        formData.value.component = 'LAYOUT';
      }
      if (formData.value.type == 0 && formData.value.routePath && formData.value.routePath.substring(0, 1) != '/') {
        formData.value.routePath = `/${formData.value.routePath}`;
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
// 切换菜单类型
const handleChangeType = (value: any) => {
  if (value == 0) {
    formData.value.component = 'LAYOUT';
  } else if (value == 1) {
    formData.value.component = m_component.value;
    formData.value.redirect = '';
  } else if (value == 2) {
    formData.value.component = '';
    formData.value.redirect = '';
  }
};

const OYoptions = [
  { label: '否', value: 0 },
  { label: '是', value: 1 }
];
</script>
