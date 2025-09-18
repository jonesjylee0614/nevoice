<template>
  <div>
    <FileManage @register="registerModal" @success="selectImg" />
  </div>
</template>

<script lang="ts" setup>
import { useModal } from '@/components/Modal';

interface Props {
  defaultText: string;
  defaultLink: string;
  defaultjuptType: string;
  className: string;
  onLoad: () => void;
  onOk: (item: any) => void;
}
const props = defineProps<Props>();
const [registerModal, { openModal }] = useModal();
// 选图片
const selectImg = (item: any) => {
  if (props.onOk) props.onOk(item);
};
onMounted(() => {
  openModal(true, {
    filetype: 'image',
    getnumber: 'more', // one 单张
    openfrom: 'manage'
  });
});
</script>
