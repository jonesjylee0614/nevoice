import { setRouteEmitter } from '@/utils/route-listener';
import setupUserLoginInfoGuard from './userLoginInfo';
import setupPermissionGuard from './permission';

function setupPageGuard(router: Router) {
  router.beforeEach(async to => {
    // emit route change
    setRouteEmitter(to);
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.debug('[router:page]', { to: to.fullPath, name: to.name });
    }
  });
}

export default function createRouteGuard(router: Router) {
  setupPageGuard(router);
  setupUserLoginInfoGuard(router);
  setupPermissionGuard(router);
}
