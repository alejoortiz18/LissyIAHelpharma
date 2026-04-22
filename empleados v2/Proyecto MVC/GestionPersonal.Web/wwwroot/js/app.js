/* ============================================================
   GESTIÓN RH — app.js  |  MVC version
   Modals · Tabs · Toast · Confirm · Form helpers
   ============================================================ */
'use strict';

document.addEventListener('DOMContentLoaded', function () {

    /* ── Contrato temporal toggle ───────────────────────────── */
    var selTipo = document.getElementById('TipoVinculacion');
    var secTemporal = document.getElementById('seccion-temporal');
    if (selTipo && secTemporal) {
        function toggleTemporal() {
            var esTemporal = selTipo.value === 'Temporal';
            secTemporal.hidden = !esTemporal;
        }
        toggleTemporal();
        selTipo.addEventListener('change', toggleTemporal);
    }

    /* ── Shift form toggles (plantilla turno) ───────────────── */
    document.querySelectorAll('.shift-check').forEach(function (chk) {
        var idx = chk.getAttribute('data-idx');
        var timesDiv = document.getElementById('s-times-' + idx);
        var labelEl  = document.getElementById('s-label-' + idx);
        if (!timesDiv) return;
        function toggleShift() {
            timesDiv.hidden = !chk.checked;
            if (labelEl) labelEl.textContent = chk.checked ? 'Labora' : 'No labora';
        }
        toggleShift();
        chk.addEventListener('change', toggleShift);
    });

    /* ── Auto-dismiss alerts after 4 s ─────────────────────── */
    document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
        setTimeout(function () { alert.style.opacity = '0'; setTimeout(function () { alert.remove(); }, 400); }, 4000);
    });

    /* ── Modals ─────────────────────────────────────────────── */
    document.querySelectorAll('[data-modal-open]').forEach(function (btn) {
        btn.addEventListener('click', function () { openModal(btn.getAttribute('data-modal-open')); });
    });
    document.querySelectorAll('[data-modal-close]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var overlay = btn.closest('.modal-overlay');
            if (overlay) closeModal(overlay.id);
        });
    });
    document.querySelectorAll('.modal-overlay').forEach(function (overlay) {
        overlay.addEventListener('click', function (e) {
            if (e.target === overlay) closeModal(overlay.id);
        });
    });
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            var open = document.querySelector('.modal-overlay:not([hidden])');
            if (open) closeModal(open.id);
        }
    });

    /* ── Tabs ───────────────────────────────────────────────── */
    document.querySelectorAll('.tabs').forEach(function (tabGroup) {
        var buttons = tabGroup.querySelectorAll('.tab-btn');
        buttons.forEach(function (btn) {
            btn.addEventListener('click', function () {
                var target = btn.getAttribute('data-tab');
                if (!target) return;
                buttons.forEach(function (b) {
                    b.classList.remove('is-active');
                    b.setAttribute('aria-selected', 'false');
                });
                btn.classList.add('is-active');
                btn.setAttribute('aria-selected', 'true');
                var container = btn.closest('[data-tabs-container]') || document;
                container.querySelectorAll('.tab-panel').forEach(function (p) {
                    p.classList.toggle('is-active', p.id === target);
                });
            });
            btn.addEventListener('keydown', function (e) {
                var btns = Array.from(buttons);
                var idx = btns.indexOf(btn);
                if (e.key === 'ArrowRight' && idx < btns.length - 1) btns[idx + 1].focus();
                if (e.key === 'ArrowLeft'  && idx > 0)               btns[idx - 1].focus();
            });
        });
    });

});

/* ── Modal helpers (global) ─────────────────────────────────── */
function openModal(id) {
    var overlay = document.getElementById(id);
    if (!overlay) return;
    overlay.hidden = false;
    overlay.removeAttribute('aria-hidden');
    var first = overlay.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (first) first.focus();
}

function closeModal(id) {
    var overlay = document.getElementById(id);
    if (!overlay) return;
    overlay.hidden = true;
    overlay.setAttribute('aria-hidden', 'true');
}

/* ── Toast (global) ─────────────────────────────────────────── */
function showToast(message, type, duration) {
    type = type || 'default';
    duration = duration || 3500;
    var container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        container.setAttribute('aria-live', 'polite');
        container.setAttribute('aria-atomic', 'false');
        document.body.appendChild(container);
    }
    var toast = document.createElement('div');
    toast.className = 'toast' + (type !== 'default' ? ' toast--' + type : '');
    toast.setAttribute('role', 'status');
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(function () { toast.remove(); }, duration);
}

/* ── Confirm dialog (global) ────────────────────────────────── */
function confirmAction(title, message, confirmLabel, type) {
    type = type || 'danger';
    return new Promise(function (resolve) {
        var overlay = document.getElementById('confirm-modal');
        if (!overlay) { resolve(true); return; }
        document.getElementById('confirm-title').textContent   = title;
        document.getElementById('confirm-message').textContent = message;
        var btn = document.getElementById('confirm-btn');
        btn.textContent = confirmLabel;
        btn.className   = 'btn ' + (type === 'danger' ? 'btn-danger' : 'btn-primary');
        openModal('confirm-modal');
        function onConfirm() {
            closeModal('confirm-modal');
            btn.removeEventListener('click', onConfirm);
            resolve(true);
        }
        btn.addEventListener('click', onConfirm);
        var cancelBtn = overlay.querySelector('[data-modal-close]');
        if (cancelBtn) {
            function onCancel() {
                closeModal('confirm-modal');
                cancelBtn.removeEventListener('click', onCancel);
                resolve(false);
            }
            cancelBtn.addEventListener('click', onCancel);
        }
    });
}

/* ── Format helpers (global) ────────────────────────────────── */
var fmt = {
    date: function (str) {
        if (!str) return '—';
        return new Intl.DateTimeFormat('es-CO', { year: 'numeric', month: 'short', day: 'numeric' }).format(new Date(str + 'T12:00:00'));
    },
    dateRange: function (start, end) {
        if (!start) return '—';
        return fmt.date(start) + (end ? ' → ' + fmt.date(end) : '');
    },
};
