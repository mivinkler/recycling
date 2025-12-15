// --- Warten bis DOM bereit ist (falls Script nicht mit 'defer' eingebunden ist)
const ready = (fn) => {
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
  else fn();
};

ready(() => {
  // --- Robuste Delegation auf das Dokument
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.btn-weight'); // Klasse muss mit Template übereinstimmen
    if (!btn) return;

    // --- Zeile & Eingabefeld bestimmen
    const row = btn.closest('tr') || btn.closest('.table-row');
    const weightInput = row?.querySelector('input[name$="-weight"]');
    if (!weightInput) {
      console.warn('[weight.js] Kein Weight-Input in der Zeile gefunden');
      return;
    }

    // --- URL prüfen (aus data-Attribut oder Fallback)
    const url = btn.dataset.weightUrl || '/api/weight-data/';
    // Optional: debuggen
    // console.log('weight url:', url);

    try {
      const res = await fetch(url, {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        credentials: 'same-origin', // --- Session-Cookies mitschicken (Login/CSRF)
      });

      // --- Text lesen und sicher zu JSON parsen (Abfangen von HTML-Redirects)
      const text = await res.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        throw new Error('Unerwartete Antwort (kein JSON) – evtl. Login-Redirect?');
      }

      if (!res.ok || !data?.weight) {
        throw new Error(data?.error || 'Kein Gewicht erhalten.');
      }

      weightInput.value = data.weight;
      weightInput.dispatchEvent(new Event('input', { bubbles: true }));
      weightInput.dispatchEvent(new Event('change', { bubbles: true }));
    } catch (err) {
      alert(err.message || 'Fehler beim Abrufen des Gewichts.');
      console.error('[weight.js]', err);
    }
  });
});
