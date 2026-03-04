window.dash_clientside = window.dash_clientside || {};

window.dash_clientside.theme = {
    toggle: function(n_clicks) {
        const root = document.getElementById('app-root');
        if (!root) return window.dash_clientside.no_update;
        const current = root.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        root.setAttribute('data-theme', next);
        return next;
    }
};
