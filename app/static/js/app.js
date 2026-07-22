function getToken() {
  return localStorage.getItem('access_token') || '';
}

async function authFetch(url, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return fetch(url, { ...options, headers, credentials: 'same-origin' });
}

document.addEventListener('DOMContentLoaded', () => {
  const token = getToken();
  if (token && (window.location.pathname === '/login' || window.location.pathname === '/register')) {
    authFetch('/auth/me')
      .then((r) => { if (r.ok) window.location.href = '/dashboard'; })
      .catch(() => {});
  }
});
