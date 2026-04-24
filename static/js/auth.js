/**
 * auth.js
 * Gestión de autenticación: login, registro, logout y navegación condicional.
 */

function openModal({ title, message, confirmText, onConfirm, danger = false }) {
    const modal = document.getElementById('confirm-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalMessage = document.getElementById('modal-message');
    const confirmBtn = document.getElementById('modal-confirm');
    const cancelBtn = document.getElementById('modal-cancel');
    const confirmTextSpan = confirmBtn.querySelector('.btn-text');

    modalTitle.textContent = title;
    modalMessage.textContent = message;
    confirmTextSpan.textContent = confirmText;
    confirmBtn.className = danger ? 'btn btn-danger' : 'btn btn-primary';

    modal.classList.remove('hidden');

    const close = () => {
        modal.classList.add('hidden');
        confirmBtn.onclick = null;
        cancelBtn.onclick = null;
        modal.onclick = null;
    };

    confirmBtn.onclick = async () => {
        setLoading(confirmBtn, true);
        try {
            await onConfirm();
        } finally {
            setLoading(confirmBtn, false);
            close();
        }
    };

    cancelBtn.onclick = close;
    modal.querySelector('.modal-overlay').onclick = close;
}

function initAuthNav() {
    const navLinks = document.getElementById('nav-links');
    if (!navLinks) return;

    apiGet('/api/users/me/')
        .then(data => {
            if (data.authenticated) {
                const user = data.user;
                const avatarStyle = user.avatar_color ? `style="background:${user.avatar_color}"` : '';
                navLinks.innerHTML = `
                    <button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()" title="Cambiar tema">☀️</button>
                    <a href="/usuarios/${user.username}/" class="nav-user">
                        <span class="avatar avatar-sm" ${avatarStyle}>${user.avatar_emoji || '🐶'}</span>
                        <span>${user.username}</span>
                    </a>
                    <button id="logout-btn">Salir</button>
                `;
                document.getElementById('logout-btn').addEventListener('click', function() {
                    openModal({
                        title: 'Cerrar sesión',
                        message: '¿Seguro que quieres salir de tu cuenta?',
                        confirmText: 'Salir',
                        danger: true,
                        onConfirm: async () => {
                            try {
                                await apiPost('/api/users/logout/');
                                showToast('Sesión cerrada.');
                                window.location.href = '/';
                            } catch (err) {
                                showToast('Error al cerrar sesión.');
                            }
                        }
                    });
                });
                // Update theme toggle icon
                const theme = window.getTheme ? window.getTheme() : 'dark';
                const toggle = document.getElementById('theme-toggle');
                if (toggle) {
                    toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
                    toggle.title = theme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro';
                }
            } else {
                const theme = window.getTheme ? window.getTheme() : 'dark';
                navLinks.innerHTML = `
                    <button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()" title="Cambiar tema">${theme === 'dark' ? '☀️' : '🌙'}</button>
                    <a href="/login/">Entrar</a>
                    <a href="/registro/">Registro</a>
                `;
            }
        })
        .catch(() => {
            const theme = window.getTheme ? window.getTheme() : 'dark';
            navLinks.innerHTML = `
                <button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()" title="Cambiar tema">${theme === 'dark' ? '☀️' : '🌙'}</button>
                <a href="/login/">Entrar</a>
                <a href="/registro/">Registro</a>
            `;
        });
}
