(() => {
  const barcodeInput = document.getElementById('barcode');
  const imgActive = document.getElementById('barcode-active');
  const imgInactive = document.getElementById('barcode-inactive');

  const setState = active => {
    imgActive.hidden = !active;
    imgInactive.hidden = active;
  };

  barcodeInput.addEventListener('focus', () => setState(true));
  barcodeInput.addEventListener('blur',  () => setState(false));

})();

document.addEventListener('DOMContentLoaded', () => {
  const barcodeInput = document.getElementById('barcode');
  if (!barcodeInput) return;

  const apiUrl        = barcodeInput.dataset.api;
  const allowedPrefix = barcodeInput.dataset.accepted || 'G';

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

      // Lieferant und Lieferschein setzen
      const customerSelect = document.getElementById('id_customer');
      if (data.customer && customerSelect) {
        customerSelect.value = data.customer;
      }

      const receiptInput  = document.getElementById('id_delivery_receipt');
      if (data.delivery_receipt && receiptInput) {
        receiptInput.value = data.delivery_receipt;
      }

      // Neue Zeile hinzufügen
      addRowBtn?.click();
      // Kurze Pause, damit die neue Zeile im DOM verfügbar wird
      await new Promise(resolve => setTimeout(resolve, 50));

      // Die letzte Zeile auswählen und Daten eintragen
      const rows = tbody.querySelectorAll('.itemcard-table-row');
      const lastRow = rows[rows.length - 1];
      if (lastRow) {
        if (data.material) {
          const materialSelect = lastRow.querySelector('select[name$="-material"]');
          if (materialSelect) materialSelect.value = data.material;
        }
        if (data.box_type) {
          const boxSelect = lastRow.querySelector('select[name$="-box_type"]');
          if (boxSelect) boxSelect.value = data.box_type;
        }
        if (data.weight) {
          const weightInput = lastRow.querySelector('input[name$="-weight"]');
          if (weightInput) weightInput.value = data.weight;
        }
      }
    } catch (err) {
      alert('Barcode konnte nicht verarbeitet werden.');
    }
  });
});
