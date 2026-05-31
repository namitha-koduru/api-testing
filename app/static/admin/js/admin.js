/**
 * EventNet – Admin Panel JS
 * Completely isolated from user panel JS.
 */

// ─── Sidebar ───────────────────────────────────────────────────────
function toggleAdminSidebar() {
  const s = document.getElementById('adminSidebar');
  if (s) s.classList.toggle('open');
}

document.addEventListener('click', (e) => {
  const sidebar = document.getElementById('adminSidebar');
  const toggle = document.querySelector('.admin-sidebar-toggle');
  if (sidebar && sidebar.classList.contains('open') && toggle &&
      !sidebar.contains(e.target) && !toggle.contains(e.target)) {
    sidebar.classList.remove('open');
  }
});

// ─── Auto-dismiss alerts ───────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.admin-alert').forEach((el) => {
    setTimeout(() => {
      el.style.transition = 'opacity .4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    }, 6000);
  });

  // Confirm dialogs
  document.querySelectorAll('form[data-confirm]').forEach((form) => {
    form.addEventListener('submit', (e) => {
      if (!confirm(form.dataset.confirm || 'Are you sure? This cannot be undone.')) {
        e.preventDefault();
      }
    });
  });

  // Table search
  const searchInput = document.getElementById('adminTableSearch');
  const searchTable = document.getElementById('adminTable');
  if (searchInput && searchTable) {
    searchInput.addEventListener('input', () => {
      const q = searchInput.value.toLowerCase();
      searchTable.querySelectorAll('tbody tr').forEach((row) => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }
});

// ─── Price toggle helper (used in forms) ──────────────────────────
function syncPriceToggle(priceInput, isFreeCheckbox) {
  const p = document.getElementById(priceInput);
  const cb = document.getElementById(isFreeCheckbox);
  if (!p || !cb) return;
  function update() {
    p.disabled = cb.checked;
    if (cb.checked) p.value = '0';
  }
  cb.addEventListener('change', update);
  update();
}

window.toggleAdminSidebar = toggleAdminSidebar;
window.syncPriceToggle = syncPriceToggle;
