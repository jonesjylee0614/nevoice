import NProgress from 'nprogress'; // progress bar
import { useAppStore, useUserStore } from '@/store';
import usePermission from '@/hooks/permission';
import { isLogin } from '@/utils/auth';
import { appRoutes } from '../routes';
import { NOT_FOUND, WHITE_LIST } from '../constants';

export default function setupPermissionGuard(router: Router) {
  router.beforeEach(async (to, from, next) => {
    const appStore = useAppStore();
    const userStore = useUserStore();
    const Permission = usePermission();
    const permissionsAllow = Permission.accessRouter(to);
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.debug('[router:guard:perm]', {
        to: to.fullPath,
        name: to.name,
        allow: permissionsAllow,
        menuFromServer: appStore.menuFromServer,
        isLogin: isLogin()
      });
    }
    if (appStore.menuFromServer && isLogin()) {
      // 针对来自服务端的菜单配置进行处理
      // Handle routing configuration from the server
      if (appStore.getIsDynamicAddedRoute) {
        // 判断是否已经加载路由组件
        next();
        NProgress.done();
        return;
      }
      // 根据需要自行完善来源于服务端的菜单配置的permission逻辑
      // Refine the permission logic from the server's menu configuration as needed
      if (!appStore.appAsyncRoute.length) {
        await appStore.fetchServerMenuConfig();
        // 加载路由组件
        appStore.appAsyncRoute.forEach(route => {
          router.addRoute(route as unknown as RouteRecordRaw);
        });
        appStore.setDynamicAddedRoute(true);
      }
      const serverMenuConfig = [...appStore.appAsyncRoute, ...WHITE_LIST];
      let exist = false;
      const targetFullPath = to.fullPath?.split('?')[0] || to.path;
      while (serverMenuConfig.length && !exist) {
        const element = serverMenuConfig.shift();
        if (!element) continue;
        // 允许 name 或 path 命中
        const elementPath = (element as any).path as string;
        if (element?.name === to.name || elementPath === targetFullPath || elementPath === to.path) {
          exist = true;
        }
        if (element?.children) {
          serverMenuConfig.push(...(element.children as unknown as RouteRecordNormalized[]));
        }
      }
      if (import.meta.env.DEV) {
        // eslint-disable-next-line no-console
        console.debug('[router:guard:perm:server-check]', { exist, to: to.name });
      }
      if (exist && permissionsAllow) {
        // 动态添加路由后，此处应当重定向到fullPath，否则会加载404页面内容
        next({ path: to.fullPath, replace: true, query: to.query });
      } else next(NOT_FOUND);
    } else {
      // eslint-disable-next-line no-lonely-if
      if (permissionsAllow) next();
      else {
        const destination =
          // Permission.findFirstPermissionRoute(appRoutes, userStore.role) ||
          NOT_FOUND;
        if (import.meta.env.DEV) {
          // eslint-disable-next-line no-console
          console.debug('[router:guard:perm:deny]', { to: to.fullPath, go: destination });
        }
        next(destination);
      }
    }
    NProgress.done();
  });
}
