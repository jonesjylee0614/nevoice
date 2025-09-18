// 共用工具函数

// 工具函数
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.remove('hidden');
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.add('hidden');
    }
}

function showResponse(responseId, statusId, timeId, contentId, status, responseTime, content) {
    const responseDiv = document.getElementById(responseId);
    const statusSpan = document.getElementById(statusId);
    const timeSpan = document.getElementById(timeId);
    const contentDiv = document.getElementById(contentId);

    if (!responseDiv || !statusSpan || !timeSpan || !contentDiv) {
        console.error('找不到响应显示元素');
        return;
    }

    responseDiv.classList.remove('hidden');
    
    // 设置状态样式
    statusSpan.className = 'response-status';
    if (status >= 200 && status < 300) {
        statusSpan.classList.add('status-200');
    } else if (status >= 400 && status < 500) {
        statusSpan.classList.add('status-400');
    } else {
        statusSpan.classList.add('status-500');
    }
    
    statusSpan.textContent = `${status}`;
    timeSpan.textContent = `响应时间: ${responseTime}ms`;
    
    // 格式化内容
    try {
        if (typeof content === 'string') {
            try {
                const jsonContent = JSON.parse(content);
                contentDiv.textContent = JSON.stringify(jsonContent, null, 2);
            } catch {
                contentDiv.textContent = content;
            }
        } else {
            contentDiv.textContent = JSON.stringify(content, null, 2);
        }
    } catch {
        contentDiv.textContent = content;
    }
}

// 改进的服务器状态检查（支持重试）
async function checkServerStatus(retryCount = 0) {
    const statusSpan = document.getElementById('serverStatus');
    if (!statusSpan) return;

    if (retryCount === 0) {
        statusSpan.className = 'status-indicator status-checking';
        statusSpan.textContent = '检查中...';
    } else {
        statusSpan.textContent = `检查中... (重试 ${retryCount}/${Config.NETWORK.RETRY_COUNT})`;
    }

    try {
        const startTime = Date.now();
        
        // 使用更长的超时时间进行网络检查
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), Config.TIMEOUT.NETWORK_CHECK);
        
        const response = await fetch(`${baseUrl}/`, {
            method: 'GET',
            signal: controller.signal,
            mode: 'cors',
            cache: 'no-cache'
        });
        
        clearTimeout(timeoutId);
        const responseTime = Date.now() - startTime;

        if (response.ok) {
            const text = await response.text();
            statusSpan.className = 'status-indicator status-online';
            statusSpan.textContent = `在线 (${responseTime}ms)`;
            
            // 验证响应内容
            if (text.trim() === 'success') {
                console.log(`服务器连接成功: ${baseUrl}`);
            } else {
                console.warn(`服务器响应异常: ${text}`);
            }
        } else {
            statusSpan.className = 'status-indicator status-offline';
            statusSpan.textContent = `HTTP错误 ${response.status}`;
            
            // 如果还有重试次数，则重试
            if (retryCount < Config.NETWORK.RETRY_COUNT) {
                setTimeout(() => {
                    checkServerStatus(retryCount + 1);
                }, Config.NETWORK.RETRY_DELAY);
            }
        }
    } catch (error) {
        console.error('服务器连接检查失败:', error);
        
        let errorMessage = '离线';
        if (error.name === 'AbortError') {
            errorMessage = '超时';
        } else if (error.message.includes('CORS')) {
            errorMessage = 'CORS错误';
        } else if (error.message.includes('network')) {
            errorMessage = '网络错误';
        } else if (error.message.includes('fetch')) {
            errorMessage = '连接失败';
        }
        
        statusSpan.className = 'status-indicator status-offline';
        
        // 如果还有重试次数，则重试
        if (retryCount < Config.NETWORK.RETRY_COUNT) {
            statusSpan.textContent = `${errorMessage} (${retryCount + 1}/${Config.NETWORK.RETRY_COUNT + 1})`;
            setTimeout(() => {
                checkServerStatus(retryCount + 1);
            }, Config.NETWORK.RETRY_DELAY);
        } else {
            statusSpan.textContent = `${errorMessage} (已重试${Config.NETWORK.RETRY_COUNT}次)`;
            
            // 提供网络诊断建议
            console.group('网络诊断建议:');
            console.log(`目标地址: ${baseUrl}`);
            console.log('可能的问题:');
            console.log('1. 服务器未启动 - 检查 rest.py 是否运行');
            console.log('2. 端口被占用 - 尝试其他端口');
            console.log('3. WSL网络问题 - 尝试不同的网络选项');
            console.log('4. 防火墙阻止 - 检查防火墙设置');
            console.groupEnd();
        }
    }
}

// 更新服务器地址
function updateServerUrl(newUrl) {
    if (!newUrl) return;
    
    baseUrl = newUrl.trim();
    if (baseUrl.endsWith('/')) {
        baseUrl = baseUrl.slice(0, -1);
    }
    
    console.log(`切换到服务器地址: ${baseUrl}`);
    
    // 自动检查新地址的状态
    checkServerStatus();
}

// 文件选择处理
function handleFileSelect(input, labelId) {
    const label = document.getElementById(labelId);
    if (!label) return;

    if (input.files && input.files[0]) {
        const file = input.files[0];
        label.classList.add('file-selected');
        label.innerHTML = `
            已选择文件: ${file.name}<br>
            <small>大小: ${(file.size / 1024 / 1024).toFixed(2)} MB</small>
        `;
    } else {
        label.classList.remove('file-selected');
        label.innerHTML = `
            点击选择音频文件或拖拽文件到此处<br>
            <small>支持 WAV, MP3, M4A 等格式</small>
        `;
    }
}

// 设置拖拽上传
function setupDragAndDrop(labelId, inputId) {
    const fileInputLabel = document.getElementById(labelId);
    const fileInput = document.getElementById(inputId);
    
    if (!fileInputLabel || !fileInput) return;
    
    fileInputLabel.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.style.background = '#e3f2fd';
    });
    
    fileInputLabel.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.style.background = '';
    });
    
    fileInputLabel.addEventListener('drop', function(e) {
        e.preventDefault();
        this.style.background = '';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelect(fileInput, labelId);
        }
    });
}

// 清空所有结果
function clearAllResults(responseIds) {
    if (!responseIds) {
        // 默认的响应元素ID列表
        responseIds = [
            'healthResponse', 'embeddingResponse', 'voiceResponse', 
            'customResponse', 'batchResults', 'offlineResponse', 
            'onlineResponse', 'realtimeResponse'
        ];
    }
    
    responseIds.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.classList.add('hidden');
        }
    });
}

// 初始化页面
function initializePage() {
    // 页面加载完成后自动检查服务器状态
    setTimeout(() => {
        checkServerStatus();
    }, 500); // 稍微延迟，确保页面完全加载
    
    // 设置服务器地址变更监听
    const serverUrlInput = document.getElementById('serverUrl');
    if (serverUrlInput) {
        serverUrlInput.addEventListener('change', function() {
            updateServerUrl(this.value);
        });
    }
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePage);
} else {
    initializePage();
} 