/* ============================================================
   GESTIÓN RH — app.js  |  Shared application logic
   Role management · Navigation · Modals · Toasts · Utils
   ============================================================ */
'use strict';

/* ── Role Config ────────────────────────────────────────────── */
const ROLES = {
  jefe:     { label: 'Jefe de Sede',         avatar: 'JE' },
  regente:  { label: 'Regente',              avatar: 'RE' },
  auxiliar: { label: 'Auxiliar de Regente',  avatar: 'AR' },
  operario: { label: 'Operario',             avatar: 'OP' },
};

/* Demo users per role (from mock data) */
const DEMO_USER = {
  jefe:     { nombre: 'Carlos A. Rodríguez', sedeId: 1 },
  regente:  { nombre: 'Laura P. Sánchez',    sedeId: 1 },
  auxiliar: { nombre: 'Andrés F. Torres',    sedeId: 1 },
  operario: { nombre: 'Diana M. Vargas',     sedeId: 1 },
};

/* Permissions */
const PERMS = {
  jefe:     ['dashboard','empleados','empleados.crear','empleados.editar','empleados.desactivar',
             'empleados.crearUsuario','eventos','eventos.crear','eventos.anular',
             'horarios','horarios.gestionar','horasExtras','horasExtras.crear',
             'horasExtras.aprobar','catalogos','otrasSedes'],
  regente:  ['empleados','empleados.crear','empleados.editar',
             'eventos','eventos.crear','eventos.anular',
             'horarios','horarios.gestionar','horasExtras','horasExtras.crear'],
  auxiliar: ['empleados','empleados.crear','empleados.editar',
             'eventos','eventos.crear','eventos.anular',
             'horarios','horarios.gestionar','horasExtras','horasExtras.crear'],
  operario: ['perfilPropio','horasExtras.verPropias'],
};

function getRole()    { return localStorage.getItem('gh_role') || 'jefe'; }
function setRole(rol) { localStorage.setItem('gh_role', rol); }
function can(perm)    { return (PERMS[getRole()] || []).includes(perm); }

/* ── Boot (runs on DOMContentLoaded) ───────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  buildSidebar();
  applyRole(getRole());
  initRoleSwitcher();
  initNav();
  initModals();
  initTabs();
});

/* ── Role ───────────────────────────────────────────────────── */
function applyRole(rol) {
  setRole(rol);

  /* Update UI: avatar, name, role label */
  const user = DEMO_USER[rol] || DEMO_USER.jefe;
  const meta = ROLES[rol] || ROLES.jefe;
  document.querySelectorAll('[data-user-name]').forEach(el => el.textContent = user.nombre);
  document.querySelectorAll('[data-user-role]').forEach(el => el.textContent = meta.label);
  document.querySelectorAll('[data-user-avatar]').forEach(el => el.textContent = meta.avatar);

  /* Show / hide by role */
  document.querySelectorAll('[data-roles]').forEach(el => {
    const allowed = el.getAttribute('data-roles').split(',').map(r => r.trim());
    el.hidden = !(allowed.includes('all') || allowed.includes(rol));
  });

  /* Disable actions by permission */
  document.querySelectorAll('[data-perm]').forEach(el => {
    const perm = el.getAttribute('data-perm');
    const disabled = !can(perm);
    if (el.tagName === 'BUTTON' || el.tagName === 'A') {
      el.toggleAttribute('disabled', disabled);
      if (disabled) el.setAttribute('aria-disabled', 'true');
      else el.removeAttribute('aria-disabled');
    } else {
      el.hidden = disabled;
    }
  });

  /* Sync the demo select if present */
  const sel = document.getElementById('role-switcher');
  if (sel && sel.value !== rol) sel.value = rol;
}

function initRoleSwitcher() {
  const sel = document.getElementById('role-switcher');
  if (!sel) return;
  sel.value = getRole();
  sel.addEventListener('change', () => applyRole(sel.value));
}

/* ── Navigation ─────────────────────────────────────────────── */
function initNav() {
  const current = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href') || '';
    if (href === current || href.endsWith('/' + current)) {
      link.classList.add('is-active');
      link.setAttribute('aria-current', 'page');
    }
  });

  /* Hide nav items by role */
  document.querySelectorAll('.nav-link[data-roles]').forEach(link => {
    const roles = link.getAttribute('data-roles').split(',').map(r => r.trim());
    link.hidden = !(roles.includes('all') || roles.includes(getRole()));
  });
}

/* ── Modals ─────────────────────────────────────────────────── */
function initModals() {
  /* Open via data-modal-open="id" */
  document.querySelectorAll('[data-modal-open]').forEach(btn => {
    btn.addEventListener('click', () => openModal(btn.getAttribute('data-modal-open')));
  });

  /* Close via data-modal-close or clicking the overlay */
  document.querySelectorAll('[data-modal-close]').forEach(btn => {
    btn.addEventListener('click', () => {
      const overlay = btn.closest('.modal-overlay');
      if (overlay) closeModal(overlay.id);
    });
  });

  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', e => {
      if (e.target === overlay) closeModal(overlay.id);
    });
  });

  /* ESC key */
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      const open = document.querySelector('.modal-overlay:not([hidden])');
      if (open) closeModal(open.id);
    }
  });
}

function openModal(id) {
  const overlay = document.getElementById(id);
  if (!overlay) return;
  overlay.hidden = false;
  overlay.removeAttribute('aria-hidden');
  const firstFocusable = overlay.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
  if (firstFocusable) firstFocusable.focus();
}

function closeModal(id) {
  const overlay = document.getElementById(id);
  if (!overlay) return;
  overlay.hidden = true;
  overlay.setAttribute('aria-hidden', 'true');
}

/* ── Tabs ───────────────────────────────────────────────────── */
function initTabs() {
  document.querySelectorAll('.tabs').forEach(tabList => {
    const buttons = tabList.querySelectorAll('.tab-btn');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.getAttribute('data-tab');
        if (!target) return;

        /* Deactivate all in this tabs group */
        buttons.forEach(b => {
          b.classList.remove('is-active');
          b.setAttribute('aria-selected', 'false');
        });
        btn.classList.add('is-active');
        btn.setAttribute('aria-selected', 'true');

        /* Show target panel */
        const container = btn.closest('[data-tabs-container]') || document;
        container.querySelectorAll('.tab-panel').forEach(p => {
          p.classList.toggle('is-active', p.id === target);
        });
      });

      /* Keyboard navigation */
      btn.addEventListener('keydown', e => {
        const btns = Array.from(buttons);
        const idx = btns.indexOf(btn);
        if (e.key === 'ArrowRight' && idx < btns.length - 1) btns[idx + 1].focus();
        if (e.key === 'ArrowLeft'  && idx > 0)               btns[idx - 1].focus();
      });
    });
  });
}

/* ── Toast ──────────────────────────────────────────────────── */
function showToast(message, type = 'default', duration = 3500) {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    container.setAttribute('aria-live', 'polite');
    container.setAttribute('aria-atomic', 'false');
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast${type !== 'default' ? ` toast--${type}` : ''}`;
  toast.setAttribute('role', 'status');
  toast.textContent = message;

  container.appendChild(toast);
  setTimeout(() => toast.remove(), duration);
}

/* ── Format Helpers ─────────────────────────────────────────── */
const fmt = {
  date(str) {
    if (!str) return '—';
    return new Intl.DateTimeFormat('es-CO', { year: 'numeric', month: 'short', day: 'numeric' }).format(new Date(str + 'T12:00:00'));
  },
  dateRange(start, end) {
    if (!start) return '—';
    return `${fmt.date(start)}${end ? ' → ' + fmt.date(end) : ''}`;
  },
  number(n) {
    return new Intl.NumberFormat('es-CO').format(n);
  },
};

/* ── Badge Helpers ──────────────────────────────────────────── */
function badgeEstado(estado) {
  const map = {
    activo:     '<span class="badge badge--activo"><span class="badge-dot"></span>Activo</span>',
    inactivo:   '<span class="badge badge--inactivo"><span class="badge-dot"></span>Inactivo</span>',
    pendiente:  '<span class="badge badge--pendiente"><span class="badge-dot"></span>Pendiente</span>',
    aprobado:   '<span class="badge badge--aprobado"><span class="badge-dot"></span>Aprobado</span>',
    rechazado:  '<span class="badge badge--rechazado"><span class="badge-dot"></span>Rechazado</span>',
    finalizado: '<span class="badge badge--finalizado"><span class="badge-dot"></span>Finalizado</span>',
    anulado:    '<span class="badge badge--anulado"><span class="badge-dot"></span>Anulado</span>',
  };
  return map[estado] || `<span class="badge">${estado}</span>`;
}

function badgeTipo(tipo) {
  const map = {
    directo:     '<span class="badge badge--directo">Directo</span>',
    temporal:    '<span class="badge badge--temporal">Temporal</span>',
    vacaciones:  '<span class="badge badge--vacaciones">Vacaciones</span>',
    incapacidad: '<span class="badge badge--incapacidad">Incapacidad</span>',
    permiso:     '<span class="badge badge--permiso">Permiso</span>',
  };
  return map[tipo] || `<span class="badge">${tipo}</span>`;
}

function badgeRol(rol) {
  const labels = { jefe: 'Jefe', regente: 'Regente', auxiliar: 'Auxiliar', operario: 'Operario' };
  return `<span class="badge badge--${rol}">${labels[rol] || rol}</span>`;
}

/* ── Vacation Balance ───────────────────────────────────────── */
function calcVacBalance(empleado) {
  if (!empleado) return { acumulados: 0, tomados: 0, disponibles: 0 };
  const ingreso = new Date(empleado.fechaIngreso + 'T12:00:00');
  const hoy = new Date();
  const meses = (hoy.getFullYear() - ingreso.getFullYear()) * 12 + (hoy.getMonth() - ingreso.getMonth());
  const acumulados = Math.floor((meses / 12) * 15);
  const tomados = empleado.diasVacacionesTomados || 0;
  const disponibles = Math.max(0, acumulados - tomados);
  return { acumulados, tomados, disponibles };
}

/* ── Initials from Name ─────────────────────────────────────── */
function initials(nombre = '') {
  const parts = nombre.trim().split(' ').filter(Boolean);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return (parts[0] || '?').slice(0, 2).toUpperCase();
}

/* ── Sidebar Injection ──────────────────────────────────────── */
function buildSidebar() {
  const mount = document.getElementById('sidebar-mount');
  if (!mount) return;
  mount.innerHTML = `
    <div class="sidebar-brand">
      <div class="sidebar-logo" aria-hidden="true">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
             fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/>
        </svg>
      </div>
      <div class="sidebar-brand-text">
        <div class="sidebar-brand-name">GestiónRH</div>
        <div class="sidebar-brand-sub">Adm. de Empleados</div>
      </div>
    </div>

    <nav class="sidebar-nav" aria-label="Menú principal">
      <span class="nav-section">Principal</span>

      <a href="dashboard.html" class="nav-link" data-roles="jefe" aria-label="Dashboard">
        <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>
          <rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>
        </svg>
        <span class="nav-text">Dashboard</span>
      </a>

      <a href="empleados.html" class="nav-link" data-roles="jefe,regente,auxiliar,operario">
        <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/>
        </svg>
        <span class="nav-text">Empleados</span>
      </a>

      <span class="nav-section">Operaciones</span>

      <a href="eventos.html" class="nav-link" data-roles="jefe,regente,auxiliar">
        <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <rect x="3" y="4" width="18" height="18" rx="2"/>
          <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
          <line x1="3" y1="10" x2="21" y2="10"/>
        </svg>
        <span class="nav-text">Eventos Laborales</span>
      </a>

      <a href="horarios.html" class="nav-link" data-roles="jefe,regente,auxiliar">
        <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
        <span class="nav-text">Horarios y Turnos</span>
      </a>

      <a href="horas-extras.html" class="nav-link" data-roles="jefe,regente,auxiliar,operario">
        <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
          <circle cx="18" cy="6" r="3" fill="currentColor" stroke="none"/>
          <line x1="17" y1="5" x2="19" y2="7" stroke-width="1.5"/><line x1="19" y1="5" x2="17" y2="7" stroke-width="1.5"/>
        </svg>
        <span class="nav-text">Horas Extras</span>
      </a>

      <span class="nav-section" data-roles="jefe">Configuración</span>

      <a href="catalogos.html" class="nav-link" data-roles="jefe">
        <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
             fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/>
        </svg>
        <span class="nav-text">Catálogos</span>
      </a>
    </nav>

    <div class="sidebar-footer">
      <div class="sidebar-user">
        <div class="sidebar-avatar" data-user-avatar aria-hidden="true">JE</div>
        <div class="sidebar-user-info">
          <div class="sidebar-user-name" data-user-name>Carlos A. Rodríguez</div>
          <div class="sidebar-user-role" data-user-role>Jefe de Sede</div>
        </div>
        <a href="index.html" title="Cerrar sesión" aria-label="Cerrar sesión"
           style="color:rgba(255,255,255,0.45); flex-shrink:0; display:flex; align-items:center;">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
               fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
        </a>
      </div>
    </div>
  `;
}

/* ── Confirm Dialog ─────────────────────────────────────────── */
function confirmAction(title, message, confirmLabel, type = 'danger') {
  return new Promise(resolve => {
    const overlay = document.getElementById('confirm-modal');
    if (!overlay) { resolve(true); return; }

    document.getElementById('confirm-title').textContent = title;
    document.getElementById('confirm-message').textContent = message;
    const btn = document.getElementById('confirm-btn');
    btn.textContent = confirmLabel;
    btn.className = `btn ${type === 'danger' ? 'btn-danger' : 'btn-primary'}`;

    openModal('confirm-modal');

    const onConfirm = () => {
      closeModal('confirm-modal');
      btn.removeEventListener('click', onConfirm);
      resolve(true);
    };
    btn.addEventListener('click', onConfirm);

    const cancelBtn = overlay.querySelector('[data-modal-close]');
    if (cancelBtn) {
      const onCancel = () => {
        closeModal('confirm-modal');
        cancelBtn.removeEventListener('click', onCancel);
        resolve(false);
      };
      cancelBtn.addEventListener('click', onCancel);
    }
  });
}
