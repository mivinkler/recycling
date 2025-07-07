document.addEventListener('DOMContentLoaded', () => {
  const barcodeInput = document.getElementById('barcode');
  const deliverySelect = document.querySelector('select[name="delivery_unit"]');
  const table = document.querySelector('.table');

  // Automatischer Scan-Handler
  barcodeInput?.addEventListener('keypress', async (e) => {
    if (e.key !== 'Enter') return;
    e.preventDefault();

    const code = barcodeInput.value.trim().toUpperCase();
    if (!code) return;

    try {
      const res = await fetch(`/api/unload-input/?code=${encodeURIComponent(code)}`);
      if (!res.ok) throw new Error("Nicht gefunden");

      const data = await res.json();

      if (data.type === "delivery_unit") {
        const { delivery_unit_id } = data;
        let option = deliverySelect.querySelector(`option[value="${delivery_unit_id}"]`);
        if (!option) {
          option = new Option(`Einheit #${delivery_unit_id}`, delivery_unit_id);
          deliverySelect.appendChild(option);
        }
        deliverySelect.value = delivery_unit_id;
      } else if (data.type === "reusable") {
        const { box_type, material, target } = data;

        const addBtn = document.getElementById('add-form-btn');
        addBtn?.click();

        const rows = table.querySelectorAll('.table-row');
        const lastRow = rows[rows.length - 1];

        lastRow.querySelector('select[name$="-box_type"]').value = box_type;
        lastRow.querySelector('select[name$="-material"]').value = material;
        lastRow.querySelector('select[name$="-target"]').value = target;
      }

      barcodeInput.value = '';
    } catch {
      alert("Barcode nicht erkannt oder Fehler beim Verarbeiten.");
    }
  });

    document.querySelector('.table')?.addEventListener('click', async (e) => {
    if (!e.target.matches('.fetch-weight-btn')) return;

    const row = e.target.closest('.table-row');
    const weightInput = row?.querySelector('input[name$="-weight"]');
    if (!weightInput) return;

    try {
      const res = await fetch('/api/weight-data/');
      const data = await res.json();
      if (!res.ok || !data.weight) throw new Error(data.error || 'Kein Gewicht');

      weightInput.value = data.weight;
    } catch (err) {
      alert(err.message || 'Fehler beim Abrufen des Gewichts.');
    }
  });
});
  