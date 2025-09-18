import type { App } from 'vue';
import Toolbar from './components/toolbar.vue';
import { fontFamilyDefaultData, fontfamily, getToolbarDefaultConfig } from './config';
import ToolbarPlugin, { ToolbarComponent } from './plugin';
import type { ToolbarOptions } from './plugin';
import type { GroupItemProps, ToolbarItemProps, ToolbarProps } from './types';

Toolbar.install = (app: App) => {
  app.component(Toolbar.name, Toolbar);
};

export default Toolbar;
export {
  ToolbarPlugin,
  ToolbarComponent,
  getToolbarDefaultConfig as getDefaultConfig,
  fontFamilyDefaultData,
  fontfamily
};
export type { ToolbarOptions, ToolbarProps, GroupItemProps, ToolbarItemProps };
