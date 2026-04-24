/**
 * api.js
 * Utilidades base para comunicación AJAX con el backend Django.
 * Maneja CSRF tokens automáticamente desde el meta tag o cookies.
 * Soporta tanto JSON como FormData (para subida de archivos).
 */

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.content;
    return getCookie('csrftoken');
}

async function apiFetch(url, options = {}) {
    const defaultHeaders = {
        'X-Requested-With': 'XMLHttpRequest',
    };

    const isFormData = options.body instanceof FormData;
    if (!isFormData) {
        defaultHeaders['Content-Type'] = 'application/json';
    }

    const csrfToken = getCsrfToken();
    if (csrfToken && (!options.method || options.method.toUpperCase() !== 'GET')) {
        defaultHeaders['X-CSRFToken'] = csrfToken;
    }

    const response = await fetch(url, {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
        credentials: 'same-origin',
    });

    let data = null;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
        data = await response.json();
    }

    if (!response.ok) {
        const error = new Error(data?.message || `Error HTTP ${response.status}`);
        error.status = response.status;
        error.errors = data?.errors || data || {};
        throw error;
    }

    return data;
}

function apiGet(url) {
    return apiFetch(url, { method: 'GET' });
}

function apiPost(url, body) {
    const isFormData = body instanceof FormData;
    return apiFetch(url, {
        method: 'POST',
        body: isFormData ? body : JSON.stringify(body),
    });
}

function apiPatch(url, body) {
    const isFormData = body instanceof FormData;
    return apiFetch(url, {
        method: 'PATCH',
        body: isFormData ? body : JSON.stringify(body),
    });
}

function apiDelete(url) {
    return apiFetch(url, { method: 'DELETE' });
}

/* ─── Toast with progress bar ─── */
let toastTimeout = null;

function showToast(message) {
    const toast = document.getElementById('toast');
    const msg = document.getElementById('toast-message');
    if (!toast || !msg) return;

    // Clear previous
    if (toastTimeout) {
        clearTimeout(toastTimeout);
        toastTimeout = null;
    }

    msg.textContent = message;
    toast.classList.remove('hidden');
    toast.classList.add('show');

    // Reset progress bar animation
    const oldProgress = toast.querySelector('.toast-progress');
    if (oldProgress) {
        oldProgress.remove();
    }
    const progress = document.createElement('div');
    progress.className = 'toast-progress';
    toast.appendChild(progress);

    toastTimeout = setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.classList.add('hidden');
            if (progress.parentNode) progress.remove();
        }, 300);
    }, 3000);
}

function setLoading(btn, isLoading) {
    btn.disabled = isLoading;
    const text = btn.querySelector('.btn-text');
    const spinner = btn.querySelector('.spinner');
    if (text) text.classList.toggle('hidden', isLoading);
    if (spinner) spinner.classList.toggle('hidden', !isLoading);
}

function renderErrors(container, errors) {
    container.innerHTML = '';
    const ul = document.createElement('ul');
    if (typeof errors === 'string') {
        const li = document.createElement('li');
        li.textContent = errors;
        ul.appendChild(li);
    } else {
        Object.entries(errors).forEach(([field, messages]) => {
            if (Array.isArray(messages)) {
                messages.forEach(msg => {
                    const li = document.createElement('li');
                    li.textContent = `${field}: ${msg}`;
                    ul.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.textContent = `${field}: ${messages}`;
                ul.appendChild(li);
            }
        });
    }
    container.appendChild(ul);
}
