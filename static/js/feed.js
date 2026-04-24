/**
 * feed.js
 * Gestión del feed global: creación, edición, eliminación, likes y renderizado.
 */

let currentUser = null;

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = (now - date) / 1000;

    if (diff < 60) return 'Ahora';
    if (diff < 3600) return `${Math.floor(diff / 60)}m`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
    if (diff < 604800) return `${Math.floor(diff / 86400)}d`;
    return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' });
}

/* ─── Helpers ─── */
function renderBarkHeader(bark) {
    const avatarColor = bark.avatar_color || '#FF6B6B';
    const avatarEmoji = bark.avatar_emoji || '🐶';
    return `
        <span class="avatar avatar-sm" style="background:${avatarColor}">${avatarEmoji}</span>
        <div class="bark-header-info">
            <a href="/usuarios/${escapeHtml(bark.username)}/" class="bark-author">@${escapeHtml(bark.username)}</a>
            <span class="bark-date">${formatDate(bark.created_at)}</span>
        </div>
    `;
}

function renderBarkContent(bark) {
    return `<p class="bark-content">${escapeHtml(bark.content)}</p>`;
}

function renderBarkImage(bark) {
    if (!bark.image_url) return '';
    return `<div class="bark-image"><img src="${escapeHtml(bark.image_url)}" alt="Imagen del ladrido" loading="lazy"></div>`;
}

function renderBarkActions(bark, isOwner) {
    const likeIcon = bark.is_liked_by_me ? '❤️' : '🤍';
    const ownerActions = isOwner ? `
        <button class="edit-btn" data-id="${bark.id}">✏️ Editar</button>
        <button class="delete-btn" data-id="${bark.id}">🗑️ Eliminar</button>
    ` : '';
    const breakLine = isOwner ? '<div class="bark-actions-break"></div>' : '';
    return `
        ${ownerActions}
        ${breakLine}
        <button class="like-btn ${bark.is_liked_by_me ? 'liked' : ''}" data-id="${bark.id}">
            <span class="like-icon">${likeIcon}</span>
            <span class="like-count">${bark.likes_count || 0}</span>
        </button>
    `;
}

/* ─── Layout builders ─── */
function buildLayout0(bark, header, content, image, actions) {
    const hasImage = !!bark.image_url;
    return `
        <div class="bark-cinema-bg">${hasImage ? image : ''}</div>
        <div class="bark-cinema-overlay"></div>
        <div class="bark-header">${header}</div>
        ${content}
        <div class="bark-actions">${actions}</div>
    `;
}

function buildLayout1(bark, header, content, image, actions) {
    const hasImage = !!bark.image_url;
    return `
        <div class="bark-editorial-left">
            <div class="bark-header">${header}</div>
            ${content}
            <div class="bark-actions">${actions}</div>
        </div>
        ${hasImage ? image : ''}
    `;
}

function buildLayout2(bark, header, content, image, actions) {
    const hasImage = !!bark.image_url;
    const avatarColor = bark.avatar_color || '#FF6B6B';
    const avatarEmoji = bark.avatar_emoji || '🐶';
    const floatHeader = `
        <div class="bark-float-header">
            <span class="avatar avatar-sm" style="background:${avatarColor}">${avatarEmoji}</span>
            <div class="bark-header-info">
                <a href="/usuarios/${escapeHtml(bark.username)}/" class="bark-author">@${escapeHtml(bark.username)}</a>
                <span class="bark-date">${formatDate(bark.created_at)}</span>
            </div>
        </div>
    `;
    return `
        <div class="bark-mosaic-media">
            ${hasImage ? image : '<div class="bark-mosaic-placeholder"></div>'}
            ${floatHeader}
        </div>
        <div class="bark-mosaic-body">
            ${content}
            <div class="bark-actions">${actions}</div>
        </div>
    `;
}

function buildLayout3(bark, header, content, image, actions) {
    const hasImage = !!bark.image_url;
    return `
        ${hasImage ? `<div class="bark-asym-image"><img src="${escapeHtml(bark.image_url)}" alt="Imagen del ladrido" loading="lazy"></div>` : ''}
        <div class="bark-asym-body">
            <div class="bark-header">${header}</div>
            ${content}
            <div class="bark-actions">${actions}</div>
        </div>
    `;
}

function buildBarkHTML(bark) {
    const isOwner = currentUser && currentUser.id === bark.user_id;
    const layout = (bark.id || 0) % 4;
    const header = renderBarkHeader(bark);
    const content = renderBarkContent(bark);
    const image = renderBarkImage(bark);
    const actions = renderBarkActions(bark, isOwner);

    let innerHTML = '';
    switch (layout) {
        case 0: innerHTML = buildLayout0(bark, header, content, image, actions); break;
        case 1: innerHTML = buildLayout1(bark, header, content, image, actions); break;
        case 2: innerHTML = buildLayout2(bark, header, content, image, actions); break;
        case 3: innerHTML = buildLayout3(bark, header, content, image, actions); break;
        default: innerHTML = buildLayout0(bark, header, content, image, actions);
    }

    const noImageClass = !bark.image_url ? ' no-image' : '';
    return { innerHTML, className: `bark-card layout-${layout}${noImageClass}` };
}

function appendBark(container, bark) {
    const { innerHTML, className } = buildBarkHTML(bark);
    const card = document.createElement('div');
    card.className = className;
    card.dataset.id = bark.id;
    card.innerHTML = innerHTML;
    attachBarkEvents(card);
    container.appendChild(card);
}

function prependBark(container, bark) {
    const { innerHTML, className } = buildBarkHTML(bark);
    const card = document.createElement('div');
    card.className = className;
    card.dataset.id = bark.id;
    card.innerHTML = innerHTML;
    attachBarkEvents(card);
    container.insertBefore(card, container.firstChild);
}

function replaceBarkCard(card, bark) {
    const { innerHTML, className } = buildBarkHTML(bark);
    card.className = className;
    card.innerHTML = innerHTML;
    attachBarkEvents(card);
}

function removeBarkCard(card) {
    card.style.opacity = '0';
    card.style.transform = 'scale(0.96) translateY(8px)';
    card.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
    setTimeout(() => card.remove(), 250);
}

function attachBarkEvents(card) {
    const likeBtn = card.querySelector('.like-btn');
    if (likeBtn) {
        likeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (!currentUser) {
                showToast('Inicia sesión para dar like.');
                window.location.href = '/login/';
                return;
            }
            toggleLike(card, likeBtn);
        });
    }

    const editBtn = card.querySelector('.edit-btn');
    if (editBtn) {
        editBtn.addEventListener('click', function(e) {
            e.preventDefault();
            enableEditMode(card);
        });
    }

    const deleteBtn = card.querySelector('.delete-btn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function(e) {
            e.preventDefault();
            confirmDelete(card, deleteBtn.dataset.id);
        });
    }
}

function confirmDelete(card, barkId) {
    openModal({
        title: 'Eliminar ladrido',
        message: '¿Estás seguro de que quieres eliminar este ladrido? Esta acción no se puede deshacer.',
        confirmText: 'Eliminar',
        danger: true,
        onConfirm: async () => {
            try {
                await apiDelete(`/api/barkposts/${barkId}/delete/`);
                showToast('Ladrido eliminado.');
                removeBarkCard(card);
            } catch (err) {
                showToast(err.errors?.general || 'Error al eliminar el ladrido.');
            }
        }
    });
}

async function toggleLike(card, btn) {
    const barkId = btn.dataset.id;
    const icon = btn.querySelector('.like-icon');
    const count = btn.querySelector('.like-count');

    btn.disabled = true;
    try {
        const result = await apiPost(`/api/barkposts/${barkId}/like/`, {});
        icon.textContent = result.is_liked ? '❤️' : '🤍';
        count.textContent = result.likes_count;
        btn.classList.toggle('liked', result.is_liked);
        if (result.is_liked) {
            showToast('¡Te gusta este ladrido!');
        } else {
            showToast('Like quitado.');
        }
    } catch (err) {
        showToast(err.errors?.general || 'Error al dar like.');
    } finally {
        btn.disabled = false;
    }
}

function enableEditMode(card) {
    const barkId = card.dataset.id;
    const contentEl = card.querySelector('.bark-content');
    const imageEl = card.querySelector('img[alt="Imagen del ladrido"]');
    const currentContent = contentEl.textContent;
    const currentImageUrl = imageEl ? imageEl.src : null;

    // Strip creative layout classes and force full-width edit layout
    card.classList.forEach(cls => {
        if (cls.startsWith('layout-')) card.classList.remove(cls);
    });
    card.classList.add('layout-edit');

    card.innerHTML = `
        <div class="bark-edit-form">
            <div class="edit-header">
                <span class="edit-title">✏️ Editar ladrido</span>
            </div>
            <textarea class="edit-textarea" rows="4" maxlength="140" placeholder="¿Qué estás pensando?">${escapeHtml(currentContent)}</textarea>
            <div class="edit-meta-row">
                <div class="edit-file-wrapper">
                    <input type="file" id="edit-file-${barkId}" class="edit-file-input" accept="image/*">
                    <label for="edit-file-${barkId}" class="edit-file-label">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                        <span class="edit-file-text">Cambiar imagen</span>
                    </label>
                    <span class="edit-file-name"></span>
                </div>
                ${currentImageUrl ? `
                    <label class="edit-remove-img">
                        <input type="checkbox" class="edit-remove-check">
                        <span class="check-box"></span>
                        <span>Eliminar imagen actual</span>
                    </label>
                ` : ''}
            </div>
            <div class="edit-image-preview hidden">
                <img class="edit-preview-img" src="" alt="Vista previa">
                <button type="button" class="edit-remove-preview-btn remove-image-btn" title="Quitar imagen">&times;</button>
            </div>
            ${currentImageUrl ? `
                <div class="edit-current-image">
                    <span class="edit-current-label">Imagen actual</span>
                    <img src="${escapeHtml(currentImageUrl)}" alt="Imagen actual" class="edit-current-img">
                </div>
            ` : ''}
            <div class="edit-actions">
                <button class="btn btn-secondary edit-cancel-btn">Cancelar</button>
                <button class="btn btn-primary edit-save-btn">
                    <span class="btn-text">Guardar cambios</span>
                    <span class="spinner hidden"></span>
                </button>
            </div>
            <div class="edit-errors errors"></div>
        </div>
    `;

    const saveBtn = card.querySelector('.edit-save-btn');
    const cancelBtn = card.querySelector('.edit-cancel-btn');
    const textarea = card.querySelector('.edit-textarea');
    const fileInput = card.querySelector('.edit-file-input');
    const fileLabel = card.querySelector('.edit-file-label');
    const fileNameSpan = card.querySelector('.edit-file-name');
    const removeCheck = card.querySelector('.edit-remove-check');
    const errorsDiv = card.querySelector('.edit-errors');
    const editPreview = card.querySelector('.edit-image-preview');
    const editPreviewImg = card.querySelector('.edit-preview-img');
    const editRemovePreviewBtn = card.querySelector('.edit-remove-preview-btn');

    // Auto-focus textarea
    textarea.focus();
    textarea.setSelectionRange(textarea.value.length, textarea.value.length);

    // Preview on file select (edit mode)
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const file = fileInput.files[0];
            if (file && editPreview && editPreviewImg) {
                fileNameSpan.textContent = file.name;
                const reader = new FileReader();
                reader.onload = function(e) {
                    editPreviewImg.src = e.target.result;
                    editPreview.classList.remove('hidden');
                };
                reader.readAsDataURL(file);
            } else if (editPreview) {
                editPreview.classList.add('hidden');
                editPreviewImg.src = '';
                fileNameSpan.textContent = '';
            }
        });
    }

    if (editRemovePreviewBtn) {
        editRemovePreviewBtn.addEventListener('click', function() {
            if (editPreview) editPreview.classList.add('hidden');
            if (editPreviewImg) editPreviewImg.src = '';
            if (fileInput) fileInput.value = '';
            if (fileNameSpan) fileNameSpan.textContent = '';
        });
    }

    cancelBtn.addEventListener('click', function() {
        window.location.reload();
    });

    saveBtn.addEventListener('click', async function() {
        setLoading(saveBtn, true);
        errorsDiv.innerHTML = '';

        const formData = new FormData();
        const newContent = textarea.value.trim();
        if (newContent) {
            formData.append('content', newContent);
        }
        if (fileInput.files[0]) {
            formData.append('image', fileInput.files[0]);
        }
        if (removeCheck && removeCheck.checked) {
            formData.append('remove_image', 'true');
        }

        try {
            const result = await apiPatch(`/api/barkposts/${barkId}/update/`, formData);
            showToast('Ladrido actualizado correctamente.');
            replaceBarkCard(card, result.barkpost);
        } catch (err) {
            renderErrors(errorsDiv, err.errors || { general: err.message || 'Error al actualizar.' });
        } finally {
            setLoading(saveBtn, false);
        }
    });
}

function initBarkForm(formId, textareaId, counterId, submitId, errorsId, onSuccess) {
    const form = document.getElementById(formId);
    const textarea = document.getElementById(textareaId);
    const counter = document.getElementById(counterId);
    const btn = document.getElementById(submitId);
    const errorsDiv = document.getElementById(errorsId);
    const fileInput = form.querySelector('input[type="file"]');
    const fileNameSpan = form.querySelector('.file-name');
    const imagePreview = form.querySelector('#image-preview');
    const imagePreviewImg = form.querySelector('#image-preview-img');
    const removeImageBtn = form.querySelector('#remove-image-btn');

    function clearImagePreview() {
        if (imagePreview) imagePreview.classList.add('hidden');
        if (imagePreviewImg) imagePreviewImg.src = '';
        if (fileInput) fileInput.value = '';
        if (fileNameSpan) fileNameSpan.textContent = '';
    }

    if (!form) return;

    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const file = fileInput.files[0];
            fileNameSpan.textContent = file ? file.name : '';
            if (file && imagePreview && imagePreviewImg) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreviewImg.src = e.target.result;
                    imagePreview.classList.remove('hidden');
                };
                reader.readAsDataURL(file);
            } else {
                clearImagePreview();
            }
        });
    }

    if (removeImageBtn) {
        removeImageBtn.addEventListener('click', function() {
            clearImagePreview();
        });
    }

    textarea.addEventListener('input', function() {
        const len = textarea.value.length;
        counter.textContent = len + '/140';
        counter.classList.remove('warning', 'danger');
        if (len > 130) counter.classList.add('danger');
        else if (len > 110) counter.classList.add('warning');
    });

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        setLoading(btn, true);
        errorsDiv.innerHTML = '';

        const content = textarea.value.trim();
        if (!content) {
            renderErrors(errorsDiv, { content: 'El contenido no puede estar vacío.' });
            setLoading(btn, false);
            return;
        }
        if (content.length > 140) {
            renderErrors(errorsDiv, { content: 'Máximo 140 caracteres.' });
            setLoading(btn, false);
            return;
        }

        const formData = new FormData();
        formData.append('content', content);
        if (fileInput && fileInput.files[0]) {
            formData.append('image', fileInput.files[0]);
        }

        try {
            const result = await apiPost('/api/barkposts/create/', formData);
            textarea.value = '';
            clearImagePreview();
            counter.textContent = '0/140';
            counter.classList.remove('warning', 'danger');
            showToast('¡Ladrido publicado correctamente!');
            if (onSuccess) onSuccess(result.barkpost);
        } catch (err) {
            renderErrors(errorsDiv, err.errors || { general: err.message || 'Error al publicar.' });
        } finally {
            setLoading(btn, false);
        }
    });
}

/* ─── Skeleton Loading ─── */
function showSkeletons(container, count) {
    container.innerHTML = '';
    const template = document.getElementById('skeleton-card-template');
    for (let i = 0; i < count; i++) {
        const skel = template
            ? template.content.cloneNode(true).firstElementChild
            : document.createElement('div');
        if (!template) {
            skel.className = 'bark-card skeleton-card';
            skel.innerHTML = `
                <div class="skeleton-header">
                    <div class="skeleton-avatar skeleton"></div>
                    <div class="skeleton-line short skeleton"></div>
                </div>
                <div class="skeleton-line skeleton" style="height:0.6rem;margin-bottom:0.5rem;"></div>
                <div class="skeleton-line skeleton" style="height:0.6rem;width:70%;"></div>
            `;
        }
        container.appendChild(skel);
    }
}

function initFeed(feedContentId, feedLoadingId, feedEmptyId, feedPaginationId, loadMoreBtnId, fetchUrl) {
    const feedContent = document.getElementById(feedContentId);
    const feedLoading = document.getElementById(feedLoadingId);
    const feedEmpty = document.getElementById(feedEmptyId);
    const feedPagination = document.getElementById(feedPaginationId);
    const loadMoreBtn = document.getElementById(loadMoreBtnId);

    let nextUrl = null;
    let hasLoaded = false;

    function render(data) {
        if (data.results.length === 0 && !nextUrl) {
            feedContent.classList.add('hidden');
            feedEmpty.classList.remove('hidden');
            feedPagination.classList.add('hidden');
            return;
        }
        feedContent.classList.remove('hidden');
        feedEmpty.classList.add('hidden');
        data.results.forEach((bark, i) => {
            appendBark(feedContent, bark);
            // Stagger animation
            const card = feedContent.lastElementChild;
            card.style.animationDelay = `${i * 0.05}s`;
        });
        nextUrl = data.next;
        if (nextUrl) {
            feedPagination.classList.remove('hidden');
        } else {
            feedPagination.classList.add('hidden');
        }
    }

    async function load(url) {
        if (!hasLoaded) {
            showSkeletons(feedContent, 3);
            feedContent.classList.remove('hidden');
        }
        feedLoading.classList.remove('hidden');
        try {
            const data = await apiGet(url);
            feedLoading.classList.add('hidden');
            if (!hasLoaded) feedContent.innerHTML = '';
            render(data);
            hasLoaded = true;
        } catch (err) {
            feedLoading.classList.add('hidden');
            if (!hasLoaded) feedContent.innerHTML = '';
            feedLoading.textContent = 'Error al cargar.';
        }
    }

    loadMoreBtn.addEventListener('click', function() {
        if (nextUrl) {
            const url = new URL(nextUrl);
            load(url.pathname + url.search);
        }
    });

    return { load };
}

/* ─── FAB Mobile ─── */
function initFAB() {
    const fab = document.getElementById('fab-compose');
    const formSection = document.getElementById('bark-form-section');
    if (!fab || !formSection) return;

    // Show FAB only on mobile when form is not visible
    function checkFAB() {
        const isMobile = window.innerWidth <= 640;
        if (isMobile) {
            fab.classList.remove('hidden');
        } else {
            fab.classList.add('hidden');
        }
    }

    checkFAB();
    window.addEventListener('resize', checkFAB);

    fab.addEventListener('click', function() {
        formSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
        const textarea = document.getElementById('bark-content');
        if (textarea) textarea.focus();
    });
}

// === HOME PAGE ===
(function() {
    if (!document.getElementById('feed-content')) return;

    apiGet('/api/users/me/').then(data => {
        if (data.authenticated) {
            currentUser = data.user;
        }
    }).catch(() => {}).finally(() => {
        const feed = initFeed('feed-content', 'feed-loading', 'feed-empty', 'feed-pagination', 'feed-load-more-btn', '/api/barkposts/');
        feed.load('/api/barkposts/');
    });

    initAuthNav();
    initBarkForm('bark-form', 'bark-content', 'char-count', 'bark-submit-btn', 'bark-errors', function(bark) {
        const feedContent = document.getElementById('feed-content');
        const feedEmpty = document.getElementById('feed-empty');
        prependBark(feedContent, bark);
        feedEmpty.classList.add('hidden');
    });

    initFAB();
})();
