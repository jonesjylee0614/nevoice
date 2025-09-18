// 左侧导航组件

// 导航配置
const Navigation = {
    // 主页面
    pages: {
        main: {
            title: 'API测试工具',
            url: 'test_page.html',
            description: '主入口页面',
            icon: '🏠'
        },
        voiceRegister: {
            title: '语音注册测试',
            url: 'pages/voice-test.html',
            description: '语音注册、声纹识别',
            icon: '🎤'
        },
        speechRecognition: {
            title: '语音识别测试',
            url: 'pages/speech-recognition-test.html',
            description: '实时语音识别、录音测试',
            icon: '🗣️'
        },
        embedding: {
            title: 'Embedding测试',
            url: 'pages/embedding-test.html',
            description: '文本向量化、批量测试',
            icon: '🧠'
        }
    },
    
    // 获取当前页面信息
    getCurrentPage: function() {
        const path = window.location.pathname;
        const filename = path.split('/').pop();
        
        for (const [key, page] of Object.entries(this.pages)) {
            if (page.url.includes(filename) || filename.includes(page.url.split('/').pop())) {
                return { key, ...page };
            }
        }
        return { key: 'unknown', title: '未知页面', url: '', description: '' };
    },
    
    // 生成面包屑导航
    generateBreadcrumb: function() {
        const current = this.getCurrentPage();
        const isSubPage = current.url.includes('pages/');
        
        let breadcrumb = '<div class="breadcrumb">';
        
        if (isSubPage) {
            breadcrumb += `<a href="../test_page.html" class="breadcrumb-item">${this.pages.main.icon} 主页</a>`;
            breadcrumb += `<span class="breadcrumb-separator">></span>`;
        }
        
        breadcrumb += `<span class="breadcrumb-current">${current.icon || '📄'} ${current.title}</span>`;
        breadcrumb += '</div>';
        
        return breadcrumb;
    },
    
    // 生成侧边栏
    generateSidebar: function() {
        const current = this.getCurrentPage();
        const isSubPage = current.url.includes('pages/');
        const basePath = isSubPage ? '../' : '';
        
        let sidebar = `
            <div class="sidebar" id="sidebar">
                <div class="sidebar-header">
                    <h2>E-Voice 测试</h2>
                    <p>智能语音识别系统</p>
                </div>
                ${this.generateBreadcrumb()}
                <div class="nav-menu">
                    <h4>📋 功能模块</h4>
                    <div class="nav-list">
        `;
        
        for (const [key, page] of Object.entries(this.pages)) {
            const isActive = key === current.key;
            const activeClass = isActive ? 'nav-item-active' : '';
            const url = basePath + page.url;
            
            sidebar += `
                <a href="${url}" class="nav-item ${activeClass}" ${isActive ? 'onclick="return false;"' : ''}>
                    <div class="nav-item-title">${page.icon} ${page.title}</div>
                    <div class="nav-item-desc">${page.description}</div>
                </a>
            `;
        }
        
        sidebar += `
                    </div>
                </div>
            </div>
            <button class="sidebar-toggle" onclick="Navigation.toggleSidebar()">
                ☰
            </button>
        `;
        
        return sidebar;
    },
    
    // 切换侧边栏（移动端）
    toggleSidebar: function() {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) {
            sidebar.classList.toggle('active');
        }
    },
    
    // 初始化导航
    init: function() {
        this.createLayout();
        
        // 为移动端添加点击外部关闭侧边栏的功能
        document.addEventListener('click', (e) => {
            const sidebar = document.getElementById('sidebar');
            const toggle = document.querySelector('.sidebar-toggle');
            
            if (sidebar && !sidebar.contains(e.target) && !toggle.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        });
    },
    
    // 创建新的页面布局
    createLayout: function() {
        const body = document.body;
        
        // 检查是否已经有布局
        if (body.querySelector('.app-layout')) return;
        
        // 获取现有内容
        const existingContent = body.innerHTML;
        
        // 创建新的布局结构
        body.innerHTML = `
            <div class="app-layout">
                ${this.generateSidebar()}
                <div class="main-panel">
                    ${existingContent}
                </div>
            </div>
        `;
        
        // 移除body的背景样式，因为现在由app-layout处理
        body.style.background = 'none';
        body.style.padding = '0';
    }
};

// 页面加载完成后初始化导航
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Navigation.init());
} else {
    Navigation.init();
} 