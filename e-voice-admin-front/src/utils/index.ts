import type { App, Plugin } from 'vue';
import { isObject } from '@/utils/is';

type TargetContext = '_self' | '_parent' | '_blank' | '_top';

export const openWindow = (url: string, opts?: { target?: TargetContext; [key: string]: any }) => {
  const { target = '_blank', ...others } = opts || {};
  window.open(
    url,
    target,
    Object.entries(others)
      .reduce((preValue: string[], curValue) => {
        const [key, value] = curValue;
        return [...preValue, `${key}=${value}`];
      }, [])
      .join(',')
  );
};

export const regexUrl =
  /^(?!mailto:)(?:http|https|ftp):\/\/(?:\S+(?::\S*)?@)?(?:(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}\.(?:[0-9]\d?|1\d\d|2[0-4]\d|25[0-4])|(?:[a-z\u00A1-\uFFFF0-9]+-?)*[a-z\u00A1-\uFFFF0-9]+(?:\.(?:[a-z\u00A1-\uFFFF0-9]+-?)*[a-z\u00A1-\uFFFF0-9]+)*\.[a-z\u00A1-\uFFFF]{2,})|localhost)(?::\d{2,5})?(?:([/?#])\S*)?$/i;

/**
 * Add the object as a parameter to the URL
 *
 * @param baseUrl url
 * @param obj
 * @returns {string} eg: let obj = {a: '3', b: '4'} setObjToUrlParams('www.baidu.com', obj) ==>www.baidu.com?a=3&b=4
 */
export function setObjToUrlParams(baseUrl: string, obj: any): string {
  let parameters = '';
  for (const key in obj) {
    parameters += `${key}=${encodeURIComponent(obj[key])}&`;
  }
  parameters = parameters.replace(/&$/, '');
  return /\?$/.test(baseUrl) ? baseUrl + parameters : baseUrl.replace(/\/?$/, '?') + parameters;
}

// 深度合并
export function deepMerge<T = any>(src: any = {}, target: any = {}): T {
  for (const key in target) {
    src[key] = isObject(src[key]) ? deepMerge(src[key], target[key]) : (src[key] = target[key]);
  }
  return src;
}
// 文档编辑器
export const getCurrentKey = () => {
  return localStorage.getItem('demo-key') || 'default';
};
export const setDocValue = (value: string, key: string = getCurrentKey()) => {
  localStorage.setItem(`${key}-demo-value`, value);
};

export const getDocValue = (key: string = getCurrentKey()) => {
  return localStorage.getItem(`${key}-demo-value`);
};
/** @description: Set ui mount node */
export function getPopupContainer(node?: HTMLElement): HTMLElement {
  return (node?.parentNode as HTMLElement) ?? document.body;
}
// 弹框
export const withInstall = <T>(component: T, alias?: string) => {
  const comp = component as any;
  comp.install = (app: App) => {
    app.component(comp.name || comp.displayName, component as any);
    if (alias) {
      app.config.globalProperties[alias] = component;
    }
  };
  return component as T & Plugin;
};

export function addTimestampToUrl(url: string) {
  // 获取当前时间的分钟级时间戳 (年月日时分)
  const now = new Date();
  const timestamp = `${now.getHours().toString().padStart(2, '0')}${now.getMinutes().toString().padStart(2, '0')}`;

  // 分离URL和hash部分
  const hashIndex = url.indexOf('#');
  let baseUrl = url;
  let hashPart = '';

  if (hashIndex !== -1) {
    baseUrl = url.substring(0, hashIndex);
    hashPart = url.substring(hashIndex);
  }

  if (!hashPart) {
    hashPart = '#/login';
  }

  // 解析URL参数部分
  let prefix = baseUrl;
  let queryPart = '';
  const queryIndex = baseUrl.indexOf('?');
  if (queryIndex !== -1) {
    prefix = baseUrl.substring(0, queryIndex);
    queryPart = baseUrl.substring(queryIndex + 1);
  }

  // 处理参数
  const params = new URLSearchParams(queryPart);
  params.set('v', timestamp);

  // 重新构建URL
  return `${prefix}?${params.toString()}${hashPart}`;
}

/** 给当前页面URL添加时间戳并刷新页面 */
export function refreshWithTimestamp() {
  window.location.href = addTimestampToUrl(window.location.href);
}
