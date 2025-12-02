<template>
  <BasicModal
    v-bind="attrs"
    :loading="loading"
    width="1000px"
    :min-height="620"
    :title="getTitle"
    @register="registerModal"
    @ok="handleSubmit"
  >
    <AForm ref="formRef" :model="formData" auto-label-width>
      <ARow style="margin-bottom: 10px">
        <ACol :span="24" style="text-align: right">
          <ASpace>
            <ALink style="width: 100px" @click="copyH5Url">复制H5链接</ALink>
            <AButton type="primary" @click="fetchData">
              <template #icon>
                <icon-search />
              </template>
              查询
            </AButton>

            <AButton v-perm="[perms.add]" type="primary" @click="addPrint">
              <template #icon>
                <icon-plus />
              </template>
              添加
            </AButton>
            <AButton v-perm="[perms.add]" type="primary" disabled @click="importPrint">
              <template #icon>
                <icon-import />
              </template>
              导入
            </AButton>
          </ASpace>
        </ACol>
      </ARow>
      <ATable
        ref="artable"
        row-key="id"
        :loading="loading"
        :pagination="pagination"
        :columns="printsColumns"
        :data="printsData"
        :bordered="{ wrapper: true, cell: true }"
        :default-expand-all-rows="true"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
      >
        <template #create_time="{ record }">
          {{ dayjs(record.create_time).format('YYYY-MM-DD HH:mm:ss') }}
        </template>
        <template #name="{ record }">
          {{ record.name }}
          <span v-if="record.nickname" style="padding-left: 5px; color: var(--color-neutral-4)">
            {{ record.nickname }}
          </span>
        </template>
        <template #options="{ record }">
          <ASpace class="option">
            <audio :ref="(el: any) => setAudioRef(el, record)">
              <source
                :ref="(el: any) => setAudioSourceRef(el, record)"
                :data-src="`${apiHost}/print_voice/${record.userid}/${record.wav_path}`"
                type="audio/ogg"
              />
            </audio>
            <Icon
              icon="icon-sound"
              :size="18"
              :color="playingId === record.id ? 'rgb(var(--success-6))' : 'rgb(var(--primary-6))'"
              @click="playAudio(record.id)"
            />
            <APopconfirm v-perm="[perms.del]" content="您确定要删除吗?" @ok="handleDel(record)">
              <Icon icon="icon-delete" :size="18" color="#ed6f6f" />
            </APopconfirm>
          </ASpace>
        </template>
      </ATable>
    </AForm>
    <AddForm @register="registerAddModal" @success="handleAddSuccess" />
  </BasicModal>
</template>

<script lang="ts" setup>
import dayjs from 'dayjs';
import { cloneDeep } from 'lodash-es';
import type { FormInstance } from '@arco-design/web-vue';
import { Message } from '@arco-design/web-vue';
import useLoading from '@/hooks/loading';
import { Icon } from '@/components/Icon';
import { BasicModal, useModal, useModalInner } from '@/components/Modal';
import { printsColumns } from '@/views/voice/print/data';
import AddForm from './AddForm.vue';
import { delUserPrint, fetchUserH5Url, getUserPrints } from './api';
import type { Pagination } from '/#/global';
// 按钮权限写到一起
const perms = {
  add: 'print:add',
  del: 'print:del'
};
const apiHost = import.meta.env.VITE_API_HOST;
const attrs = useAttrs();
const printsData = ref([]);
const audioRefs = {} as any;
const audioSourceRefs = {} as any;
const playingId = ref(0);

const setAudioRef = (el: any, record: any) => {
  audioRefs[record.id] = el;
};

const setAudioSourceRef = (el: any, record: any) => {
  audioSourceRefs[record.id] = el;
};

const playAudio = (id: any) => {
  if (playingId.value == id) {
    playingId.value = 0;
    audioRefs[id].pause();
    audioRefs[id].currentTime = 0;
    return;
  }
  // 停止其他播放
  for (const id in audioRefs) {
    if (audioRefs[id]) {
      audioRefs[id].pause();
      audioRefs[id].currentTime = 0;
    }
  }

  playingId.value = id;
  if (audioRefs[id]) {
    audioSourceRefs[id].setAttribute('src', audioSourceRefs[id].getAttribute('data-src'));
    audioRefs[id].load();
    audioRefs[id]
      .play() // 播放
      .catch(() => {
        Message.error('播放失败，请检查音频文件');
      });
  }
};

const [registerAddModal, { openModal: openAddModal }] = useModal();

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

// 表单
const formRef = ref<FormInstance>();
// 表单字段
const formData = ref<any>({ userId: '', userName: '' });
// 编辑器
const [registerModal, { setModalProps, closeModal }] = useModalInner(async data => {
  formRef.value?.resetFields();
  setModalProps({ confirmLoading: false });
  formData.value.userId = data.record.id;
  formData.value.userName = data.record.name;
  await fetchData();
});

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

const fetchData = async () => {
  setLoading(true);
  try {
    const data = await getUserPrints({
      page: pagination.current,
      pageSize: pagination.pageSize,
      userId: formData.value.userId
    });
    printsData.value = data.items;
    pagination.current = data.page;
    pagination.total = data.total;
  } catch (err) {
    // you can report use errorHandler or other
  } finally {
    setLoading(false);
  }
};

const copyH5Url = async () => {
  // navigator.clipboard.writeText(url);
  // 调用后端接口生成H5链接并复制到剪贴板
  const params = formData.value;
  const data = await fetchUserH5Url(params);
  try {
    await navigator.clipboard.writeText(data);
  } catch (e) {
    Message.success('复制成功');
    return;
  }
  Message.success('复制成功');
};

const addPrint = () => {
  openAddModal(true, {
    record: cloneDeep(formData.value)
  });
};

const handleAddSuccess = async () => {
  setTimeout(fetchData, 1000);
};

const importPrint = () => {};

const getTitle = computed(() => '声纹管理');
// 点击确认
const { loading, setLoading } = useLoading();
const handleSubmit = async () => {
  closeModal();
};

const handleDel = async (record: any) => {
  await delUserPrint({ docId: record.id, userId: formData.value.userId });
  setTimeout(fetchData, 1000);
};
</script>

<style lang="less" scoped></style>
