document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('barcode');
  const label = document.getElementById('barcode-label');
  const imgOn = document.getElementById('barcode-active');
  const imgOff = document.getElementById('barcode-inactive');

  if (!input) {
    console.warn('[SCAN] #barcode fehlt');
    return;
  }

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

  // Kommentar: Icon-Zustand setzen (aktiv/inaktiv)
  const toggleIcon = (active) => {
    if (imgOn) imgOn.hidden = !active;
    if (imgOff) imgOff.hidden = active;
  };

  // Kommentar: Klick auf Icon setzt Fokus in das Scanner-Feld
  if (label) {
    label.addEventListener('click', () => input.focus());
  }

  input.addEventListener('focus', () => toggleIcon(true));
  input.addEventListener('blur', () => toggleIcon(false));
  toggleIcon(document.activeElement === input);

  // Kommentar: Barcode normalisieren (Trim + Uppercase + GS1-Präfixe entfernen)
  const normalize = (raw) => {
    let s = (raw || '').trim().toUpperCase();

    // Kommentar: GS1/Scanner-Präfixe entfernen (z.B. "]C1")
    s = s.replace(/^\]C\d/, '');   // ]C1, ]C2 ...
    // Kommentar: führende Sonderzeichen entfernen
    s = s.replace(/^[^\w]+/, '');

    return s;
  };

  // Kommentar: Robuster JSON-Fetch (falls Server HTML statt JSON liefert)
  const fetchJsonSafe = async (url) => {
    const res = await fetch(url, { method: 'GET' });
    const ct = (res.headers.get('content-type') || '').toLowerCase();

    let payload = null;
    if (ct.includes('application/json')) {
      payload = await res.json().catch(() => null);
    } else {
      // Kommentar: z.B. Login-HTML oder Fehlerseite
      await res.text().catch(() => '');
      payload = { error: 'Server lieferte kein JSON.' };
    }
    return { res, payload };
  };

  // Kommentar: Weiterleitung zur Create-Seite (recycling_create/<unload_pk>/)
  const goToCreate = (unloadId) => {
    const target = createUrlTemplate.replace('/0/', `/${unloadId}/`);
    window.location.assign(target);
  };

  // Kommentar: Hauptlogik Scan → API → Redirect
  const scan = async (rawCode) => {
    const code = normalize(rawCode);
    if (!code) return;

    // Kommentar: Präfix-Check ("S" für Unload)
    if (acceptedPrefix && !code.startsWith(acceptedPrefix)) {
      alert(`Nur Barcodes mit Präfix "${acceptedPrefix}" sind hier erlaubt.`);
      return;
    }

    // Kommentar: Parameter-Name "barcode" (konsistent mit anderem Screen)
    const url = new URL(apiUrl, window.location.origin);
    url.searchParams.set('code', code);

    const { res, payload } = await fetchJsonSafe(url.toString());

    if (!res.ok) {
      alert(payload?.error || `Fehler beim Barcode-Scan (Status ${res.status}).`);
      return;
    }

    // Erwartet: { unload_id: <int> }  (optional: type: "unload")
    const unloadId = payload?.unload_id ?? payload?.id ?? null;

    if (unloadId == null) {
      console.warn('[SCAN] Unerwartete Antwort:', payload);
      alert('Barcode erkannt, aber keine unload_id erhalten.');
      return;
    }

    goToCreate(unloadId);
  };

  // Kommentar: Scanner sendet meistens Enter
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

  // Kommentar: Fallback, falls Scanner nur "change" feuert
  input.addEventListener('change', (e) => {
    const value = e.target.value;
    e.target.value = '';
    scan(value).catch((err) => {
      console.error('[SCAN] Fehler (change):', err);
      alert('Barcode konnte nicht verarbeitet werden.');
    });
  });
});
