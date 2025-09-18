<template>
  <BasicModal
    v-bind="attrs"
    :is-padding="false"
    :loading="loading"
    width="1000px"
    :min-height="modelHeight"
    :title="getTitle"
    @register="registerModal"
    @height-change="onHeightChange"
    @ok="handleSubmit"
  >
    <div class="addFormbox" :style="{ 'min-height': `${windHeight}px` }">
      <div v-if="isEditor" class="tabs-header">
        <div class="tabs-nav-wrap">
          <div
            v-for="iten in tapList"
            :key="iten.id"
            class="tap_item"
            :class="{ item_active: activeKey == iten.id }"
            @click="
              () => {
                activeKey = iten.id;
              }
            "
          >
            <div class="label">{{ iten.name }}</div>
          </div>
        </div>
        <div class="tabs-bar" :style="{ top: `${(activeKey - 1) * 64}px`, height: `64px` }"></div>
      </div>
      <div class="tabs-content" :class="{ addpadding: !isEditor }">
        <AForm ref="formRef" :model="formData" auto-label-width>
          <div class="content_box">
            <!--基础信息-->
            <AScrollbar v-show="activeKey == 1" style="overflow: auto" :style="{ height: `${windHeight}px` }">
              <div class="besecontent">
                <ARow :gutter="16">
                  <ACol :span="12">
                    <AFormItem field="cid" label="选择分类" validate-trigger="input">
                      <ASelect v-model="formData.cid" :options="cateList" placeholder="请选择分类" />
                    </AFormItem>
                  </ACol>
<!--replaceTpl-->
                </ARow>
              </div>
            </AScrollbar>
            <!--高级信息-->
            <div v-show="activeKey == 2" class="hcontent" :style="{ height: `${windHeight}px` }">
              <Editor ref="editorRef" :min-height="windHeight" @updata="handleEditUpdta" />
            </div>
          </div>
        </AForm>
      </div>
    </div>
  </BasicModal>
</template>

<script lang="ts" setup>
import { cloneDeep } from 'lodash-es';
import type { FormInstance } from '@arco-design/web-vue';
// api
import type { TreeNodeData } from '@arco-design/web-vue';
import { Message } from '@arco-design/web-vue';
import useLoading from '@/hooks/loading';
import { BasicModal, useModalInner } from '@/components/Modal';
import Editor from '@/components/Editor/Main.vue';
import { getCate } from './cate/api';
import FileUpload from '@/components/upload/FileUpload.vue';
import ImgUpload from '@/components/upload/ImgUpload.vue';
import { getContent, save } from './api/index';

const attrs = useAttrs();

const emit = defineEmits(['success']);
// 判断是否存在编辑器
const isEditor = ref(true);
const isUpdate = ref(false);
const cateList = ref<TreeNodeData[]>([]);
const activeKey = ref(1);
const modelHeight = ref(620);
const windHeight = ref(620);
// 表单
const formRef = ref<FormInstance>();
// 表单字段
const basedata = {
  id: 0,
  replaceField: null
};
const formData = ref<any>(basedata);
// 编辑器
const editorRef = ref();
const [registerModal, { setModalProps, closeModal }] = useModalInner(async data => {
  formRef.value?.resetFields();
  activeKey.value = 1;
  setModalProps({ confirmLoading: false });
  const mdata = await getCate({});
  const parntList_df: any = [{ value: 0, label: '未选分类' }];
  if (mdata) {
    cateList.value = parntList_df.concat(mdata);
  } else {
    cateList.value = parntList_df;
  }
  isUpdate.value = Boolean(data?.isUpdate);
  if (unref(isUpdate)) {
    formData.value = cloneDeep(data.record);
    const mewdata = await getContent({ id: data.record.id });
    formData.value = { ...formData.value, ...mewdata };
    if (editorRef.value) editorRef.value.setVal(mewdata.content);
  } else {
    formData.value = cloneDeep(basedata);
  }
});
const getTitle = computed(() => (!unref(isUpdate) ? '新增数据' : '编辑数据'));
// 点击确认
const { loading, setLoading } = useLoading();
const handleSubmit = async () => {
  try {
    const res = await formRef.value?.validate();
    if (!res) {
      setLoading(true);
      Message.loading({ content: '提交中', id: 'upStatus', duration: 2000 });
      const savedata = cloneDeep(unref(formData));
      await save(savedata);
      Message.success({ content: '提交成功', id: 'upStatus', duration: 2000 });
      closeModal();
      emit('success');
      setLoading(false);
    }
  } catch (error) {
    setLoading(false);
    Message.clear('top');
  }
};
// 编辑器返回数据
const handleEditUpdta = (val: string) => {
  formData.value.content = val;
};
// 监听高度
const onHeightChange = (val: any) => {
  windHeight.value = val;
};

const OYoptions = [
  { label: '否', value: 0 },
  { label: '是', value: 1 }
];
const tapList = [
  { id: 1, name: '基础内容' },
  { id: 2, name: '详细内容' }
];
</script>

<style lang="less" scoped>
@import '@/assets/style/formlayer.less';
</style>
