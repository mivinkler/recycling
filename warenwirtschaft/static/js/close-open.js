// Helfer zum (de-)aktivieren der Felder in einer Tabellenzeile
function setRowLockState(row, open) {
  // Nur sichtbare, bearbeitbare Felder anpacken (keine hidden inputs)
  const controls = row.querySelectorAll(
    'input:not([type="hidden"]), select, textarea, button.btn-weight'
  );

  controls.forEach(el => {
    // "disabled" und "readonly" je nach Zustand setzen
    if (open) {
      el.disabled = false;
      el.readOnly = false;
      el.setAttribute('aria-disabled', 'false');
    } else {
      el.disabled = true;
      el.readOnly = true;
      el.setAttribute('aria-disabled', 'true');
    }
  });
}

// Initial alle Zeilen schließen (außer если хочешь одну открытую по умолчанию)
function lockAllRows() {
  document.querySelectorAll('.itemcard-table-row').forEach(row => {
    row.classList.remove('is-open');
    setRowLockState(row, /*open=*/false);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  // Beim Laden alles закрыть
  lockAllRows();
});

// Akkordeon-Logik + (de)aktivieren Felder
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.btn-lock');
  if (!btn) return;

  const row = btn.closest('.itemcard-table-row');
  if (!row) return;

  // Zuerst alle anderen Zeilen schließen
  document.querySelectorAll('.itemcard-table-row.is-open')
    .forEach(r => {
      if (r !== row) {
        r.classList.remove('is-open');
        setRowLockState(r, /*open=*/false);
      }
    });

  // Aktuelle Zeile umschalten
  const willOpen = !row.classList.contains('is-open');
  row.classList.toggle('is-open', willOpen);
  setRowLockState(row, /*open=*/willOpen);
});