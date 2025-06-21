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
        // ⬇️ Zuerst Liefereinheit versuchen
        let res = await fetch(`/api/unload-input/?code=${encodeURIComponent(code)}&type=unit`);
        if (res.ok) {
          const { delivery_unit_id } = await res.json();
          let option = deliverySelect.querySelector(`option[value="${delivery_unit_id}"]`);
          if (!option) {
            option = new Option(`Einheit #${delivery_unit_id}`, delivery_unit_id);
            deliverySelect.appendChild(option);
          }
          deliverySelect.value = delivery_unit_id;
          barcodeInput.value = '';
          return;
        }

        // ⬇️ Falls nicht gefunden: ReusableBarcode versuchen
        res = await fetch(`/api/unload-input/?code=${encodeURIComponent(code)}&type=reuse`);
        if (res.ok) {
          const { box_type, material, target } = await res.json();

          // Füge neue Zeile hinzu, falls nötig
          const addBtn = document.getElementById('add-form-btn');
          addBtn?.click();

          const rows = table.querySelectorAll('.table-row');
          const lastRow = rows[rows.length - 1];

          lastRow.querySelector('select[name$="-box_type"]').value = box_type;
          lastRow.querySelector('select[name$="-material"]').value = material;
          lastRow.querySelector('select[name$="-target"]').value = target;

          barcodeInput.value = '';
          return;
        }

        alert("Barcode nicht erkannt.");
      } catch {
        alert("Fehler beim Verarbeiten des Barcodes.");
      }
    });

    // Gewicht abfragen
    table?.addEventListener('click', async (e) => {
      if (!e.target.matches('.fetch-weight-btn')) return;

      const row = e.target.closest('.table-row');
      const input = row?.querySelector('input[name$="-weight"]');
      if (!input) return;

      try {
        const res = await fetch('/api/weight-data/');
        if (!res.ok) throw new Error();
        const { weight } = await res.json();
        if (weight !== undefined) input.value = weight;
        else alert("Ungültiges Gewicht");
      } catch {
        alert("Fehler beim Abrufen des Gewichts.");
      }
    });
  });