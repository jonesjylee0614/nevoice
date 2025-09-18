import { useUserStore } from '@/store';

function checkPermission(el: HTMLElement, binding: DirectiveBinding) {
  const { value } = binding;
  const userStore = useUserStore();
  const { role, perms } = userStore;

  if (Array.isArray(value)) {
    if (value.length > 0) {
      const hasRole = value.includes(role);
      const hasPerm = perms.includes('*') || perms.some(perm => value.includes(perm));
      const hasPermission = hasRole || hasPerm;
      if (!hasPermission && el.parentNode) {
        el.parentNode.removeChild(el);
      }
    }
  } else {
    throw new TypeError(`need roles! Like v-permission="['admin','user']"`);
  }
}

export default {
  mounted(el: HTMLElement, binding: DirectiveBinding) {
    checkPermission(el, binding);
  },
  updated(el: HTMLElement, binding: DirectiveBinding) {
    checkPermission(el, binding);
  }
};
