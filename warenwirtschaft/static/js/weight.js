// static/js/weight.js

document.querySelector('.table')?.addEventListener('click', async (e) => {
  // --- Deutsch: prüfen, ob ein Button mit Klasse .btn-weight geklickt wurde
  const btn = e.target.closest('.btn-weight');
  if (!btn) return;

  // --- Deutsch: die zugehörige Zeile und das Gewichts-Eingabefeld finden
  const row = btn.closest('.table-row');
  const weightInput = row?.querySelector('input[name$="-weight"]');
  if (!weightInput) return;

  try {
    // URL aus data-Attribut oder Fallback
    const url = btn.dataset.weightUrl || '/api/weight-data/';
    const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
    const data = await res.json();

    if (!res.ok || !data.weight) {
      throw new Error(data.error || 'Kein Gewicht');
    }

    weightInput.value = data.weight;

    // --- Deutsch: Events feuern, damit Formset/Validation Änderungen erkennt
    weightInput.dispatchEvent(new Event('input', { bubbles: true }));
    weightInput.dispatchEvent(new Event('change', { bubbles: true }));
  } catch (err) {
    alert(err.message || 'Fehler beim Abrufen des Gewichts.');
    console.error('[weight.js]', err);
  }
});
