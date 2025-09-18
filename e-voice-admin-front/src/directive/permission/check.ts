import { useUserStore } from '@/store';

export function hasPerm(perm: string): boolean {
  const userStore = useUserStore();
  const { perms } = userStore;
  return perms.includes('*') || perms.includes(perm);
}
