// 测试工具配置
const Config = {
    // 默认服务器配置
    DEFAULT_SERVER_URL: 'http://localhost:8210',
    
    // 可选的服务器地址
    SERVER_OPTIONS: {
        'localhost': 'http://localhost:8210',
        'wsl-localhost': 'http://localhost:8210',        // WSL内部访问
        'wsl-host': 'http://172.31.77.180:8210',         // WSL对外IP
        'wsl-bridge': 'http://127.0.0.1:8210',           // WSL桥接
        'development': 'http://172.31.77.180:8210',      // 开发环境地址（保持兼容）
        'production': 'http://127.0.0.1:8210',          // 生产环境地址
        'custom': ''                                     // 自定义地址
    },
    
    // API端点
    ENDPOINTS: {
        HEALTH: '/',
        EMBEDDING: '/embedding',
        VOICE_REGISTER: '/voice-register',
        VOICE_RECOGNIZE_OFFLINE: '/voice-recognize-offline',
        VOICE_RECOGNIZE_ONLINE: '/voice-recognize-online'
    },
    
    // 请求超时设置（增加超时时间）
    TIMEOUT: {
        DEFAULT: 10000,      // 10秒，原来5秒
        FILE_UPLOAD: 60000,  // 60秒，原来30秒
        NETWORK_CHECK: 15000 // 15秒，专门用于网络检查
    },
    
    // 网络检查配置
    NETWORK: {
        RETRY_COUNT: 3,      // 重试次数
        RETRY_DELAY: 2000    // 重试延迟(毫秒)
    }
};

// 全局变量
let baseUrl = Config.DEFAULT_SERVER_URL;

// 导出配置供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Config;
} 