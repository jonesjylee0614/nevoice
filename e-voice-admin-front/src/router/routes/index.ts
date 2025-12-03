import type { RouteRecordNormalized } from 'vue-router';
import type { AppRouteModule } from '@/router/types';
import { flatMultiLevelRoutes, transformObjToRoute } from '@/router/helper/routeHelper';
const modules = import.meta.glob('./modules/*.ts', { eager: true });
// 外连接不需要添加组件到路由
const externalModules = import.meta.glob('./externalModules/*.ts', {
  eager: true
});

function formatModules(_modules: any, result: RouteRecordNormalized[]) {
  Object.keys(_modules).forEach(key => {
    const defaultModule = _modules[key].default;
    if (!defaultModule) return;
    const moduleList = Array.isArray(defaultModule) ? [...defaultModule] : [defaultModule];
    result.push(...moduleList);
  });
  return result;
}
export const appExternalRoutes: RouteRecordNormalized[] = formatModules(externalModules, []);
// 将静态模块中的字符串 component 映射为实际组件，并拍平成二级路由，修复无效组件与 name 不匹配问题
const transformed = transformObjToRoute(formatModules(modules, []) as unknown as AppRouteModule[]);
export const appRoutes: RouteRecordNormalized[] = flatMultiLevelRoutes(
  transformed
) as unknown as RouteRecordNormalized[];
