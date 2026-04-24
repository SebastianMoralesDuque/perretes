/**
 * search.js
 * Búsqueda en tiempo real con autocomplete (usuarios y ladridos).
 */

(function() {
    const searchInput = document.getElementById('global-search');
    const dropdown = document.getElementById('search-dropdown');
    const usersSection = document.getElementById('search-users-section');
    const usersList = document.getElementById('search-users-list');
    const postsSection = document.getElementById('search-posts-section');
    const postsList = document.getElementById('search-posts-list');
    const emptyMsg = document.getElementById('search-empty');

    if (!searchInput) return;

    let debounceTimer = null;

    function debounce(fn, ms) {
        return function(...args) {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => fn.apply(this, args), ms);
        };
    }

    function hideDropdown() {
        dropdown.classList.add('hidden');
    }

    function showDropdown() {
        dropdown.classList.remove('hidden');
    }

    function clearResults() {
        usersList.innerHTML = '';
        postsList.innerHTML = '';
        usersSection.classList.add('hidden');
        postsSection.classList.add('hidden');
        emptyMsg.classList.add('hidden');
    }

    function renderUsers(users) {
        if (!users || users.length === 0) return;
        usersSection.classList.remove('hidden');
        users.forEach(u => {
            const li = document.createElement('li');
            li.className = 'search-item';
            li.innerHTML = `
                <span class="search-item-icon">🐶</span>
                <span class="search-item-text">@${escapeHtml(u.username)}</span>
            `;
            li.addEventListener('click', () => {
                window.location.href = `/usuarios/${encodeURIComponent(u.username)}/`;
            });
            usersList.appendChild(li);
        });
    }

    function renderPosts(posts) {
        if (!posts || posts.length === 0) return;
        postsSection.classList.remove('hidden');
        posts.forEach(p => {
            const li = document.createElement('li');
            li.className = 'search-item';
            const preview = p.content.length > 60 ? p.content.slice(0, 60) + '...' : p.content;
            li.innerHTML = `
                <span class="search-item-icon">💬</span>
                <span class="search-item-text">${escapeHtml(preview)}</span>
                <span class="search-item-meta">@${escapeHtml(p.username)}</span>
            `;
            li.addEventListener('click', () => {
                window.location.href = `/usuarios/${encodeURIComponent(p.username)}/`;
            });
            postsList.appendChild(li);
        });
    }

    async function doSearch(query) {
        clearResults();
        if (!query || query.length < 2) {
            hideDropdown();
            return;
        }

        try {
            const data = await apiGet(`/api/barkposts/search/?q=${encodeURIComponent(query)}`);
            renderUsers(data.users);
            renderPosts(data.posts);

            const hasResults = (data.users && data.users.length > 0) || (data.posts && data.posts.length > 0);
            if (!hasResults) {
                emptyMsg.classList.remove('hidden');
            }
            showDropdown();
        } catch (err) {
            hideDropdown();
        }
    }

    const debouncedSearch = debounce(doSearch, 250);

    searchInput.addEventListener('input', function() {
        const query = searchInput.value.trim();
        if (query.length < 2) {
            clearResults();
            hideDropdown();
            return;
        }
        debouncedSearch(query);
    });

    // Cerrar dropdown al hacer click fuera
    document.addEventListener('click', function(e) {
        const isInside = searchInput.contains(e.target) || dropdown.contains(e.target);
        if (!isInside) {
            hideDropdown();
        }
    });

    // Abrir dropdown de nuevo al enfocar si hay texto
    searchInput.addEventListener('focus', function() {
        const query = searchInput.value.trim();
        if (query.length >= 2) {
            doSearch(query);
        }
    });

    // Keyboard shortcut: / to focus search
    document.addEventListener('keydown', function(e) {
        if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
            e.preventDefault();
            searchInput.focus();
        }
        if (e.key === 'Escape') {
            hideDropdown();
            searchInput.blur();
        }
    });
})();

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
