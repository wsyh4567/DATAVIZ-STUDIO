/**
 * 代码复制功能
 * 
 * 处理代码复制到剪贴板的客户端逻辑
 */

// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    console.log('Code copy module loaded');
});

// 监听复制按钮点击
document.addEventListener('click', function(e) {
    // 检查是否点击了复制代码按钮
    if (e.target.id === 'btn-copy-code' || e.target.closest('#btn-copy-code')) {
        copyCodeToClipboard();
    }
});

/**
 * 复制代码到剪贴板
 */
function copyCodeToClipboard() {
    // 查找代码显示区域
    const codeElement = document.querySelector('#code-display-area code');
    
    if (!codeElement) {
        console.error('Code element not found');
        showCopyStatus('未找到代码', 'error');
        return;
    }
    
    const code = codeElement.textContent;
    
    // 使用现代 Clipboard API
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(code)
            .then(() => {
                console.log('Code copied to clipboard');
                showCopyStatus('代码已复制到剪贴板', 'success');
            })
            .catch(err => {
                console.error('Failed to copy code:', err);
                fallbackCopyToClipboard(code);
            });
    } else {
        // 降级方案
        fallbackCopyToClipboard(code);
    }
}

/**
 * 降级复制方案（兼容旧浏览器）
 */
function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            console.log('Code copied using fallback method');
            showCopyStatus('代码已复制到剪贴板', 'success');
        } else {
            console.error('Fallback copy failed');
            showCopyStatus('复制失败，请手动复制', 'error');
        }
    } catch (err) {
        console.error('Fallback copy error:', err);
        showCopyStatus('复制失败，请手动复制', 'error');
    }
    
    document.body.removeChild(textArea);
}

/**
 * 显示复制状态提示
 */
function showCopyStatus(message, type) {
    // 创建提示元素
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'success' ? 'success' : 'danger'} position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 250px;';
    toast.innerHTML = `
        <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
        ${message}
    `;
    
    document.body.appendChild(toast);
    
    // 3秒后自动移除
    setTimeout(() => {
        toast.style.transition = 'opacity 0.3s';
        toast.style.opacity = '0';
        setTimeout(() => {
            if (toast.parentNode) {
                document.body.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

/**
 * 延迟执行（debounce）工具函数
 * 用于优化实时预览性能
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 导出函数供其他模块使用
window.copyCodeToClipboard = copyCodeToClipboard;
window.debounce = debounce;
