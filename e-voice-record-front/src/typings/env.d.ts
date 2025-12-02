/**
 * Namespace Env
 *
 * It is used to declare the type of the import.meta object
 */
declare namespace Env {
  type RouterHistoryMode = 'hash' | 'history' | 'memory';

  interface ImportMeta extends ImportMetaEnv {
    /** The base url of the application */
    readonly VITE_BASE_URL: string;
    /** The title of the application */
    readonly VITE_APP_TITLE: string;

    readonly VITE_SERVER_URL: string;
    readonly VITE_WEBSOCKET_URL: string;
    readonly VITE_ROUTER_HISTORY_MODE?: RouterHistoryMode;
  }
}

