// barcode-delivery.js
(() => {})();

document.addEventListener('DOMContentLoaded', () => {
  const barcodeInput = document.getElementById('barcode');
  const imgActive    = document.getElementById('barcode-active');
  const imgInactive  = document.getElementById('barcode-inactive');

  if (!barcodeInput) return;

  // Icons für aktiven/inaktiven Scan-Eingabefokus
  const setState = (active) => {
    if (imgActive)   imgActive.hidden   = !active;
    if (imgInactive) imgInactive.hidden =  active;
  };
  barcodeInput.addEventListener('focus', () => setState(true));
  barcodeInput.addEventListener('blur',  () => setState(false));

  // Konfiguration
  const apiUrl        = barcodeInput.dataset.api;
  const allowedPrefix = barcodeInput.dataset.accepted || 'G';

  // Selektoren/Helfer
  const addRowBtn = document.getElementById('form-add-btn');
  const getRows   = () => Array.from(document.querySelectorAll('.itemcard-table-row'));

  function isFilled(el) {
    return !!(el && String(el.value || '').trim());
  }

  // Erste unvollständige Tabellenzeile finden
  function findIncompleteRow() {
    for (const row of getRows()) {
      const sMat = row.querySelector('select[name$="-material"]');
      const sBox = row.querySelector('select[name$="-box_type"]');
      const iWgt = row.querySelector('input[name$="-weight"]');
      if (!isFilled(sMat) || !isFilled(sBox) || !isFilled(iWgt)) return row;
    }
    return null;
  }

  // Zeile mit API-Daten befüllen – nur leere Felder setzen
  function fillRowFromData(row, data) {
    const sMat = row.querySelector('select[name$="-material"]');
    const sBox = row.querySelector('select[name$="-box_type"]');
    const iWgt = row.querySelector('input[name$="-weight"]');

    if (sMat && !isFilled(sMat) && data.material != null) sMat.value = String(data.material);
    if (sBox && !isFilled(sBox) && data.box_type != null) sBox.value = String(data.box_type);
    if (iWgt && !isFilled(iWgt) && data.weight)           iWgt.value = data.weight;
  }

  // Barcode-Scan (Enter)
  barcodeInput.addEventListener('keydown', async (e) => {
    if (e.key !== 'Enter') return;
    e.preventDefault();

    const code = barcodeInput.value.trim().toUpperCase();
    barcodeInput.value = '';
    if (!code) return;

    if (!code.startsWith(allowedPrefix)) {
      alert(`Nur Barcodes mit ${allowedPrefix}-Präfix sind für Wareneingang gültig.`);
      return;
    }

    try {
      const response = await fetch(`${apiUrl}?barcode=${encodeURIComponent(code)}`);
      const data = await response.json();
      if (!response.ok) {
        alert(data.error || 'Fehler beim Barcode');
        return;
      }

      // ZUERST eine unvollständige Zeile verwenden
      let targetRow = findIncompleteRow();

      // Zielzeile befüllen
      fillRowFromData(targetRow, data);

    } catch (err) {
      console.error(err);
      alert('Barcode konnte nicht verarbeitet werden.');
    }
  });
});
