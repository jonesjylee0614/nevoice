<template>
  <div class="container">
    <Breadcrumb :items="['menu.system', 'system.role']" />
    <ACard class="general-card oneLineCard" style="height: calc(100% - 50px)">
      <ARow style="margin-bottom: 10px">
        <ACol :span="16">
          <ASpace>
            <AInput v-model="formModel.name" :style="{ width: '220px' }" placeholder="标题" allow-clear />
            <ARangePicker v-model="formModel.createdTime" :style="{ width: '200px' }" />
            <ASelect
              v-model="formModel.status"
              :options="statusOptions"
              placeholder="状态"
              :style="{ width: '120px' }"
            />
            <AButton type="primary" @click="search">
              <template #icon>
                <icon-search />
              </template>
              查询
            </AButton>
            <AButton @click="reset">
              {{ $t('searchTable.form.reset') }}
            </AButton>
          </ASpace>
        </ACol>
        <ACol :span="8" style="text-align: right">
          <ASpace>
            <AButton v-perm="[perms.edit]" type="primary" @click="handleCreate">
              <template #icon>
                <icon-plus />
              </template>
              {{ $t('searchTable.operation.create') }}
            </AButton>
            <ATooltip :content="$t('searchTable.actions.refresh')">
              <div class="action-icon" @click="search"><icon-refresh size="18" /></div>
            </ATooltip>
          </ASpace>
        </ACol>
      </ARow>
      <ATable
        ref="artable"
        row-key="id"
        :loading="loading"
        :pagination="false"
        :columns="cloneColumns as TableColumnData[]"
        :data="renderData"
        :bordered="{ wrapper: true, cell: true }"
        :size="size"
        :default-expand-all-rows="true"
        @change="handleChange"
      >
        <template #title="{ record }">
          <span style="padding-right: 5px; color: var(--color-neutral-4)" v-html="record.spacer"></span>
          {{ record.name }}
        </template>
        <template #icon="{ record }">
          <Icon :icon="record.icon" :size="20" />
        </template>
        <template #createTime="{ record }">
          {{ dayjs(record.createTime).format('YYYY-MM-DD') }}
        </template>
        <template #status="{ record }">
          <ASwitch
            v-model="record.status"
            v-perm="[perms.upStatus]"
            type="round"
            :checked-value="0"
            :unchecked-value="1"
            @change="handleStatus(record)"
          >
            <template #checked>开</template>
            <template #unchecked>关</template>
          </ASwitch>
        </template>
        <template #operations="{ record }">
          <ASpace class="option">
            <Icon v-perm="[perms.edit]" icon="icon-edit" color="rgb(var(--primary-6))" @click="handleEdit(record)" />
            <APopconfirm v-perm="[perms.del]" content="您确定要删除吗?" @ok="handleDel(record)">
              <Icon icon="icon-delete" :size="18" color="#ed6f6f" />
            </APopconfirm>
          </ASpace>
        </template>
      </ATable>
    </ACard>
    <!--表单-->
    <AddDrawer ref="AddFormRef" @success="handleData" />
  </div>
</template>

<script lang="ts" setup>
import dayjs from 'dayjs';
import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';
import type { SelectOptionData } from '@arco-design/web-vue/es/select/interface';
import cloneDeep from 'lodash/cloneDeep';
import { Message } from '@arco-design/web-vue';
import { del, getList, upStatus } from '@/api/system/role';
import useLoading from '@/hooks/loading';
import { Icon } from '@/components/Icon';
import AddDrawer from './AddDrawer.vue';
import { columns } from './data';
defineOptions({
  name: 'Role'
});
const perms = {
  del: 'role:del',
  edit: 'role:edit',
  upStatus: 'role:upStatus'
};
type SizeProps = 'mini' | 'small' | 'medium' | 'large';
type Column = TableColumnData & { checked?: true };
const { loading, setLoading } = useLoading(true);
const AddFormRef = ref();
const renderData = ref([]);
const cloneColumns = ref<Column[]>([]);
const showColumns = ref<Column[]>([]);
const size = ref<SizeProps>('large');
// 查询字段
const generateFormModel = () => {
  return {
    trade_no: '',
    name: '',
    createdTime: [],
    status: ''
  };
};
const formModel = ref(generateFormModel());
const artable = ref();
const fetchData = async () => {
  setLoading(true);
  try {
    const data = await getList(formModel.value);
    renderData.value = data;
    nextTick(() => {
      artable.value.expandAll();
    });
  } catch (err) {
    // you can report use errorHandler or other
  } finally {
    setLoading(false);
  }
};

const search = () => {
  fetchData();
};
const reset = () => {
  formModel.value = generateFormModel();
  fetchData();
};
fetchData();

watch(
  () => columns.value,
  val => {
    cloneColumns.value = cloneDeep(val);
    cloneColumns.value.forEach((item, index) => {
      item.checked = true;
    });
    showColumns.value = cloneDeep(cloneColumns.value);
  },
  { deep: true, immediate: true }
);
// 添加菜单
const handleCreate = () => {
  AddFormRef.value?.openDrawer({
    isUpdate: false,
    record: null
  });
};
// 编辑数据
const handleEdit = async (record: any) => {
  AddFormRef.value?.openDrawer({
    isUpdate: true,
    record
  });
};
// 更新数据
const handleData = async () => {
  fetchData();
};
// 排序拖拽
const handleChange = (_data: any) => {
  console.log(_data);
  renderData.value = _data;
};
// 更新状态
const handleStatus = async (record: any) => {
  try {
    const res = await upStatus({ id: record.id, status: record.status });
    if (res) {
      Message.success({ content: '更新状态成功', id: 'upStatus' });
    }
  } catch (error) {}
};
// 删除数据
const handleDel = async (record: any) => {
  try {
    const res = await del({ ids: [record.id] });
    if (res) {
      fetchData();
      Message.success({ content: '删除成功', id: 'upStatus' });
    }
  } catch (error) {}
};
// 状态
const statusOptions = computed<SelectOptionData[]>(() => [
  {
    label: '全部',
    value: ''
  },
  {
    label: '正常',
    value: 0
  },
  {
    label: '禁用',
    value: 1
  }
]);
</script>

<style scoped lang="less">
:deep(.arco-table-th) {
  &:last-child {
    .arco-table-th-item-title {
      margin-left: 16px;
    }
  }
}
.action-icon {
  margin-left: 12px;
  cursor: pointer;
}
.active {
  color: #0960bd;
  background-color: #e3f4fc;
}
.setting {
  display: flex;
  align-items: center;
  width: 200px;
  .title {
    margin-left: 12px;
    cursor: pointer;
  }
}
:deep(.general-card > .arco-card-header) {
  padding: 10px 16px;
}
</style>
