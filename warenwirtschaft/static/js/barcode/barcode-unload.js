document.addEventListener('DOMContentLoaded', () => {
  const input  = document.getElementById('barcode');
  const select = document.getElementById('id_delivery_unit');
  const imgOn  = document.getElementById('barcode-active');
  const imgOff = document.getElementById('barcode-inactive');
  const label  = document.querySelector('label[for="barcode"]');
  const apiUrl = input?.dataset.api || '';

  // Fehlermeldung
  if (!input)  { console.warn('[SCAN] #barcode nicht gefunden'); return; }
  if (!select) { console.warn('[SCAN] #id_delivery_unit nicht gefunden'); return; }
  if (!apiUrl) { console.warn('[SCAN] data-api fehlt am #barcode'); return; }

  // --- Helfer ---
  const toggleIcon = (active) => {
    if (imgOn)  imgOn.hidden  = !active;
    if (imgOff) imgOff.hidden =  active;
  };

  const ensureOption = (id, text = `Einheit #${id}`) => {
    let opt = select.querySelector(`option[value="${id}"]`);
    if (!opt) {
      opt = new Option(text, String(id));
      select.add(opt);
    }
    select.value = String(id);
    // Optional: Formular automatisch senden
    const form = document.getElementById('du-select-form');
    if (form) form.submit();
  };

  const scan = async (code) => {
    const q = code.trim().toUpperCase();
    if (!q) return;

    // URL robust aufbauen, Query-Param setzen
    const url = new URL(apiUrl, window.location.origin);
    // ACHTUNG: Falls dein API-View einen anderen Param-Namen erwartet, hier anpassen.
    url.searchParams.set('code', q);

    let res;
    try {
      res = await fetch(url.toString(), { method: 'GET' });
    } catch (err) {
      console.error('[SCAN] Netzwerkfehler:', err);
      throw err;
    }
    if (!res.ok) {
      console.warn('[SCAN] API antwortete mit Status', res.status);
      throw new Error('not-ok');
    }

    // Defensive JSON-Verarbeitung
    let data;
    try {
      data = await res.json();
    } catch (err) {
      console.error('[SCAN] Ungültiges JSON', err);
      throw err;
    }

    // Erwartete Struktur: { type: "delivery_unit", delivery_unit_id: <int>, label?: <string> }
    if (data?.type === 'delivery_unit' && data?.delivery_unit_id != null) {
      const label = data.label || `Einheit #${data.delivery_unit_id}`;
      ensureOption(data.delivery_unit_id, label);
    } else {
      console.warn('[SCAN] Unerwartetes Antwortformat', data);
      throw new Error('bad-shape');
    }
  };

  // --- Fokus/UX ---
  // input.focus();
  // label?.addEventListener('click', () => input.focus());
  // input.addEventListener('focus', () => toggleIcon(true));
  // input.addEventListener('blur',  () => toggleIcon(false));
  // toggleIcon(document.activeElement === input);

  // --- Enter vom Scanner abfangen ---
  input.addEventListener('keydown', async (e) => {
    if (e.key !== 'Enter') return;
    e.preventDefault();
    const value = input.value;
    input.value = ''; // sofort leeren für nächsten Scan
    try {
      await scan(value);
    } catch (err) {
      alert('Barcode nicht erkannt oder Fehler beim Verarbeiten.');
    }
  });
});
