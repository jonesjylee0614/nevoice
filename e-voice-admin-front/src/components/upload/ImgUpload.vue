<template>
  <div class="upimagebox">
    <div class="imagebtn">
      <div v-if="modelValue" class="upload-show-picture">
        <AImage
          :src="modelValue"
          height="90"
          :preview-visible="visibleimage"
          @preview-visible-change="
            () => {
              visibleimage = false;
            }
          "
        />
        <div class="upload-show-picture-mask">
          <ASpace>
            <icon-eye class="opbtn" @click="() => (visibleimage = true)" />
            <IconEdit class="opbtn" @click="UpImage" />
          </ASpace>
        </div>
      </div>
      <div v-else class="upload-picture-card" @click="UpImage">
        <div class="upload-picture-card-text">
          <IconPlus />
          <div style="margin-top: 10px; font-weight: 600">上传图片</div>
        </div>
      </div>
    </div>
  </div>
  <FileManage @register="registerFileModal" @success="selectImg" />
</template>

<script lang="ts" setup>
import { useModal } from '@/components/Modal';
import FileManage from '@/views/datacenter/attachment/components/FileManage.vue';

const [registerFileModal, { openModal: openFileModal }] = useModal();

const visibleimage = ref(false);
const emit = defineEmits(['update:modelValue']);

interface Props {
  multi?: boolean;
  modelValue: string;
}
const props = defineProps<Props>();
// 上传图片
const UpImage = () => {
  openFileModal(true, {
    filetype: 'image',
    getnumber: props.multi ? 'more' : 'one', // one 单张
    openfrom: 'manage' // manage管理 use 选择使用
  });
};
// 选择附件返回
const selectImg = (item: any) => {
  if (item.type == 'more') {
    item.list.forEach((img: any) => {
      console.log('多张附件返回:', img);
    });
    emit('update:modelValue', item.list);
  } else if (item.type == 'one') {
    emit('update:modelValue', item.url);
  }
};
</script>

<style lang="less" scoped></style>
