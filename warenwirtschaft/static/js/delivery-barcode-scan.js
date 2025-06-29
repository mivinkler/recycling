document.addEventListener('DOMContentLoaded', () => {
  const barcodeInput = document.getElementById('barcode');
  const table = document.querySelector('.table');
  const addBtn = document.getElementById('add-form-btn');

  const supplierSelect = document.querySelector('select[name="supplier"]');
  const receiptInput = document.querySelector('input[name="delivery_receipt"]');

  const fillLastRow = (fields) => {
    const rows = table?.querySelectorAll('.table-row');
    const lastRow = rows?.[rows.length - 1];
    if (!lastRow) return;

    for (const [key, value] of Object.entries(fields)) {
      const input = lastRow.querySelector(`[name$="-${key}"]`);
      if (input) input.value = value;
    }
  };

  barcodeInput?.addEventListener('keypress', async (e) => {
    if (e.key !== 'Enter') return;
    e.preventDefault();

    const code = barcodeInput.value.trim().toUpperCase();
    if (!code) return;

    try {
      const res = await fetch(`/api/delivery-input/?code=${encodeURIComponent(code)}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Fehler beim Barcode');

      // Setze Lieferant & Lieferschein wenn vorhanden
      if (data.supplier && supplierSelect) {
        supplierSelect.value = data.supplier;
      }
      if (data.delivery_receipt && receiptInput) {
        receiptInput.value = data.delivery_receipt;
      }

      addBtn?.click();
      fillLastRow(data);
      barcodeInput.value = '';
    } catch (err) {
      alert(err.message || 'Barcode konnte nicht verarbeitet werden.');
      barcodeInput.value = '';
    }
  });
});
