<template>
  <ADrawer :width="720" :visible="showDrawer" unmount-on-close @ok="handleSubmit" @cancel="handleCancel">
    <template #title>{{ getTitle }}</template>
    <div class="drawer-box">
      <AForm ref="formRef" :model="formData" auto-label-width>
        <AFormItem
          field="name"
          label="角色名称"
          validate-trigger="input"
          :rules="[{ required: true, message: '请填写角色名称' }]"
          style="margin-bottom: 15px"
        >
          <AInput v-model="formData.name" placeholder="请填写角色名称" allow-clear />
        </AFormItem>
        <AFormItem label="上级菜单" field="pid" style="margin-bottom: 15px">
          <ATreeSelect
            v-model="formData.pid"
            placeholder="选择上级菜单"
            :data="parentList"
            :field-names="{
              key: 'id',
              title: 'name',
              children: 'children'
            }"
          ></ATreeSelect>
        </AFormItem>
        <AFormItem field="remark" label="备注" validate-trigger="input" style="margin-bottom: 15px">
          <ATextarea v-model="formData.remark" placeholder="请填写备注" allow-clear />
        </AFormItem>
        <AFormItem field="data_access" label="数据权限" style="margin-bottom: 5px">
          <ARadioGroup v-model="formData.data_access" :options="OYoptions" />
        </AFormItem>
        <AFormItem field="menu" label="菜单分配" style="margin-bottom: 5px">
          <div class="rule_data">
            <div class="haeder">
              <ACheckbox v-if="!isRules" v-model="IsChecked" style="margin-right: 15px" @change="toggleChecked">
                {{ IsChecked ? '取消' : '全选' }}
              </ACheckbox>
              <ACheckbox v-model="onExpanded" @change="toggleExpanded">{{ onExpanded ? '收起' : '展开' }}</ACheckbox>
            </div>
            <div class="treebox">
              <ATree
                ref="ruleTreeRef"
                checked-strategy="all"
                :checked-keys="formData.menu"
                :show-line="true"
                :checkable="!isRules"
                :field-names="{
                  key: 'id',
                  title: 'title',
                  children: 'children'
                }"
                :data="menutreeData"
                @check="onCheck"
              />
            </div>
          </div>
        </AFormItem>
      </AForm>
    </div>
  </ADrawer>
</template>

<script lang="ts" setup>
import { cloneDeep } from 'lodash-es';
import type { FormInstance } from '@arco-design/web-vue';
import { Message } from '@arco-design/web-vue';
// api
import type { RuleItem } from '@/api/system/role';
import { getMenuList, getParent, save } from '@/api/system/role';
import useLoading from '@/hooks/loading';
import type { TreeItem } from './data';

const emit = defineEmits(['success']);

const showDrawer = ref(false);
const isUpdate = ref(false);
const parentList = ref<RuleItem[]>([]);

// 表单
const formRef = ref<FormInstance>();
// 表单字段
const basedata = {
  id: 0,
  pid: 0,
  name: '',
  remark: '',
  menu: [], // 选择的id，用于编辑赋值
  weigh: 1,
  data_access: 0
};
const formData = ref<any>(basedata);
// 菜单权限
const isRules = ref(false);
const IsChecked = ref(false);
const onExpanded = ref(false);
const ruleTreeRef = ref();
const menutreeData = ref<TreeItem[]>([]);
// 打开弹框
const openDrawer = async (item: any) => {
  isUpdate.value = Boolean(item?.isUpdate);
  showDrawer.value = true;
  formRef.value?.resetFields();
  const resultdata = await getParent();
  if (resultdata && resultdata.length > 0) {
    parentList.value = resultdata;
    const parntList_df: any = [{ id: 0, name: '一级角色', pid: 0, locale: '' }];
    parentList.value = parntList_df.concat(resultdata);

    if (!unref(isUpdate)) {
      formData.value.pid = resultdata[0].id;
    }
  } else {
    parentList.value = [];
  }
  if (unref(isUpdate)) {
    formData.value = cloneDeep(item.record);
    const menuarr = cloneDeep(item.record.menu);
    isRules.value = item.record.rules == '*';
    if (menuarr == '*') {
      formData.value.menu = [];
      nextTick().then(() => {
        setTimeout(() => {
          if (ruleTreeRef.value) ruleTreeRef.value.checkAll(true);
        }, 800);
      });
    } else if (formData.value.menu && menuarr != '*') {
      formData.value.menu = JSON.parse(menuarr);
    }
  } else {
    formData.value = cloneDeep(basedata);
  }
  // 获取菜单
  const id = unref(isUpdate) ? item.record.id : 0;
  const pid = unref(isUpdate) ? item.record.pid : 0;
  menutreeData.value = (await getMenuList({ id, pid })) as any as TreeItem[];
  nextTick().then(() => {
    onExpanded.value = true;
    ruleTreeRef.value.expandAll(onExpanded.value);
  });
};
const getTitle = computed(() => (!unref(isUpdate) ? '新增角色菜单' : '编辑角色菜单'));
// 点击确认
const { toggle } = useLoading();
const handleSubmit = async () => {
  try {
    const res = await formRef.value?.validate();
    if (!res) {
      toggle();
      await save(unref(formData));
      Message.success({ content: '数据提交成功', id: 'upStatus' });
      emit('success');
      showDrawer.value = false;
      toggle();
    }
  } catch (error) {
    toggle();
  }
};
const handleCancel = () => {
  showDrawer.value = false;
};
// 权限菜单
// 全选
const toggleChecked = (value: any) => {
  ruleTreeRef.value.checkAll(value);
};
// 展开
const toggleExpanded = (value: any) => {
  ruleTreeRef.value.expandAll(value);
};
// 选中
const onCheck = (newCheckedKeys: any, event: any) => {
  formData.value.menu = newCheckedKeys;
};

const OYoptions = [
  { label: '自己', value: 0 },
  { label: '自己及子权限', value: 1 },
  { label: '全部', value: 2 }
];

defineExpose({ openDrawer });
</script>

<style lang="less" scoped>
.drawer-box {
  .rule_data {
    width: 100%;
    .haeder {
      border-bottom: var(--color-neutral-4) solid 1px;
    }
  }
}
.treebox {
  max-height: 300px;
}
</style>
