/**
 * @author Awen
 * @Date 2024/05/25
 * @Email wengaolng@gmail.com
 */

export const getDomXY = (dom: any) => {
  let x = 0;
  let y = 0;
  if (dom.getBoundingClientRect) {
    const box = dom.getBoundingClientRect();
    const D = document.documentElement;
    x = box.left + Math.max(D.scrollLeft, document.body.scrollLeft) - D.clientLeft;
    y = box.top + Math.max(D.scrollTop, document.body.scrollTop) - D.clientTop;
  } else {
    while (dom !== document.body) {
      x += dom.offsetLeft;
      y += dom.offsetTop;
      // eslint-disable-next-line no-param-reassign
      dom = dom.offsetParent;
    }
  }
  return {
    domX: x,
    domY: y
  };
};

export const checkTargetFather = (that: any, e: any) => {
  let parent = e.relatedTarget;
  try {
    while (parent && parent !== that) {
      parent = parent.parentNode;
    }
    // eslint-disable-next-line @typescript-eslint/no-shadow
  } catch (e) {}

  return parent !== that;
};
