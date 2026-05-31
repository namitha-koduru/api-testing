/**
 * EventNet – User Panel JS
 * Handles: toast notifications, form helpers, table search, sidebar toggle
 */

// ─── Toast Notification System ─────────────────────────────────────
const Toast = (() => {
  let container = null;

  function getContainer() {
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999;display:flex;flex-direction:column;gap:10px;';
      document.body.appendChild(container);
    }
    return container;
  }

  function show(message, type = 'success', duration = 4000) {
    const el = document.createElement('div');
    const colors = {
      success: { bg: '#166534', color: '#fff' },
      error:   { bg: '#991b1b', color: '#fff' },
      warning: { bg: '#92400e', color: '#fff' },
      info:    { bg: '#1e40af', color: '#fff' },
    };
    const c = colors[type] || colors.info;
    el.style.cssText = `
      background:${c.bg};color:${c.color};
      padding:13px 18px;border-radius:10px;font-size:14px;font-weight:500;
      min-width:240px;max-width:360px;box-shadow:0 4px 20px rgba(0,0,0,.2);
      animation:toastIn .25s ease;cursor:pointer;line-height:1.4;
    `;
    el.textContent = message;
    el.addEventListener('click', () => el.remove());

    if (!document.getElementById('toast-style')) {
      const s = document.createElement('style');
      s.id = 'toast-style';
      s.textContent = '@keyframes toastIn{from{transform:translateX(120%);opacity:0}to{transform:translateX(0);opacity:1}}';
      document.head.appendChild(s);
    }

    getContainer().appendChild(el);
    setTimeout(() => { if (el.parentElement) el.remove(); }, duration);
  }

  return { show, success: (m) => show(m,'success'), error: (m) => show(m,'error'), info: (m) => show(m,'info') };
})();

// ─── API Helper ────────────────────────────────────────────────────
async function apiPost(url, body = {}) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    credentials: 'include',
  });
  if (!res.ok && res.status === 401) {
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }
  return res.json();
}

async function apiGet(url) {
  const res = await fetch(url, { credentials: 'include' });
  return res.json();
}

// ─── Sidebar Toggle ────────────────────────────────────────────────
function toggleSidebar() {
  const s = document.getElementById('sidebar');
  if (s) s.classList.toggle('open');
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', (e) => {
  const sidebar = document.getElementById('sidebar');
  const toggle = document.querySelector('.sidebar-toggle');
  if (sidebar && sidebar.classList.contains('open') && toggle &&
      !sidebar.contains(e.target) && !toggle.contains(e.target)) {
    sidebar.classList.remove('open');
  }
});

// ─── Auto-dismiss flash alerts ─────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert').forEach((el) => {
    setTimeout(() => {
      el.style.transition = 'opacity .4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    }, 5000);
  });

  // Confirm dialogs for delete forms
  document.querySelectorAll('form[data-confirm]').forEach((form) => {
    form.addEventListener('submit', (e) => {
      const msg = form.dataset.confirm || 'Are you sure?';
      if (!confirm(msg)) e.preventDefault();
    });
  });
});

// ─── Table client-side search ──────────────────────────────────────
function initTableSearch(inputId, tableId) {
  const input = document.getElementById(inputId);
  const table = document.getElementById(tableId);
  if (!input || !table) return;

  input.addEventListener('input', () => {
    const q = input.value.toLowerCase();
    table.querySelectorAll('tbody tr').forEach((row) => {
      row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
  });
}

// ─── Expose globals ────────────────────────────────────────────────
window.Toast = Toast;
window.apiPost = apiPost;
window.apiGet = apiGet;
window.toggleSidebar = toggleSidebar;
window.initTableSearch = initTableSearch;
