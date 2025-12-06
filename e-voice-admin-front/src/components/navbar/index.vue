<template>
  <div class="navbar">
    <div class="left-side">
      <ASpace>
        <img alt="logo" src="/logo.png" style="height: 33px; overflow: hidden" />
        <ATypographyTitle :style="{ margin: 0, fontSize: '18px' }" :heading="5">
          {{ AppTitle }}
        </ATypographyTitle>
        <icon-menu-fold
          v-if="!topMenu && appStore.device === 'mobile'"
          style="font-size: 22px; cursor: pointer"
          @click="toggleDrawerMenu"
        />
      </ASpace>
    </div>
    <div class="center-side">
      <Menu v-if="topMenu" />
    </div>
    <ul class="right-side">
      <!--
<li>
  <ATooltip :content="$t('settings.search')">
    <AButton class="nav-btn" type="outline" shape="circle">
      <template #icon>
        <icon-search />
      </template>
    </AButton>
  </ATooltip>
</li>
<li>
  <ATooltip :content="$t('settings.language')">
    <AButton class="nav-btn" type="outline" shape="circle" @click="setDropDownVisible">
      <template #icon>
        <icon-language />
      </template>
    </AButton>
  </ATooltip>
  <ADropdown trigger="click" @select="changeLocale as any">
    <div ref="triggerBtn" class="trigger-btn"></div>
    <template #content>
      <ADoption v-for="item in locales" :key="item.value" :value="item.value">
        <template #icon>
          <icon-check v-show="item.value === currentLocale" />
        </template>
        {{ item.label }}
      </ADoption>
    </template>
  </ADropdown>
</li>
-->
      <li>
        <ATooltip
          :content="theme === 'light' ? $t('settings.navbar.theme.toDark') : $t('settings.navbar.theme.toLight')"
        >
          <AButton class="nav-btn" type="outline" shape="circle" @click="handleToggleTheme">
            <template #icon>
              <icon-moon-fill v-if="theme === 'dark'" />
              <icon-sun-fill v-else />
            </template>
          </AButton>
        </ATooltip>
      </li>
      <!--      <li>-->
      <!--        <ATooltip :content="$t('settings.navbar.alerts')">-->
      <!--          <div class="message-box-trigger">-->
      <!--            <ABadge :count="9" dot>-->
      <!--              <AButton class="nav-btn" type="outline" shape="circle" @click="setPopoverVisible">-->
      <!--                <icon-notification />-->
      <!--              </AButton>-->
      <!--            </ABadge>-->
      <!--          </div>-->
      <!--        </ATooltip>-->
      <!--        <APopover-->
      <!--          trigger="click"-->
      <!--          :arrow-style="{ display: 'none' }"-->
      <!--          :content-style="{ padding: 0, width: '400px' }"-->
      <!--          content-class="message-popover"-->
      <!--        >-->
      <!--          <div ref="refBtn" class="ref-btn"></div>-->
      <!--          <template #content>-->
      <!--            <MessageBox />-->
      <!--          </template>-->
      <!--        </APopover>-->
      <!--      </li>-->
      <li>
        <ATooltip :content="isFullscreen ? $t('settings.navbar.screen.toExit') : $t('settings.navbar.screen.toFull')">
          <AButton class="nav-btn" type="outline" shape="circle" @click="toggleFullScreen">
            <template #icon>
              <icon-fullscreen-exit v-if="isFullscreen" />
              <icon-fullscreen v-else />
            </template>
          </AButton>
        </ATooltip>
      </li>
      <li>
        <ATooltip :content="$t('settings.title')">
          <AButton class="nav-btn" type="outline" shape="circle" @click="setVisible">
            <template #icon>
              <icon-settings />
            </template>
          </AButton>
        </ATooltip>
      </li>
      <li>
        <ADropdown trigger="click">
          <AAvatar :size="32" :style="{ marginRight: '8px', cursor: 'pointer' }">
            <ATooltip :content="username">
              <img alt="avatar" :src="avatar" />
            </ATooltip>
          </AAvatar>
          <template #content>
            <!--            <ADoption>-->
            <!--              <ASpace @click="$router.push({ path: '/user/info' })">-->
            <!--                <icon-user />-->
            <!--                <span>-->
            <!--                  {{ $t('messageBox.userCenter') }}-->
            <!--                </span>-->
            <!--              </ASpace>-->
            <!--            </ADoption>-->
            <ADoption>
              <ASpace @click="$router.push({ path: '/user/setting' })">
                <icon-settings />
                <span>
                  {{ $t('messageBox.userSettings') }}
                </span>
              </ASpace>
            </ADoption>
            <ADoption>
              <ASpace @click="handleLogout">
                <icon-export />
                <span>
                  {{ $t('messageBox.logout') }}
                </span>
              </ASpace>
            </ADoption>
          </template>
        </ADropdown>
      </li>
    </ul>
  </div>
</template>

<script lang="ts" setup>
import { useDark, useFullscreen, useToggle } from '@vueuse/core';
import { useAppStore, useUserStore } from '@/store';
import useLocale from '@/hooks/locale';
import useUser from '@/hooks/user';
import { LOCALE_OPTIONS } from '@/locale';
import MessageBox from '@/components/message-box/index.vue';
import Menu from '@/components/menu/index.vue';

const appStore = useAppStore();
const userStore = useUserStore();
const { logout } = useUser();
const { changeLocale, currentLocale } = useLocale();
const { isFullscreen, toggle: toggleFullScreen } = useFullscreen();
const locales = [...LOCALE_OPTIONS];
const avatar = computed(() => {
  console.log('avatar:', userStore.avatar);
  return userStore.avatar;
});
const username = computed(() => {
  return userStore.name;
});
const theme = computed(() => {
  return appStore.theme;
});
const topMenu = computed(() => appStore.topMenu && appStore.menu);
const isDark = useDark({
  selector: 'body',
  attribute: 'arco-theme',
  valueDark: 'dark',
  valueLight: 'light',
  storageKey: 'arco-theme',
  onChanged(dark: boolean) {
    // overridden default behavior
    appStore.toggleTheme(dark);
  }
});
const toggleTheme = useToggle(isDark);
const handleToggleTheme = () => {
  toggleTheme();
};
const setVisible = () => {
  appStore.updateSettings({ globalSettings: true });
};
const refBtn = ref();
const triggerBtn = ref();
const setPopoverVisible = () => {
  const event = new MouseEvent('click', {
    view: window,
    bubbles: true,
    cancelable: true
  });
  refBtn.value.dispatchEvent(event);
};
const handleLogout = () => {
  logout();
};
const setDropDownVisible = () => {
  const event = new MouseEvent('click', {
    view: window,
    bubbles: true,
    cancelable: true
  });
  triggerBtn.value.dispatchEvent(event);
};
const toggleDrawerMenu = inject('toggleDrawerMenu') as () => void;
// 获取网站配置-应用名称
const AppTitle = import.meta.env.VITE_APP_TITLE;
</script>

<style scoped lang="less">
.navbar {
  display: flex;
  justify-content: space-between;
  height: 100%;
  background-color: var(--color-bg-2);
  border-bottom: 1px solid var(--color-border);
}

.left-side {
  display: flex;
  align-items: center;
  padding-left: 20px;
}

.center-side {
  flex: 1;
}

.right-side {
  display: flex;
  padding-right: 20px;
  list-style: none;
  :deep(.locale-select) {
    border-radius: 20px;
  }
  li {
    display: flex;
    align-items: center;
    padding: 0 10px;
  }

  a {
    color: var(--color-text-1);
    text-decoration: none;
  }
  .nav-btn {
    border-color: rgb(var(--gray-2));
    color: rgb(var(--gray-8));
    font-size: 16px;
  }
  .trigger-btn,
  .ref-btn {
    position: absolute;
    bottom: 14px;
  }
  .trigger-btn {
    margin-left: 14px;
  }
}
</style>

<style lang="less">
.message-popover {
  .arco-popover-content {
    margin-top: 0;
  }
}
</style>
