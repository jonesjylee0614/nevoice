<template>
  <BasicModal
    v-bind="attrs"
    :is-padding="false"
    :loading="loading"
    width="calc(100% - 100px)"
    :min-height="modelHeight"
    title="会议详情"
    @register="registerModal"
    @ok="handleSubmit"
    @cancel="closeModal"
  >
    <div class="container">
      <ACard class="general-card oneLineCard" style="height: calc(100% - 50px)">
        <ARow style="margin-bottom: 10px">
          <ACol :span="16">
            <ASpace>
              <AInput v-model="formModel.spkName" :style="{ width: '160px' }" placeholder="说话人" allow-clear />
              <AInput v-model="formModel.text" :style="{ width: '160px' }" placeholder="说话内容" allow-clear />
              <ARangePicker v-model="formModel.createdTime" :style="{ width: '230px' }" />
              <AButton type="primary" @click="search">
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
              <ATooltip content="刷新">
                <div class="action-icon" @click="search"><icon-refresh size="18" /></div>
              </ATooltip>
            </ASpace>
          </ACol>
        </ARow>
        <ATable
          row-key="id"
          :loading="loading"
          :pagination="false"
          :columns="detailColumns"
          :data="renderData"
          :scroll="{ x: '100%', y: '620px' }"
        >
          <template #spkUserName="{ record }">
            <ATag v-if="!record.spkUserName" color="gray">未确认</ATag>
            <ATag v-else>{{ record.spkUserName }}</ATag>
          </template>
          <template #trainStatus="{ record }">
            <ATag v-if="record.trainStatus === 0" color="gray">未加入</ATag>
            <ATag v-else-if="record.trainStatus === 55" color="blue">待训练</ATag>
            <ATag v-else-if="record.trainStatus === 66" color="green">已完成</ATag>
          </template>
          <template #operations="{ record }">
            <ASpace class="option">
              <audio :ref="(el: any) => setAudioRef(el, record)">
                <source
                  :ref="(el: any) => setAudioSourceRef(el, record)"
                  :data-src="`${apiHost}/meeting_voice/detail/${record.meetingId}/${record.wavPath}`"
                  type="audio/ogg"
                />
              </audio>
              <Icon
                icon="icon-sound"
                :size="18"
                :color="playingId === record.id ? 'rgb(var(--success-6))' : 'rgb(var(--primary-6))'"
                @click="playAudio(record.id)"
              />

              <ATooltip v-if="record.trainStatus === 0" content="加入训练">
                <Icon
                  icon="icon-robot-add"
                  :size="18"
                  color="rgb(var(--primary-6))"
                  @click="handleAddTrain(record, true)"
                />
              </ATooltip>
              <ATooltip v-if="record.trainStatus === 55" content="移除训练">
                <APopconfirm
                  v-perm="[perms.detail_edit_train]"
                  content="您确定移除训练吗?"
                  @ok="handleAddTrain(record, false)"
                >
                  <Icon icon="icon-robot-add" :size="18" color="#ed6f6f" />
                </APopconfirm>
              </ATooltip>
              <Icon
                v-perm="[perms.detail_edit]"
                icon="icon-edit"
                color="rgb(var(--primary-6))"
                @click="handleEdit(record)"
              />
            </ASpace>
          </template>
        </ATable>
      </ACard>
      <!--表单-->
      <DetailForm @register="registerEditModal" @success="handleData" />
    </div>
  </BasicModal>
</template>

<script lang="ts" setup>
import { cloneDeep } from 'lodash-es';
import { Message } from '@arco-design/web-vue';
import useLoading from '@/hooks/loading';
import { useAttrs } from '@/hooks/core/useAttrs';
import { BasicModal, useModal, useModalInner } from '@/components/Modal';
import { Icon } from '@/components/Icon';
import { detailColumns } from './data';
import { getDetail, trainDetail } from './api/index';
import DetailForm from './DetailForm.vue';

const attrs = useAttrs();
const [registerEditModal, { openModal: openEditModal }] = useModal();

// 按钮权限写到一起
const perms = {
  detail_export: 'meeting:offline:detail:export',
  detail_edit: 'meeting:offline:detail:edit',
  detail_edit_train: 'meeting:offline:detail:edit_train'
};

const { loading, setLoading } = useLoading(true);
const renderData = ref([]);
const modelHeight = ref(720);
// 查询字段
const generateFormModel = (meetingId: any) => {
  return {
    meetingId,
    spkName: '',
    createdTime: [],
    text: ''
  };
};

const formModel = ref(generateFormModel(0));
const detailRecord = ref();

const apiHost = import.meta.env.VITE_API_HOST;

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

const [registerModal, { closeModal }] = useModalInner(async data => {
  detailRecord.value = cloneDeep(data.record);
  formModel.value = generateFormModel(detailRecord.value.id);
  await fetchData();
});

const fetchData = async () => {
  setLoading(true);
  try {
    renderData.value = await getDetail(formModel.value);
  } finally {
    setLoading(false);
  }
};
// 查找
const search = () => {
  fetchData();
};
const reset = () => {
  formModel.value = generateFormModel(detailRecord.value.id);
  fetchData();
};

// 编辑数据
const handleEdit = async (record: any) => {
  openEditModal(true, {
    isUpdate: true,
    record
  });
};

// 更新数据
const handleData = async () => {
  await fetchData();
};
const handleSubmit = () => {
  console.log('submit');
};
const handleAddTrain = async (record: any, add: boolean) => {
  await trainDetail({ id: record.id, add });
  await fetchData();
};
</script>

<style lang="less" scoped>
@import '@/assets/style/formlayer.less';
</style>
