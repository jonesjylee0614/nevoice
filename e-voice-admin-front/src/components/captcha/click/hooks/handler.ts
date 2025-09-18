import { reactive } from 'vue';
import type { CaptchaData, CaptchaEvent, Point } from '@/components/captcha/types';
import { getDomXY } from '../../helper';

export function useHandler(_data: CaptchaData, event: CaptchaEvent) {
  const dots = reactive<{ list: Array<Point> }>({ list: [] });

  const clickEvent = (e: Event | any) => {
    const dom = e.currentTarget;
    const xy = getDomXY(dom);

    const mouseX = e.pageX || e.clientX;
    const mouseY = e.pageY || e.clientY;

    const domX = xy.domX;
    const domY = xy.domY;

    const xPos = mouseX - domX;
    const yPos = mouseY - domY;

    const xx = Number.parseInt(xPos.toString(), 10);
    const yy = Number.parseInt(yPos.toString(), 10);
    const date = new Date();
    const index = dots.list.length;
    const list = dots.list;
    list.push({ key: date.getTime(), index: index + 1, x: xx, y: yy });
    dots.list = list;

    event.click && event.click(xx, yy);
    e.cancelBubble = true;
    e.preventDefault();
    return false;
  };

  const confirmEvent = (e: Event | any) => {
    event.confirm &&
      event.confirm({ points: dots.list }, () => {
        dots.list = [];
      });
    e.cancelBubble = true;
    e.preventDefault();
    return false;
  };

  const closeEvent = (e: Event | any) => {
    event.close && event.close();
    dots.list = [];
    e.cancelBubble = true;
    e.preventDefault();
    return false;
  };

  const refreshEvent = (e: Event | any) => {
    event.refresh && event.refresh();
    dots.list = [];
    e.cancelBubble = true;
    e.preventDefault();
    return false;
  };

  return {
    dots,
    clickEvent,
    confirmEvent,
    closeEvent,
    refreshEvent
  };
}
