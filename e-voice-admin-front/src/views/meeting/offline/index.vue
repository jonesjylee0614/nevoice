<template>
  <div class="container">
    <Breadcrumb :items="[route.matched[0].meta.locale, route.meta.locale]" />
    <ACard class="general-card oneLineCard" style="height: calc(100% - 50px)">
      <ARow style="margin-bottom: 10px">
        <ACol :span="16">
          <ASpace>
            <AInput v-model="formModel.title" :style="{ width: '160px' }" placeholder="会议名称" allow-clear />
            <ARangePicker v-model="formModel.createdTime" :style="{ width: '230px' }" />
            <AButton type="primary" :loading="btnLoading" @click="search">
              <template #icon>
                <icon-search />
              </template>
              查询
            </AButton>
            <AButton @click="reset">重置</AButton>
          </ASpace>
        </ACol>
        <ACol :span="8" style="text-align: right">
          <ASpace>
            <AButton v-perm="[perms.edit]" type="primary" @click="handleCreate">
              <template #icon>
                <icon-plus />
              </template>
              新建
            </AButton>
          </ASpace>
        </ACol>
      </ARow>
      <ATable
        row-key="id"
        :loading="loading"
        :pagination="pagination"
        :columns="columns"
        :data="renderData"
        :bordered="{ wrapper: true, cell: true }"
        :size="size"
        :default-expand-all-rows="true"
        @page-change="handlePaageChange"
        @page-size-change="handlePageSizeChange"
      >
        <template #operations="{ record }">
          <ASpace class="option">
            <ATooltip v-perm="[perms.detail]" content="详情">
              <Icon icon="icon-list" color="rgb(var(--primary-6))" @click="handleDetail(record)" />
            </ATooltip>
            <Icon v-perm="[perms.edit]" icon="icon-edit" color="rgb(var(--primary-6))" @click="handleEdit(record)" />
            <APopconfirm v-perm="[perms.del]" content="您确定要删除吗?" @ok="handleDel(record)">
              <Icon icon="icon-delete" :size="18" color="#ed6f6f" />
            </APopconfirm>
          </ASpace>
        </template>
      </ATable>
    </ACard>
    <!--表单-->
    <AddForm @register="registerModal" @success="handleData" />
    <Detail @register="registerDetailModal" />
  </div>
</template>

<script lang="ts" setup>
import { useRoute } from 'vue-router';
import { Message } from '@arco-design/web-vue';
import useLoading from '@/hooks/loading';
import { Icon } from '@/components/Icon';
import type { Pagination } from '@/types/global';
import { useModal } from '@/components/Modal';
import { columns } from '@/views/meeting/offline/data';
import AddForm from './AddForm.vue';
import { del, getList } from './api';
import Detail from './Detail.vue';

const route = useRoute();
const [registerModal, { openModal }] = useModal();
const [registerDetailModal, { openModal: openDetailModal }] = useModal();

// 按钮权限写到一起
const perms = {
  del: 'meeting:offline:del',
  edit: 'meeting:offline:edit',
  detail: 'meeting:offline:detail'
};

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
const { loading, setLoading } = useLoading(true);
const { loading: btnLoading, setLoading: setBtnLoading } = useLoading(false);
const renderData = ref([]);
const size = ref<SizeProps>('large');
// 查询字段
const generateFormModel = () => {
  return {
    trade_no: '',
    title: '',
    name: '',
    createdTime: [],
    status: ''
  };
};
const formModel = ref(generateFormModel());
const fetchData = async () => {
  setLoading(true);
  try {
    const data = await getList({ page: pagination.current, pageSize: pagination.pageSize, ...formModel.value });
    renderData.value = data.items;
    pagination.current = data.page;
    pagination.total = data.total;
  } catch (err) {
    // you can report use errorHandler or other
  } finally {
    setLoading(false);
  }
};
// 查找
const search = () => {
  setBtnLoading(true);
  fetchData();
  setTimeout(() => {
    setBtnLoading(false);
  }, 1000);
};
const reset = () => {
  formModel.value = generateFormModel();
  fetchData();
};

fetchData();

// 添加
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

const handleDetail = async (record: any) => {
  openDetailModal(true, {
    record
  });
};
// 更新数据
const handleData = async () => {
  setTimeout(fetchData, 1000);
};
// 分页
const handlePaageChange = (page: any) => {
  pagination.current = page;
  fetchData();
};
// 分页总数
const handlePageSizeChange = (pageSize: any) => {
  pagination.pageSize = pageSize;
  fetchData();
};
// 删除数据
const handleDel = async (record: any) => {
  try {
    Message.loading({ content: '删除中', id: 'upStatus' });
    const res = await del({ ids: [record.id] });
    if (res) {
      fetchData();
      Message.success({ content: '删除成功', id: 'upStatus' });
    }
  } catch (error) {
    Message.clear('top');
  }
};
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
.option .arco-icon {
  user-select: none;
  cursor: pointer;
  opacity: 0.8;
  &:hover {
    opacity: 1;
  }
}
</style>
