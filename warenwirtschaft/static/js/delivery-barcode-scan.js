document.addEventListener('DOMContentLoaded', () => {
  const barcodeInput = document.getElementById('barcode');
  const table = document.querySelector('.table');
  const addBtn = document.getElementById('add-form-btn');

  const supplierSelect = document.querySelector('select[name="supplier"]');
  const receiptInput = document.querySelector('input[name="delivery_receipt"]');

  // Suche die erste leere Zeile (nach Gewicht-Feld)
  const findEmptyRow = () => {
    const rows = table?.querySelectorAll('.table-row');
    for (const row of rows) {
      const weightInput = row.querySelector('[name$="-weight"]');
      if (weightInput && !weightInput.value) {
        return row;
      }
    }
    return null;
  };

  // Fügt die übergebene Zeichenfolge mit Daten
  const fillRow = (row, fields) => {
    for (const [key, value] of Object.entries(fields)) {
      const input = row.querySelector(`[name$="-${key}"]`);
      if (input) input.value = value;
    }
  };

  // Barcode Scan Verarbeitung
  barcodeInput?.addEventListener('keypress', async (e) => {
    if (e.key !== 'Enter') return;
    e.preventDefault();

    const code = barcodeInput.value.trim().toUpperCase();
    if (!code) return;

    try {
      const res = await fetch(`/api/delivery-input/?code=${encodeURIComponent(code)}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Fehler beim Barcode');

      // Geben Sie den Lieferanten und ggf. die Lieferschein ein.
      if (data.supplier && supplierSelect) supplierSelect.value = data.supplier;
      if (data.delivery_receipt && receiptInput) receiptInput.value = data.delivery_receipt;

      // Suchen nach der ersten leere Zeile
      let row = findEmptyRow();

      // Wenn keine leere Zeile vorhanden ist, fügen wir sie hinzu
      if (!row) {
        addBtn?.click();
        await new Promise(resolve => setTimeout(resolve, 50)); // ждём DOM
        row = findEmptyRow();
      }

      // Füllen die Zeile aus
      if (row) fillRow(row, data);

      barcodeInput.value = '';
    } catch (err) {
      alert(err.message || 'Barcode konnte nicht verarbeitet werden.');
      barcodeInput.value = '';
    }
  });
});
