<template>
  <div class="container">
    <Breadcrumb :items="['语音能力', '热词管理']" />
    <ACard class="general-card" :bordered="false">
      <!-- 统计卡片 -->
      <ARow :gutter="16" class="stats-row">
        <ACol :span="8">
          <AStatistic title="热词总数" :value="stats.total">
            <template #prefix>
              <icon-file />
            </template>
          </AStatistic>
        </ACol>
        <ACol :span="8">
          <AStatistic title="已启用" :value="stats.enabled" value-style="color: #00b42a">
            <template #prefix>
              <icon-check-circle />
            </template>
          </AStatistic>
        </ACol>
        <ACol :span="8">
          <AStatistic title="已禁用" :value="stats.disabled" value-style="color: #f53f3f">
            <template #prefix>
              <icon-close-circle />
            </template>
          </AStatistic>
        </ACol>
      </ARow>
      <ADivider />
      <!-- 搜索与操作 -->
      <ARow :gutter="16">
        <ACol :span="14">
          <ASpace>
            <AInput
              v-model="formModel.word"
              placeholder="请输入热词关键字"
              allow-clear
              style="width: 200px"
              @press-enter="search"
            />
            <ARangePicker
              v-model="formModel.createdTime"
              style="width: 240px"
              :placeholder="['创建开始时间', '创建结束时间']"
            />
            <AButton type="primary" @click="search">
              <template #icon>
                <icon-search />
              </template>
              查询
            </AButton>
            <AButton @click="reset">重置</AButton>
          </ASpace>
        </ACol>
        <ACol :span="10" style="text-align: right">
          <ASpace>
            <AButton type="primary" @click="handleAdd">
              <template #icon>
                <icon-plus />
              </template>
              新增
            </AButton>
            <AButton type="outline" @click="showImportModal = true">
              <template #icon>
                <icon-upload />
              </template>
              批量导入
            </AButton>
            <AButton type="outline" @click="handleExport">
              <template #icon>
                <icon-download />
              </template>
              导出
            </AButton>
            <AButton type="outline" status="success" @click="handleSync">
              <template #icon>
                <icon-sync />
              </template>
              同步文件
            </AButton>
          </ASpace>
        </ACol>
      </ARow>
      <ADivider style="margin-top: 16px" />
      <!-- 表格 -->
      <ATable
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
          <ASwitch :model-value="record.status === 1" @change="val => handleStatusChange(record, val as boolean)">
            <template #checked>启用</template>
            <template #unchecked>禁用</template>
          </ASwitch>
        </template>
        <template #operations="{ record }">
          <ASpace>
            <AButton type="text" size="small" @click="handleEdit(record)">编辑</AButton>
            <APopconfirm content="确定要删除该热词吗?" @ok="handleDelete(record)">
              <AButton type="text" size="small" status="danger">删除</AButton>
            </APopconfirm>
          </ASpace>
        </template>
      </ATable>
    </ACard>

    <!-- 编辑/新增模态框 -->
    <AModal
      v-model:visible="modalVisible"
      :title="isUpdate ? '编辑热词' : '新增热词'"
      @ok="handleSave"
      @cancel="handleCancel"
    >
      <AForm ref="formRef" :model="form" :rules="rules" layout="vertical">
        <AFormItem label="热词" field="word">
          <AInput v-model="form.word" placeholder="请输入热词" :max-length="200" show-word-limit />
        </AFormItem>
        <AFormItem label="状态" field="status">
          <ARadioGroup v-model="form.status">
            <ARadio :value="1">启用</ARadio>
            <ARadio :value="0">禁用</ARadio>
          </ARadioGroup>
        </AFormItem>
      </AForm>
    </AModal>

    <!-- 导入模态框 -->
    <AModal
      v-model:visible="showImportModal"
      title="批量导入热词"
      :ok-loading="importLoading"
      @ok="handleImport"
      @cancel="showImportModal = false"
    >
      <AAlert type="info" style="margin-bottom: 16px">
        <template #content>
          <div>请上传 .txt 文件，每行一个热词</div>
          <div style="color: #86909c; font-size: 12px; margin-top: 4px">已存在的热词会自动跳过</div>
        </template>
      </AAlert>
      <AUpload :auto-upload="false" :limit="1" accept=".txt" :file-list="fileList" @change="handleFileChange">
        <template #upload-button>
          <AButton type="primary">
            <template #icon>
              <icon-upload />
            </template>
            选择文件
          </AButton>
        </template>
      </AUpload>
      <div v-if="importResult" style="margin-top: 16px">
        <AAlert :type="importResult.success ? 'success' : 'error'">
          <template #content>
            {{ importResult.message }}
          </template>
        </AAlert>
      </div>
    </AModal>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, reactive, ref } from 'vue';
import { Message } from '@arco-design/web-vue';
import type { FileItem } from '@arco-design/web-vue/es/upload/interfaces';
import useLoading from '@/hooks/loading';
import { defHttp } from '@/utils/http';
import { columns } from './data';
import { Api, deleteHotword, getList, getStats, save, syncToFile, updateStatus } from './api';

defineOptions({
  name: 'VoiceHotword'
});

const { loading, setLoading } = useLoading(true);
const renderData = ref<any[]>([]);
const formRef = ref();
const modalVisible = ref(false);
const isUpdate = ref(false);
const showImportModal = ref(false);
const importLoading = ref(false);
const fileList = ref<FileItem[]>([]);
const importResult = ref<{ success: boolean; message: string } | null>(null);

// 统计数据
const stats = reactive({
  total: 0,
  enabled: 0,
  disabled: 0
});

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
  word: '',
  createdTime: [] as string[]
});

// 表单数据
const form = reactive({
  id: 0,
  word: '',
  status: 1
});

// 表单验证规则
const rules = {
  word: [{ required: true, message: '请输入热词' }]
};

// 获取统计信息
const fetchStats = async () => {
  try {
    const data = await getStats();
    stats.total = data.total || 0;
    stats.enabled = data.enabled || 0;
    stats.disabled = data.disabled || 0;
  } catch (err) {
    console.error('获取统计信息失败', err);
  }
};

// 获取列表数据
const fetchData = async () => {
  setLoading(true);
  try {
    const params = {
      page: pagination.current,
      pageSize: pagination.pageSize,
      word: formModel.word,
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
  formModel.word = '';
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
  Object.assign(form, {
    id: 0,
    word: '',
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
    await deleteHotword({ ids: [record.id] });
    Message.success('删除成功');
    fetchData();
    fetchStats();
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
      fetchStats();
    } catch (err) {
      // Message.error(isUpdate.value ? '更新失败' : '新增失败');
    }
  }
};

// 取消
const handleCancel = () => {
  modalVisible.value = false;
};

// 状态切换
const handleStatusChange = async (record: any, status: boolean) => {
  try {
    await updateStatus({ id: record.id, status: status ? 1 : 0 });
    Message.success('状态更新成功');
    fetchData();
    fetchStats();
  } catch (err) {
    Message.error('状态更新失败');
  }
};

// 文件选择
const handleFileChange = (list: FileItem[]) => {
  fileList.value = list;
  importResult.value = null;
};

// 导入
const handleImport = async () => {
  if (fileList.value.length === 0) {
    Message.warning('请选择文件');
    return;
  }

  const file = fileList.value[0].file;
  if (!file) {
    Message.warning('文件无效');
    return;
  }

  importLoading.value = true;
  try {
    const formData = new FormData();
    formData.append('file', file);

    const res = await defHttp.post({
      url: Api.import,
      params: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    importResult.value = {
      success: true,
      message: `导入完成！总计 ${res.total} 条，成功 ${res.success} 条，跳过 ${res.skip} 条`
    };

    fetchData();
    fetchStats();
    fileList.value = [];
  } catch (err: any) {
    importResult.value = {
      success: false,
      message: err.message || '导入失败'
    };
  } finally {
    importLoading.value = false;
  }
};

// 导出
const handleExport = () => {
  window.open(`/api${Api.export}`, '_blank');
};

// 同步到文件
const handleSync = async () => {
  try {
    await syncToFile();
    Message.success('同步成功');
  } catch (err) {
    Message.error('同步失败');
  }
};

onMounted(() => {
  fetchData();
  fetchStats();
});
</script>

<style scoped lang="less">
.container {
  padding: 16px;
}

.general-card {
  margin-top: 16px;
}

.stats-row {
  margin-bottom: 8px;
}
</style>
