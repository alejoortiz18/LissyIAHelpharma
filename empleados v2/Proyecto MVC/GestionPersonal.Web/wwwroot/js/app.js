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
            var confirmEl = document.getElementById('confirm-modal');
            if (confirmEl && !confirmEl.hidden) return;
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
var _confirmPending = null;

/**
 * Muestra el modal de confirmación del sitio.
 * @param {string|object} titleOrOpts — título o { title, subtitle, message, confirmLabel, type, itemType, itemName }
 */
function confirmAction(titleOrOpts, message, confirmLabel, type) {
    var opts = typeof titleOrOpts === 'object' && titleOrOpts !== null
        ? titleOrOpts
        : {
            title: titleOrOpts,
            message: message || '',
            confirmLabel: confirmLabel || 'Confirmar',
            type: type || 'danger'
        };

    opts.type = opts.type || 'danger';
    opts.confirmLabel = opts.confirmLabel || 'Confirmar';

    return new Promise(function (resolve) {
        var overlay = document.getElementById('confirm-modal');
        if (!overlay) { resolve(window.confirm(opts.title + '\n\n' + (opts.message || ''))); return; }

        if (_confirmPending) {
            _confirmPending.resolve(false);
            _confirmPending.teardown();
            _confirmPending = null;
        }

        var panel = document.getElementById('confirm-modal-panel');
        var isDanger = opts.type === 'danger';

        document.getElementById('confirm-title').textContent = opts.title || 'Confirmar';
        var subtitleEl = document.getElementById('confirm-subtitle');
        subtitleEl.textContent = opts.subtitle || '';
        subtitleEl.hidden = !opts.subtitle;

        document.getElementById('confirm-message').textContent = opts.message || '';

        var itemWrap = document.getElementById('confirm-item-wrap');
        var hasItem = !!(opts.itemName);
        itemWrap.hidden = !hasItem;
        if (hasItem) {
            document.getElementById('confirm-item-type').textContent = opts.itemType || '';
            document.getElementById('confirm-item-name').textContent = opts.itemName;
        }

        document.getElementById('confirm-icon-danger').hidden = !isDanger;
        document.getElementById('confirm-icon-primary').hidden = isDanger;

        panel.classList.toggle('modal--danger-confirm', isDanger);
        panel.classList.toggle('modal--info-confirm', !isDanger);

        var btn = document.getElementById('confirm-btn');
        btn.textContent = opts.confirmLabel;
        btn.className = 'btn ' + (isDanger ? 'btn-danger' : 'btn-primary');

        function finish(ok) {
            closeModal('confirm-modal');
            if (_confirmPending) {
                _confirmPending.teardown();
                _confirmPending = null;
            }
            resolve(ok);
        }

        function onConfirm() { finish(true); }
        function onCancel() { finish(false); }

        btn.addEventListener('click', onConfirm);
        overlay.querySelectorAll('[data-confirm-cancel]').forEach(function (el) {
            el.addEventListener('click', onCancel);
        });
        function onOverlayClick(e) {
            if (e.target === overlay) onCancel();
        }
        overlay.addEventListener('click', onOverlayClick);
        function onEscape(e) {
            if (e.key === 'Escape' && !overlay.hidden) onCancel();
        }
        document.addEventListener('keydown', onEscape);

        _confirmPending = {
            resolve: resolve,
            teardown: function () {
                btn.removeEventListener('click', onConfirm);
                overlay.querySelectorAll('[data-confirm-cancel]').forEach(function (el) {
                    el.removeEventListener('click', onCancel);
                });
                overlay.removeEventListener('click', onOverlayClick);
                document.removeEventListener('keydown', onEscape);
            }
        };

        openModal('confirm-modal');
        btn.focus();
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
