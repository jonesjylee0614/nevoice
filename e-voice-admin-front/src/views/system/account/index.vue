<template>
  <div class="container">
    <Breadcrumb :items="['menu.system', 'menu.system.account']" />
    <ACard class="general-card oneLineCard" style="height: calc(100% - 50px)">
      <ARow style="margin-bottom: 10px">
        <ACol :span="16">
          <ASpace>
            <AInput v-model="formModel.name" placeholder="姓名/账号/昵称" allow-clear @keyup.enter="search" />
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
            <AButton v-perm="[perms.add]" type="primary" @click="handleCreate">
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
        :pagination="pagination"
        :columns="cloneColumns as TableColumnData[]"
        :data="renderData"
        :bordered="{ wrapper: true, cell: true }"
        :size="size"
        :default-expand-all-rows="true"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
      >
        <template #name="{ record }">
          {{ record.name }}
          <span v-if="record.nickname" style="padding-left: 5px; color: var(--color-neutral-4)">
            {{ record.nickname }}
          </span>
        </template>
        <template #avatar="{ record }">
          <AImage alt="" :src="record.avatar" width="30px" style="cursor: pointer" />
        </template>
        <template #createTime="{ record }">
          {{ dayjs(record.createTime).format('YYYY-MM-DD') }}
        </template>
        <template #status="{ record }">
          <ASwitch
            v-model="record.status"
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
            <APopconfirm content="您确定要删除吗?" @ok="handleDel(record)">
              <Icon v-perm="[perms.del]" icon="icon-delete" :size="18" color="#ed6f6f" />
            </APopconfirm>
          </ASpace>
        </template>
      </ATable>
    </ACard>
    <!--表单-->
    <AddForm @register="registerModal" @success="handleData" />
  </div>
</template>

<script lang="ts" setup>
import dayjs from 'dayjs';
import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';
import type { SelectOptionData } from '@arco-design/web-vue/es/select/interface';
import cloneDeep from 'lodash/cloneDeep';
import { Message } from '@arco-design/web-vue';
import { del, getList, upStatus } from '@/api/system/account';
import useLoading from '@/hooks/loading';
import { Icon } from '@/components/Icon';
import { useModal } from '@/components/Modal';
import type { Pagination } from '@/types/global';
import { hasPerm } from '@/directive/permission/check';
import AddForm from './AddForm.vue';
import { columns } from './data';
defineOptions({
  name: 'Rule'
});

// 按钮权限写到一起
const perms = {
  add: 'account:add',
  del: 'account:del',
  edit: 'account:edit',
  upStatus: 'account:upStatus'
};

const [registerModal, { openModal }] = useModal();
// 分页
const basePagination: Pagination = {
  current: 1,
  pageSize: 10
};
const pagination = reactive({
  ...basePagination,
  showTotal: true,
  showPageSize: true
});
type SizeProps = 'mini' | 'small' | 'medium' | 'large';
type Column = TableColumnData & { checked?: true };
const { loading, setLoading } = useLoading(true);
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
const fetchData = async () => {
  setLoading(true);
  try {
    const data = await getList({
      page: pagination.current,
      pageSize: pagination.pageSize,
      ...formModel.value
    });
    renderData.value = data.items;
    pagination.current = data.page;
    pagination.total = data.total;
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
    if (!hasPerm(perms.upStatus)) {
      // 过滤掉status列
      cloneColumns.value = cloneColumns.value.filter(item => item.dataIndex !== 'status');
    }
    showColumns.value = cloneDeep(cloneColumns.value);
  },
  { deep: true, immediate: true }
);
// 添加菜单
const handleCreate = () => {
  openModal(true, {
    isUpdate: false,
    record: null
  });
};
// 编辑数据
const handleEdit = async (record: any) => {
  openModal(true, {
    isUpdate: true,
    record
  });
};
// 更新数据
const handleData = async () => {
  fetchData();
};
// 分页
const handlePageChange = (page: any) => {
  pagination.current = page;
  fetchData();
};
// 分页总数
const handlePageSizeChange = (pageSize: any) => {
  pagination.pageSize = pageSize;
  fetchData();
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
