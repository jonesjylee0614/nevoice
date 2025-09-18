<template>
  <div class="container">
    <Breadcrumb :items="['语音能力', '语料管理']" />
    <a-card class="general-card" :bordered="false">
      <a-row :gutter="16">
        <a-col :span="16">
          <a-space>
            <a-input v-model="formModel.title" placeholder="请输入标题" allow-clear style="width: 200px" />
            <a-range-picker
              v-model="formModel.createdTime"
              style="width: 240px"
              :placeholder="['创建开始时间', '创建结束时间']"
            />
            <a-button type="primary" @click="search">
              <template #icon>
                <icon-search />
              </template>
              查询
            </a-button>
            <a-button @click="reset">重置</a-button>
          </a-space>
        </a-col>
        <a-col :span="8" style="text-align: right">
          <a-space>
            <a-button type="primary" @click="handleAdd">
              <template #icon>
                <icon-plus />
              </template>
              新建
            </a-button>
          </a-space>
        </a-col>
      </a-row>
      <a-divider style="margin-top: 16px" />
      <a-table
        row-key="id"
        :loading="loading"
        :pagination="pagination"
        :columns="columns"
        :data="renderData"
        :bordered="{ wrapper: true, cell: true }"
        :scroll="{ x: '100%', y: '100%' }"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
      >
        <template #status="{ record }">
          <a-tag v-if="record.status === 1" color="green">启用</a-tag>
          <a-tag v-else color="red">禁用</a-tag>
        </template>
        <template #operations="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="handleEdit(record)">编辑</a-button>
            <a-popconfirm content="确定要删除该记录吗?" @ok="handleDelete(record)">
              <a-button type="text" size="small" status="danger">删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </a-table>
    </a-card>
    
    <!-- 编辑/新增模态框 -->
    <a-modal
      v-model:visible="modalVisible"
      :title="isUpdate ? '编辑语料' : '新增语料'"
      @ok="handleSave"
      @cancel="handleCancel"
    >
      <a-form ref="formRef" :model="form" :rules="rules">
        <a-form-item label="标题" field="name">
          <a-input v-model="form.name" placeholder="请输入标题" />
        </a-form-item>
        <a-form-item label="内容" field="content">
          <a-textarea v-model="form.content" placeholder="请输入内容" :auto-size="{ minRows: 4 }" />
        </a-form-item>
        <a-form-item label="状态" field="status">
          <a-radio-group v-model="form.status">
            <a-radio :value="1">启用</a-radio>
            <a-radio :value="0">禁用</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { Message } from '@arco-design/web-vue';
import useLoading from '@/hooks/loading';
import { columns } from './data';
import { getList, save, deleteDoc } from './api';

defineOptions({
  name: 'VoiceDocument'
});

const { loading, setLoading } = useLoading(true);
const renderData = ref<any[]>([]);
const formRef = ref();
const modalVisible = ref(false);
const isUpdate = ref(false);

// 分页
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showTotal: true,
  showPageSize: true
});

// 查询条件
const formModel = reactive({
  title: '',
  createdTime: []
});

// 表单数据
const form = reactive({
  id: 0,
  name: '',
  content: '',
  status: 1
});

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入标题' }],
  content: [{ required: true, message: '请输入内容' }]
};

// 获取列表数据
const fetchData = async () => {
  setLoading(true);
  try {
    const params = {
      page: pagination.current,
      pageSize: pagination.pageSize,
      title: formModel.title,
      createdTime: formModel.createdTime.length > 0 ? formModel.createdTime.join(',') : ''
    };
    const data = await getList(params);
    renderData.value = data.items || [];
    pagination.current = data.page;
    pagination.total = data.total;
  } catch (err) {
    Message.error('获取数据失败');
  } finally {
    setLoading(false);
  }
};

// 查询
const search = () => {
  pagination.current = 1;
  fetchData();
};

// 重置
const reset = () => {
  formModel.title = '';
  formModel.createdTime = [];
  pagination.current = 1;
  fetchData();
};

// 分页
const handlePageChange = (page: number) => {
  pagination.current = page;
  fetchData();
};

const handlePageSizeChange = (pageSize: number) => {
  pagination.pageSize = pageSize;
  fetchData();
};

// 新增
const handleAdd = () => {
  isUpdate.value = false;
  modalVisible.value = true;
  // 重置表单
  Object.assign(form, {
    id: 0,
    name: '',
    content: '',
    status: 1
  });
};

// 编辑
const handleEdit = (record: any) => {
  isUpdate.value = true;
  modalVisible.value = true;
  Object.assign(form, record);
};

// 删除
const handleDelete = async (record: any) => {
  try {
    await deleteDoc({ ids: [record.id] });
    Message.success('删除成功');
    fetchData();
  } catch (err) {
    Message.error('删除失败');
  }
};

// 保存
const handleSave = async () => {
  const res = await formRef.value?.validate();
  if (!res) {
    try {
      await save(form);
      Message.success(isUpdate.value ? '更新成功' : '新增成功');
      modalVisible.value = false;
      fetchData();
    } catch (err) {
      Message.error(isUpdate.value ? '更新失败' : '新增失败');
    }
  }
};

// 取消
const handleCancel = () => {
  modalVisible.value = false;
};

fetchData();
</script>

<script lang="ts">
export default {
  name: 'VoiceDocument'
};
</script>

<style scoped lang="less">
.container {
  padding: 16px;
}

.general-card {
  margin-top: 16px;
}
</style>