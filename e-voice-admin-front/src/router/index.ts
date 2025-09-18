import NProgress from 'nprogress'; // progress bar
import 'nprogress/nprogress.css';
import { createRouter, createWebHashHistory } from 'vue-router';
import { appRoutes } from './routes';
import defaultSettings from '@/config/settings.json';
import { NOT_FOUND_ROUTE, REDIRECT_MAIN } from './routes/base';
import createRouteGuard from './guard';
NProgress.configure({ showSpinner: false }); // NProgress Configuration

const router = createRouter({
  // history: createWebHistory(),//history模式
  history: createWebHashHistory(process.env.NODE_ENV === 'production' ? '/webbusiness/' : ''), // has模式带#号
  routes: [
    {
      path: '/',
      redirect: '/home'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/login/index.vue'),
      meta: {
        requiresAuth: false
      }
    },
    ...(defaultSettings.menuFromServer ? [] : appRoutes),
    REDIRECT_MAIN,
    NOT_FOUND_ROUTE
  ],
  scrollBehavior() {
    return { top: 0 };
  }
});

// 开发环境下输出基础路由与history基路径，便于定位404/重定向问题
if (import.meta.env.DEV) {
  // eslint-disable-next-line no-console
  console.debug('[router:init]', {
    base: process.env.NODE_ENV === 'production' ? '/webbusiness/' : '',
    mode: 'hash',
    routes: router.getRoutes().map(r => ({ name: r.name, path: r.path }))
  });
}

createRouteGuard(router);

export default router;
