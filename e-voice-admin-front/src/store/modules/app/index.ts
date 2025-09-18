import type { RouteRecordNormalized } from 'vue-router';
import { defineStore } from 'pinia';
import { cloneDeep } from 'lodash-es';
import { Message, Notification } from '@arco-design/web-vue';
import defaultSettings from '@/config/settings.json';
import { getMenuList } from '@/api/user';
import type { AppRouteRecordRaw } from '@/router/types';
import { transformObjToRoute } from '@/router/helper/routeHelper';
import type { AppState } from './types';

const useAppStore = defineStore('app', {
  state: (): AppState => ({ ...defaultSettings }),

  getters: {
    appCurrentSetting(state: AppState): AppState {
      return { ...state };
    },
    appDevice(state: AppState) {
      return state.device;
    },
    appAsyncMenus(state: AppState): RouteRecordNormalized[] {
      return state.serverMenu as unknown as RouteRecordNormalized[];
    },
    appAsyncRoute(state: AppState): RouteRecordNormalized[] {
      return state.serverRoute as unknown as RouteRecordNormalized[];
    },
    // 获取路由状态
    getIsDynamicAddedRoute(): boolean {
      return this.isDynamicAddedRoute;
    },
    // 获取主题
    getTheme(): string {
      return this.theme;
    }
  },

  actions: {
    // 规范化并合并服务端菜单：
    // 1) 合并相同 path 的顶级菜单（如重复的 /voice）并合并 children
    // 2) 将子路由 path 规范为绝对路径（父路径 + 子路径）
    // 3) 去重 children（按 path 或 component）并修复重名 name
    normalizeServerMenus(menus: any[]) {
      if (!Array.isArray(menus)) return menus;
      const byPath = new Map<string, any>();
      const ensureAbsoluteChildPath = (parentPath: string, childPath: string) => {
        if (!childPath) return parentPath;
        if (childPath.startsWith('http')) return childPath;
        if (childPath.startsWith('/')) return childPath;
        const base = parentPath.endsWith('/') ? parentPath.slice(0, -1) : parentPath;
        return `${base}/${childPath}`;
      };
      const uniqChildren = (children: any[]) => {
        const seen = new Map<string, any>();
        const result: any[] = [];
        children?.forEach((c: any) => {
          const key = c?.path || c?.component || c?.name || Math.random().toString(36).slice(2);
          if (!seen.has(key)) {
            seen.set(key, true);
            result.push(c);
          }
        });
        // 修复重名（仅在同一父级内）
        const nameCount = new Map<string, number>();
        result.forEach((c: any) => {
          if (!c?.name) return;
          const n = nameCount.get(c.name) || 0;
          if (n > 0) c.name = `${c.name}_${n + 1}`;
          nameCount.set(c.name, n + 1);
        });
        return result;
      };
      menus.forEach((m: any) => {
        if (!m || !m.path) return;
        if (!byPath.has(m.path)) {
          // 深拷贝，避免修改原对象
          const clone = JSON.parse(JSON.stringify(m));
          byPath.set(m.path, clone);
        } else {
          const existed = byPath.get(m.path);
          const merged: any = existed;
          const incoming = m;
          const children = [...(merged.children || []), ...(incoming.children || [])];
          merged.children = children;
          // 保留第一个的 meta/icon 等，其余忽略
        }
      });
      // 规范 children 路径并去重
      const mergedList = Array.from(byPath.values());
      mergedList.forEach((parent: any) => {
        if (!parent?.children?.length) return;
        parent.children = parent.children.map((c: any) => ({
          ...c,
          path: ensureAbsoluteChildPath(parent.path, c.path)
        }));
        parent.children = uniqChildren(parent.children);
      });
      return mergedList;
    },
    // 设置动态路由加载状态
    setDynamicAddedRoute(added: boolean) {
      this.isDynamicAddedRoute = added;
    },
    // Update app settings
    updateSettings(partial: Partial<AppState>) {
      this.$patch(partial as any);
    },

    // Change theme color
    toggleTheme(dark: boolean) {
      if (dark) {
        this.theme = 'dark';
        document.body.setAttribute('arco-theme', 'dark');
      } else {
        this.theme = 'light';
        document.body.removeAttribute('arco-theme');
      }
    },
    toggleDevice(device: string) {
      this.device = device;
    },
    toggleMenu(value: boolean) {
      this.hideMenu = value;
    },
    async fetchServerMenuConfig() {
      try {
        const data = await getMenuList();
        const normalized = this.normalizeServerMenus(data);
        this.serverMenu = normalized;
        // 动态引入组件
        const routeList: AppRouteRecordRaw[] = cloneDeep(normalized);
        this.serverRoute = transformObjToRoute(routeList);
        Message.success({ content: '加载完成', id: 'menuNotice' });
      } catch (error) {
        Notification.error({
          id: 'menuNotice',
          title: '错误提示',
          content: '加载菜单出错了!',
          position: 'bottomRight'
        });
      }
    },
    clearServerMenu() {
      this.serverMenu = [];
    }
  }
});

export default useAppStore;
