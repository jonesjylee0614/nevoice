<template>
  <BasicModal
    v-bind="$attrs"
    :is-padding="false"
    :footer="false"
    :loading="loading"
    width="1000px"
    :min-height="modelHeight"
    :title="getTitle"
    @register="registerModal"
    @height-change="onHeightChange"
  >
    <div class="modalbox" :style="{ 'min-height': `${windHeight}px` }">
      <div class="table-content">
        <ARow style="margin-bottom: 10px">
          <ACol :span="16">
            <ASpace>
              <AInput v-model="formModel.name" :style="{ width: '160px' }" placeholder="名称" allow-clear />
              <ARangePicker v-model="formModel.createdTime" :style="{ width: '200px' }" />
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
              <AButton type="primary" @click="createData">
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
          size="medium"
          :default-expand-all-rows="true"
          @page-change="handlePaageChange"
          @page-size-change="handlePageSizeChange"
        >
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
            <Icon icon="icon-edit" color="rgb(var(--primary-6))" @click="handleEdit(record)"/>
            <ADivider direction="vertical" />
            <APopconfirm content="您确定要删除吗?" @ok="handleDel(record)">
              <Icon icon="icon-delete" :size="18" color="#ed6f6f"/>
            </APopconfirm>
          </template>
        </ATable>
      </div>
    </div>
    <!--表单-->
    <AddForm ref="addFormRef" @success="search" />
  </BasicModal>
</template>

<script lang="ts" setup>
import dayjs from 'dayjs';
import { Message } from '@arco-design/web-vue';
import { BasicModal, useModalInner } from '@/components/Modal';
import useLoading from '@/hooks/loading';
import type { Pagination } from '@/types/global';
import { Icon } from '@/components/Icon';
import { columns } from './data';
import { del, getList, upStatus } from './api';
import AddForm from './AddForm.vue';

const isUpdate = ref(false);
const modelHeight = ref(620);
const windHeight = ref(620);
const renderData = ref([]);
const { loading, setLoading } = useLoading(true);
const { loading: btnLoading, setLoading: setBtnLoading } = useLoading(false);
const [registerModal, { setModalProps }] = useModalInner(async data => {
  setModalProps({ confirmLoading: false });
  isUpdate.value = Boolean(data?.isUpdate);
  await fetchData();
});
// 查询字段
const generateFormModel = () => {
  return {
    title: '',
    name: '',
    createdTime: [],
    status: ''
  };
};
const formModel = ref(generateFormModel());
// 加载数据
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
const getTitle = computed(() => (!unref(isUpdate) ? '分类管理' : '编辑数据'));
// 点击确认
// 监听高度
const onHeightChange = (val: any) => {
  windHeight.value = val;
};
// 表格
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
// 更新状态
const handleStatus = async (record: any) => {
  try {
    Message.loading({ content: '更新状态中', id: 'upStatus' });
    const res = await upStatus({ id: record.id, status: record.status });
    if (res) {
      Message.success({ content: '更新状态成功', id: 'upStatus' });
    }
  } catch (error) {
    Message.clear('top');
  }
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
// 新增数据
const addFormRef = ref();
const createData = async () => {
  addFormRef.value.ShowModal({
    isUpdate: false,
    record: null
  });
};
// 编辑数据
const handleEdit = async (record: any) => {
  addFormRef.value.ShowModal({
    isUpdate: true,
    record
  });
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
</script>

<style lang="less" scoped>
.modalbox {
  padding: 10px;
  .table-content {
  }
}
</style>
