// 客户端函数：复制到剪贴板

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        copyToClipboard: function(n_clicks, code) {
            if (n_clicks && code) {
                navigator.clipboard.writeText(code).then(function() {
                    console.log('代码已复制到剪贴板');
                }).catch(function(err) {
                    console.error('复制失败:', err);
                });
            }
            return window.dash_clientside.no_update;
        }
    }
});
