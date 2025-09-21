document.addEventListener('DOMContentLoaded', () => {
  const barcodeInput = document.getElementById('barcode');
  if (!barcodeInput) return;

  const apiUrl = barcodeInput.dataset.api;
  const allowedPrefix = barcodeInput.dataset.accepted || 'G';

  // Селект поставщика и текстовое поле Lieferschein по id
  const customerSelect = document.getElementById('id_customer');
  const receiptInput  = document.getElementById('id_delivery_receipt');

  const tbody = document.querySelector('.itemcard-tbody');
  const addRowBtn = document.getElementById('form-add-btn');

  barcodeInput.addEventListener('keypress', async (e) => {
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

      // Kunde setzen, nur если опция существует
      if (data.customer && customerSelect) {
        const opt = customerSelect.querySelector(`option[value="${data.customer}"]`);
        if (opt) {
          customerSelect.value = data.customer;
        } else {
          // при желании можно показать предупреждение
          console.warn(`Unbekannter Lieferant: ${data.customer}`);
        }
      }

      // Lieferschein in Textfeld schreiben (это не select)
      if (data.delivery_receipt && receiptInput) {
        receiptInput.value = data.delivery_receipt;
      }

      // Neue Zeile hinzufügen
      addRowBtn?.click();
      const rows = tbody.querySelectorAll('.itemcard-table-row');
      const lastRow = rows[rows.length - 1];

      // Material und Box-Type setzen
      if (lastRow) {
        if (data.material) {
          const materialSelect = lastRow.querySelector('select[name$="-material"]');
          if (materialSelect) materialSelect.value = data.material;
        }
        if (data.box_type) {
          const boxSelect = lastRow.querySelector('select[name$="-box_type"]');
          if (boxSelect) boxSelect.value = data.box_type;
        }
      }
    } catch (err) {
      alert('Barcode konnte nicht verarbeitet werden.');
    }
  });
});
