/**
 * theme.js
 * Gestión de tema oscuro/claro con persistencia en localStorage.
 * Modo oscuro por defecto.
 */

(function() {
    const html = document.documentElement;
    const STORAGE_KEY = 'perretes-theme';

    function getTheme() {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) return saved;
        // Dark mode by default
        return 'dark';
    }

    function applyTheme(theme) {
        html.setAttribute('data-theme', theme);
        updateToggleIcon(theme);
    }

    function updateToggleIcon(theme) {
        const toggle = document.getElementById('theme-toggle');
        if (!toggle) return;
        toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
        toggle.title = theme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro';
    }

    function toggleTheme() {
        const current = html.getAttribute('data-theme') || 'dark';
        const next = current === 'dark' ? 'light' : 'dark';
        localStorage.setItem(STORAGE_KEY, next);
        applyTheme(next);
    }

    // Init
    const theme = getTheme();
    applyTheme(theme);

    // Expose globally
    window.toggleTheme = toggleTheme;
    window.getTheme = getTheme;
})();
