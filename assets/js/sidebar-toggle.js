window.dash_clientside = window.dash_clientside || {};

window.dash_clientside.sidebar = {
    toggle: function(n_clicks, current_class) {
        if (!n_clicks) {
            try {
                const saved = sessionStorage.getItem('sidebar-collapsed');
                if (saved === 'true') {
                    return ['dvs-sidebar dvs-sidebar--collapsed', 'bi bi-chevron-bar-right'];
                }
            } catch (e) {
                console.warn('SessionStorage unavailable:', e);
            }
            return window.dash_clientside.no_update;
        }

        const collapsed = (current_class || '').includes('dvs-sidebar--collapsed');
        const newClass = collapsed ? 'dvs-sidebar' : 'dvs-sidebar dvs-sidebar--collapsed';
        const newIcon = collapsed ? 'bi bi-chevron-bar-left' : 'bi bi-chevron-bar-right';

        try {
            sessionStorage.setItem('sidebar-collapsed', (!collapsed).toString());
        } catch (e) {
            console.warn('SessionStorage unavailable:', e);
        }

        return [newClass, newIcon];
    }
};
