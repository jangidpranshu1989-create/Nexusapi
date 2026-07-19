if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch(err => {
            console.error('ServiceWorker registration failed: ', err);
        });
    });
}

const TOKEN_KEY = 'nexusapi_jwt';
function getToken() { return localStorage.getItem(TOKEN_KEY); }
function setToken(token) { localStorage.setItem(TOKEN_KEY, token); }
function clearToken() { localStorage.removeItem(TOKEN_KEY); }
function clearRole() { localStorage.removeItem(ROLE_KEY); }
function isLoggedIn() { return !!getToken(); }

function logout() {
    clearToken();
    clearRole();
    window.location.href = '/';
}

function updateNavUI() {
    const guest = document.getElementById('nav-guest');
    const auth = document.getElementById('nav-auth');
    if (!guest || !auth) return;

    if (isLoggedIn()) {
        guest.classList.add('hidden');
        guest.classList.remove('flex');
        auth.classList.remove('hidden');
        auth.classList.add('flex');
    } else {
        auth.classList.add('hidden');
        auth.classList.remove('flex');
        guest.classList.remove('hidden');
        guest.classList.add('flex');
    }
}

document.addEventListener('DOMContentLoaded', updateNavUI);

function showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentElement) toast.remove();
    }, 3000);
}

async function apiFetch(path, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(path, { ...options, headers });

    let data;
    try {
        data = await response.json();
    } catch (e) {
        data = null;
    }

    if (!response.ok) {
        const errorMsg = (data && data.detail) || 'An unexpected error occurred';
        throw new Error(errorMsg);
    }

    return data;
}


// Role storage - saved at login/register time so pages can check without extra API calls
const ROLE_KEY = 'nexusapi_role';
function setRole(role) { localStorage.setItem(ROLE_KEY, role); }
function getRole() { return localStorage.getItem(ROLE_KEY); }
function isDeveloperOrAdmin() {
    const role = getRole();
    return role === 'developer' || role === 'admin';
}

// Floating "Submit System" button - shown only to verified developers/admins
function renderFloatingSubmitButton() {
    if (!isLoggedIn() || !isDeveloperOrAdmin()) return;

    const btn = document.createElement('a');
    btn.href = '/dashboard';
    btn.className = 'fixed bottom-6 right-6 bg-brand hover:bg-brand/90 text-white rounded-full shadow-lg shadow-brand/30 px-5 py-3 flex items-center gap-2 font-medium transition z-50';
    btn.innerHTML = '<span style="font-size:1.2em;">+</span> Submit System';
    document.body.appendChild(btn);
}

document.addEventListener('DOMContentLoaded', renderFloatingSubmitButton);
