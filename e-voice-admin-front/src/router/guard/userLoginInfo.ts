import NProgress from 'nprogress'; // progress bar
import { useUserStore } from '@/store';
import { isLogin } from '@/utils/auth';

export default function setupUserLoginInfoGuard(router: Router) {
  router.beforeEach(async (to, from, next) => {
    NProgress.start();
    const userStore = useUserStore();
    if (isLogin()) {
      if (userStore.userId) {
        if (import.meta.env.DEV) {
          // eslint-disable-next-line no-console
          console.debug('[router:guard:user] logged-in cached', { to: to.fullPath });
        }
        next();
      } else {
        try {
          await userStore.info();
          if (import.meta.env.DEV) {
            // eslint-disable-next-line no-console
            console.debug('[router:guard:user] fetched user info');
          }
          next();
        } catch (error) {
          await userStore.logout();
          if (import.meta.env.DEV) {
            // eslint-disable-next-line no-console
            console.debug('[router:guard:user] fetch user info failed, redirect to login');
          }
          next({
            name: 'login',
            query: {
              redirect: to.name,
              ...to.query
            } as LocationQueryRaw
          });
        }
      }
    } else {
      if (to.name === 'login') {
        next();
        return;
      }
      if (import.meta.env.DEV) {
        // eslint-disable-next-line no-console
        console.debug('[router:guard:user] not login, redirect to login');
      }
      next({
        name: 'login',
        query: {
          redirect: to.name,
          ...to.query
        } as LocationQueryRaw
      });
    }
  });
}
