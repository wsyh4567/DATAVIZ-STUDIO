/**
 * 字段拖拽功能
 * 
 * 实现字段从字段面板拖拽到图表配置区域
 */

// 拖拽开始
document.addEventListener('dragstart', function(e) {
    const target = e.target.closest('[draggable="true"]');
    if (!target) return;
    
    const fieldName = target.dataset.field;
    const fieldCategory = target.dataset.category;
    
    if (fieldName && fieldCategory) {
        e.dataTransfer.effectAllowed = 'copy';
        e.dataTransfer.setData('text/plain', JSON.stringify({
            field: fieldName,
            category: fieldCategory
        }));
        
        target.style.opacity = '0.5';
    }
});

// 拖拽结束
document.addEventListener('dragend', function(e) {
    const target = e.target.closest('[draggable="true"]');
    if (target) {
        target.style.opacity = '1';
    }
});

// 拖拽经过放置区
document.addEventListener('dragover', function(e) {
    const dropZone = e.target.closest('.drop-zone');
    if (dropZone) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
        dropZone.classList.add('drop-zone-hover');
    }
});

// 离开放置区
document.addEventListener('dragleave', function(e) {
    const dropZone = e.target.closest('.drop-zone');
    if (dropZone && !dropZone.contains(e.relatedTarget)) {
        dropZone.classList.remove('drop-zone-hover');
    }
});

// 放置
document.addEventListener('drop', function(e) {
    const dropZone = e.target.closest('.drop-zone');
    if (!dropZone) return;
    
    e.preventDefault();
    dropZone.classList.remove('drop-zone-hover');
    
    try {
        const data = JSON.parse(e.dataTransfer.getData('text/plain'));
        const zoneId = dropZone.dataset.zone;
        
        if (data.field && zoneId) {
            // 触发 Dash 回调
            const event = new CustomEvent('fieldDropped', {
                detail: {
                    field: data.field,
                    zone: zoneId,
                    category: data.category
                }
            });
            document.dispatchEvent(event);
            
            // 更新 UI
            updateDropZone(dropZone, data.field);
        }
    } catch (err) {
        console.error('Drop error:', err);
    }
});

// 更新放置区 UI
function updateDropZone(dropZone, fieldName) {
    dropZone.classList.remove('drop-zone-empty');
    dropZone.classList.add('drop-zone-filled');
    
    const zoneId = dropZone.dataset.zone;
    
    dropZone.innerHTML = `
        <div class="d-flex align-items-center justify-content-between">
            <span>${fieldName}</span>
            <i class="bi bi-x-circle" 
               style="cursor: pointer; color: #EF4444;"
               onclick="removeField('${zoneId}')"></i>
        </div>
    `;
}

// 移除字段
function removeField(zoneId) {
    const dropZone = document.querySelector(`[data-zone="${zoneId}"]`);
    if (dropZone) {
        dropZone.classList.remove('drop-zone-filled');
        dropZone.classList.add('drop-zone-empty');
        dropZone.innerHTML = '<span class="text-muted small">拖拽字段到此处</span>';
        
        // 触发 Dash 回调
        const event = new CustomEvent('fieldRemoved', {
            detail: { zone: zoneId }
        });
        document.dispatchEvent(event);
    }
}

// 监听自定义事件并更新 Dash Store
document.addEventListener('fieldDropped', function(e) {
    const { field, zone, category } = e.detail;
    
    // 获取当前字段映射
    const storeElement = document.getElementById('chart-fields-store');
    if (storeElement) {
        const currentData = JSON.parse(storeElement.dataset.data || '{}');
        currentData[zone] = field;
        
        // 更新 store（触发 Dash 回调）
        if (window.dash_clientside) {
            window.dash_clientside.set_props('chart-fields-store', { data: currentData });
        }
    }
});

document.addEventListener('fieldRemoved', function(e) {
    const { zone } = e.detail;
    
    // 获取当前字段映射
    const storeElement = document.getElementById('chart-fields-store');
    if (storeElement) {
        const currentData = JSON.parse(storeElement.dataset.data || '{}');
        delete currentData[zone];
        
        // 更新 store（触发 Dash 回调）
        if (window.dash_clientside) {
            window.dash_clientside.set_props('chart-fields-store', { data: currentData });
        }
    }
});
