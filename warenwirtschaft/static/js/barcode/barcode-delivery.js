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

  // Auf neue Zeile warten (nach Klick auf "+")
  async function waitForNewRow(expectedCount, timeoutMs = 800) {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      if (getRows().length >= expectedCount) return true;
      await new Promise(r => setTimeout(r, 25));
    }
    return false;
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

  // Lieferant in das passende Feld schreiben (ModelChoiceField erwartet PK)
  function setCustomer(data) {
    const customerSelect = document.getElementById('id_customer'); // Variante: ein <select>
    if (customerSelect && data.customer_id != null) {
      const wanted = String(data.customer_id);
      customerSelect.value = wanted;
      if (customerSelect.value !== wanted) {
        const opt = document.createElement('option');
        opt.value = wanted;
        opt.textContent = data.customer_name || wanted;
        customerSelect.appendChild(opt);
        customerSelect.value = wanted;
      }
      return;
    }
    // Variante: getrennte Felder (hidden PK + sichtbarer Text)
    const customerIdInput   = document.getElementById('id_customer_id');
    const customerTextInput = document.getElementById('id_customer');
    if (customerIdInput && data.customer_id != null) customerIdInput.value = String(data.customer_id);
    if (customerTextInput && data.customer_name && !customerTextInput.value) customerTextInput.value = data.customer_name;
  }

  // Nach dem Befüllen sicherstellen: eine leere Zeile am Ende vorhanden
  async function ensureTrailingEmptyRow() {
    if (!findIncompleteRow()) {
      const before = getRows().length;
      addRowBtn?.click();
      await waitForNewRow(before + 1);
      // bewusst NICHT befüllen -> bleibt leer für den nächsten Scan
    }
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

      // Lieferant/Lieferschein vorbelegen (nur wenn leer)
      setCustomer(data);
      const receiptInput = document.getElementById('id_delivery_receipt');
      if (receiptInput && data.delivery_receipt && !receiptInput.value) {
        receiptInput.value = data.delivery_receipt;
      }

      // ZUERST eine unvollständige Zeile verwenden
      let targetRow = findIncompleteRow();

      // Wenn alle Zeilen vollständig sind: neue Zeile anlegen
      if (!targetRow) {
        const before = getRows().length;
        addRowBtn?.click();
        await waitForNewRow(before + 1);
        const rows = getRows();
        targetRow = rows[rows.length - 1] || null;
      }

      if (!targetRow) {
        alert('Keine Tabellenzeile verfügbar.');
        return;
      }

      // Zielzeile befüllen
      fillRowFromData(targetRow, data);

      // Danach sicherstellen, dass am Ende eine leere Zeile bereitsteht
      await ensureTrailingEmptyRow();
    } catch (err) {
      console.error(err);
      alert('Barcode konnte nicht verarbeitet werden.');
    }
  });
});
