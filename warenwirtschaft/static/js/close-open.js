// ============================================
// Zeilensteuerung (Create + Update)
// ============================================

function getMode() {
  const form = document.getElementById('unload-form');
  return (form && form.dataset && form.dataset.mode) ? form.dataset.mode : 'create';
}

// 🇩🇪 Editierbare Controls einer Zeile auswählen (ohne Hidden)
function getEditableControls(row) {
  return row.querySelectorAll('input:not([type="hidden"]), select, textarea, button.btn-weight');
}

// 🇩🇪 Ursprungswerte einmalig merken (für Reset bei Schließen)
function snapshotRow(row) {
  if (row.dataset.snapshotted === '1') return;
  getEditableControls(row).forEach(el => {
    if (el.type === 'checkbox' || el.type === 'radio') {
      el.dataset.initialChecked = String(el.checked);
    } else if (el instanceof HTMLButtonElement) {
      // Buttons haben keinen Wert – überspringen
    } else {
      el.dataset.initialValue = el.value;
    }
  });
  row.dataset.snapshotted = '1';
}

// 🇩🇪 Werte auf Ursprungszustand zurücksetzen (wenn nicht gespeichert)
function restoreRow(row) {
  getEditableControls(row).forEach(el => {
    if (el.type === 'checkbox' || el.type === 'radio') {
      if (el.dataset.initialChecked !== undefined) {
        el.checked = (el.dataset.initialChecked === 'true');
      }
    } else if (!(el instanceof HTMLButtonElement) && el.dataset.initialValue !== undefined) {
      el.value = el.dataset.initialValue;
    }
  });
}

// 🇩🇪 Felder (de)aktivieren + Radio behandeln
function setRowLockState(row, open) {
  const mode = getMode();
  const keepRow = row.hasAttribute('data-keep-enabled-row'); // Update: verknüpft => aktiv lassen

  getEditableControls(row).forEach(el => {
    if (el.classList.contains('btn-lock')) return;

    const isRadio = el.matches('input[type="radio"][name="selected_recycling"]');
    const keepRadio = isRadio && el.hasAttribute('data-keep-enabled');

    // 🇩🇪 Update: verknüpfte Zeilen bleiben bedienbar (auch bei geschlossenem Schloss)
    if (keepRow) {
      el.disabled = false;
      if (!(el instanceof HTMLButtonElement)) el.readOnly = false;
      el.setAttribute('aria-disabled', 'false');
      return;
    }

    // 🇩🇪 Update: Radio-checked NIE automatisch ändern
    if (mode === 'update' && isRadio) {
      if (!keepRadio) {
        el.disabled = !open;
        el.setAttribute('aria-disabled', String(!open));
      } else {
        el.disabled = false;
        el.setAttribute('aria-disabled', 'false');
      }
      return;
    }

    // 🇩🇪 Standard (Create + andere Inputs)
    el.disabled = !open;
    if (!(el instanceof HTMLButtonElement)) el.readOnly = !open;
    el.setAttribute('aria-disabled', String(!open));
  });

  // 🇩🇪 Auto-Check NUR im Create-Modus
  if (getMode() === 'create' && !row.hasAttribute('data-keep-enabled-row')) {
    const radio = row.querySelector('input[type="radio"][name="selected_recycling"]:not([data-keep-enabled])');
    if (radio) {
      radio.disabled = !open;
      radio.checked  = !!open;
    }
  }

  const lockBtn = row.querySelector('.btn-lock');
  if (lockBtn) lockBtn.setAttribute('aria-pressed', String(!!open));
}

// 🇩🇪 Alle Zeilen schließen (Startzustand)
function lockAllRows() {
  document.querySelectorAll('.itemcard-table-row').forEach(row => {
    row.classList.remove('is-open');
    snapshotRow(row);
    setRowLockState(row, /*open=*/false);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  lockAllRows();

  // 🇩🇪 Create: ersten "Neue Wagen"-Lock automatisch öffnen
  if (getMode() === 'create') {
    const firstNewLockBtn = document.querySelector('tbody .itemcard-table-row[data-kind="new"] .btn-lock');
    if (firstNewLockBtn) firstNewLockBtn.click();
  }
});

// 🇩🇪 Akkordeon – immer nur eine Zeile offen (über beide Tabellen hinweg)
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.btn-lock');
  if (!btn) return;

  const row = btn.closest('.itemcard-table-row');
  if (!row) return;

  const willOpen = !row.classList.contains('is-open');

  // 1) Andere offene Zeilen schließen + zurücksetzen
  document.querySelectorAll('.itemcard-table-row.is-open').forEach(other => {
    if (other === row) return;
    restoreRow(other);
    other.classList.remove('is-open');
    setRowLockState(other, /*open=*/false);
  });

  // 2) Aktuelle Zeile toggeln
  if (willOpen) {
    snapshotRow(row);
    row.classList.add('is-open');
    setRowLockState(row, /*open=*/true);
  } else {
    restoreRow(row);
    row.classList.remove('is-open');
    setRowLockState(row, /*open=*/false);
  }

  // 🇩🇪 Hidden "active_row" setzen (für Update: Unlink)
  const hidden = document.getElementById('active_row');
  if (hidden) {
    const value = row.dataset.kind === 'new' ? ('new:' + row.dataset.key) : String(row.dataset.key || '');
    hidden.value = value;
  }
});

// =====================================================
// 🇩🇪 Update: verknüpfte Radio-Zeile aktiv abwählbar machen
// - Nur wenn Zeile offen ist
// - Klick auf Radio toggelt es AUS (unchecked)
// - Beim Submit setzen wir unlink_pk für den Server
// =====================================================
document.addEventListener('click', (e) => {
  const radio = e.target.closest('input[type="radio"][name="selected_recycling"][data-keep-enabled]');
  if (!radio) return;
  if (getMode() !== 'update') return;

  const row = radio.closest('.itemcard-table-row');
  if (!row || !row.classList.contains('is-open')) return;

  // Radio explizit abwählen
  e.preventDefault();
  radio.checked = false;

  // Merken, wen wir entfernen wollen
  const hiddenUnlink = document.getElementById('unlink_pk');
  if (hiddenUnlink) hiddenUnlink.value = String(row.dataset.key || '');

  // Auch active_row setzen (на всякий случай)
  const hiddenActive = document.getElementById('active_row');
  if (hiddenActive) hiddenActive.value = String(row.dataset.key || '');
});

// 🇩🇪 Vor dem Submit: falls offene verknüpfte Zeile ohne Haken -> unlink_pk setzen
document.getElementById('unload-form')?.addEventListener('submit', () => {
  if (getMode() !== 'update') return;

  const openLinked = document.querySelector('.itemcard-table-row.is-open[data-kind="existing"][data-keep-enabled-row]');
  if (!openLinked) return;

  const radio = openLinked.querySelector('input[type="radio"][name="selected_recycling"][data-keep-enabled]');
  if (radio && !radio.checked) {
    const hiddenUnlink = document.getElementById('unlink_pk');
    if (hiddenUnlink) hiddenUnlink.value = String(openLinked.dataset.key || '');
    const hiddenActive = document.getElementById('active_row');
    if (hiddenActive) hiddenActive.value = String(openLinked.dataset.key || '');
  }
});
