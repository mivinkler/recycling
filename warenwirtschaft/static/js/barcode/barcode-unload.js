document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('barcode');
  const label = document.getElementById('barcode-label');
  const imgOn = document.getElementById('barcode-active');
  const imgOff = document.getElementById('barcode-inactive');

  if (!input) return;

  const apiUrl = input.dataset.api || '';
  const createUrlTemplate = input.dataset.createUrl || '';
  const acceptedPrefix = (input.dataset.accepted || '').toUpperCase();

  if (!apiUrl) {
    console.warn('[SCAN] data-api fehlt am #barcode');
    return;
  }
  if (!createUrlTemplate.includes('/0/')) {
    console.warn('[SCAN] data-create-url fehlt oder hat keinen /0/-Platzhalter');
    return;
  }

  // Icon-Zustand setzen
  const toggleIcon = (active) => {
    if (imgOn) imgOn.hidden = !active;
    if (imgOff) imgOff.hidden = active;
  };

  // Beim Klick auf Icon Fokus setzen
  if (label) {
    label.addEventListener('click', () => input.focus());
  }

  input.addEventListener('focus', () => toggleIcon(true));
  input.addEventListener('blur', () => toggleIcon(false));
  toggleIcon(document.activeElement === input);

  const normalize = (raw) => (raw || '').toUpperCase().trim();

  const goToCreate = (duId) => {
    // URL-Template "/.../0/" → "/.../<id>/"
    const target = createUrlTemplate.replace('/0/', `/${duId}/`);
    window.location.assign(target);
  };

  const fetchJsonSafe = async (url) => {
    const res = await fetch(url, { method: 'GET' });
    const ct = (res.headers.get('content-type') || '').toLowerCase();

    let payload = null;
    if (ct.includes('application/json')) {
      payload = await res.json().catch(() => null);
    } else {
      // falls HTML/Redirect/Login zurückkommt
      const text = await res.text().catch(() => '');
      payload = { error: text ? 'Server lieferte kein JSON.' : 'Serverantwort ungültig.' };
    }
    return { res, payload };
  };

  const scan = async (rawCode) => {
    const code = normalize(rawCode);
    if (!code) return;

    if (acceptedPrefix && !code.startsWith(acceptedPrefix)) {
      alert(`Nur Barcodes mit Präfix "${acceptedPrefix}" sind hier erlaubt.`);
      return;
    }

    const url = new URL(apiUrl, window.location.origin);
    url.searchParams.set('code', code);

    const { res, payload } = await fetchJsonSafe(url.toString());

    if (!res.ok) {
      alert(payload?.error || `Fehler beim Barcode-Scan (Status ${res.status}).`);
      return;
    }

    // Wartet auf: { delivery_unit_id: <int> }
    const duId = payload?.delivery_unit_id;
    if (duId == null) {
      console.warn('[SCAN] Unerwartete Antwort:', payload);
      alert('Barcode erkannt, aber keine delivery_unit_id erhalten.');
      return;
    }

    goToCreate(duId);
  };

  // Scanner sendet meistens Enter
  input.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter' && e.key !== 'NumpadEnter') return;
    e.preventDefault();

    const value = input.value;
    input.value = '';
    scan(value).catch((err) => {
      console.error('[SCAN] Fehler:', err);
      alert('Barcode konnte nicht verarbeitet werden.');
    });
  });
});
