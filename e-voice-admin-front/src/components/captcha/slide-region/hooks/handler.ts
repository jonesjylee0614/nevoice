import type { Ref } from 'vue';
import { reactive } from 'vue';
import type { CaptchaData, CaptchaEvent } from '@/components/captcha/types';
import { checkTargetFather } from '../../helper';

// eslint-disable-next-line max-params
export const useHandler = (data: Ref<CaptchaData>, event: CaptchaEvent, containerRef: Ref, tileRef: Ref) => {
  const state = reactive<{ x: number; y: number }>({ x: data.value.thumbX || 0, y: data.value.thumbY || 0 });

  const clear = () => {
    state.x = data.value.thumbX || 0;
    state.y = data.value.thumbY || 0;
  };

  const dragEvent = (e: Event | any) => {
    const touch = e.touches && e.touches[0];
    const offsetLeft = tileRef.value.offsetLeft;
    const offsetTop = tileRef.value.offsetTop;
    const width = containerRef.value.offsetWidth;
    const height = containerRef.value.offsetHeight;
    const tileWidth = tileRef.value.offsetWidth;
    const tileHeight = tileRef.value.offsetHeight;
    const maxWidth = width - tileWidth;
    const maxHeight = height - tileHeight;

    let isMoving = false;
    let startX = 0;
    let startY = 0;
    let tileLeft = 0;
    let tileTop = 0;
    if (touch) {
      startX = touch.pageX - offsetLeft;
      startY = touch.pageY - offsetTop;
    } else {
      startX = e.clientX - offsetLeft;
      startY = e.clientY - offsetTop;
    }

    // eslint-disable-next-line @typescript-eslint/no-shadow
    const moveEvent = (e: Event | any) => {
      isMoving = true;
      const mTouche = e.touches && e.touches[0];

      let left: number;
      let top: number;
      if (mTouche) {
        left = mTouche.pageX - startX;
        top = mTouche.pageY - startY;
      } else {
        left = e.clientX - startX;
        top = e.clientY - startY;
      }

      if (left <= 0) {
        left = 0;
      }

      if (top <= 0) {
        top = 0;
      }

      if (left >= maxWidth) {
        left = maxWidth;
      }

      if (top >= maxHeight) {
        top = maxHeight;
      }

      state.x = left;
      state.y = top;
      tileLeft = left;
      tileTop = top;
      event.move && event.move(left, top);

      e.cancelBubble = true;
      e.preventDefault();
    };

    // eslint-disable-next-line @typescript-eslint/no-shadow
    const upEvent = (e: Event | any) => {
      if (!checkTargetFather(containerRef.value, e)) {
        return;
      }

      if (!isMoving) {
        return;
      }
      isMoving = false;

      containerRef.value.removeEventListener('mousemove', moveEvent, false);
      containerRef.value.removeEventListener('touchmove', moveEvent, { passive: false });

      containerRef.value.removeEventListener('mouseup', upEvent, false);
      containerRef.value.removeEventListener('mouseout', upEvent, false);
      containerRef.value.removeEventListener('touchend', upEvent, false);

      event.confirm &&
        event.confirm({ position: { x: tileLeft, y: tileTop } }, () => {
          clear();
        });

      e.cancelBubble = true;
      e.preventDefault();
    };

    containerRef.value.addEventListener('mousemove', moveEvent, false);
    containerRef.value.addEventListener('touchmove', moveEvent, { passive: false });
    containerRef.value.addEventListener('mouseup', upEvent, false);
    containerRef.value.addEventListener('mouseout', upEvent, false);
    containerRef.value.addEventListener('touchend', upEvent, false);
  };

  const closeEvent = (e: Event | any) => {
    event && event.close && event.close();
    clear();
    e.cancelBubble = true;
    e.preventDefault();
    return false;
  };

  const refreshEvent = (e: Event | any) => {
    event && event.refresh && event.refresh();
    clear();
    e.cancelBubble = true;
    e.preventDefault();
    return false;
  };

  return {
    state,
    dragEvent,
    closeEvent,
    refreshEvent
  };
};
