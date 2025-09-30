document.addEventListener('DOMContentLoaded', () => {
  const input   = document.getElementById('barcode');
  const select  = document.getElementById('id_unload');         // Ziel-Select
  const apiUrl  = input?.dataset.api || '';
  const accepted = (input?.dataset.accepted || '').toUpperCase();

  // Grundprüfung
  if (!input)  { console.warn('[SCAN] #barcode fehlt'); return; }
  if (!select) { console.warn('[SCAN] #id_unload fehlt'); return; }
  if (!apiUrl) { console.warn('[SCAN] data-api am #barcode fehlt'); return; }

  // Falls Enter im Feld die ganze Seite submitten würde – verhindern
  const parentForm = input.closest('form');
  if (parentForm) {
    parentForm.addEventListener('submit', (e) => {
      if (document.activeElement === input) e.preventDefault();
    });
  }

  // Normalisierung: Großschreibung + Whitespace/CR/LF entfernen
  const normalize = (raw) => (raw || '').toUpperCase().replace(/[\s\r\n]+/g, '');

  // Option im Select sicherstellen + auswählen (kein Autosubmit)
  const ensureOption = (id, text = `Einheit #${id}`) => {
    let opt = select.querySelector(`option[value="${id}"]`);
    if (!opt) {
      opt = new Option(text, String(id));
      select.add(opt);
    }
    select.value = String(id);
  };

  // Hauptlogik Scan → API → Select setzen
  const scan = async (raw) => {
    const code = normalize(raw);
    if (!code) { console.warn('[SCAN] leerer Code'); return; }

    // Clientseitige Präfixprüfung spart 400er
    if (accepted && !code.startsWith(accepted)) {
      alert(`Falscher Präfix: "${code}". Erlaubt: "${accepted}"`);
      return;
    }

    const url = new URL(apiUrl, window.location.origin);
    url.searchParams.set('code', code);
    if (accepted) url.searchParams.set('accepted', accepted);

    console.debug('[SCAN] fetch:', url.toString());

    let res, data;
    try {
      res = await fetch(url.toString(), { method: 'GET' });
      data = await res.json().catch(() => null);
    } catch (e) {
      alert('Netzwerkfehler.');
      return;
    }

    if (!res.ok) {
      alert(data?.error || `Fehler ${res.status}`);
      return;
    }

    if (data?.type === 'unload' && data?.unload_id != null) {
      ensureOption(data.unload_id, data.label || `Einheit #${data.unload_id}`);
    } else {
      alert('Unerwartetes Antwortformat.');
    }
  };

  // Scanner schickt meist Enter → hier abfangen
  input.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter') return;
    e.preventDefault();
    const value = input.value;  // zuerst lesen
    input.value = '';           // dann für nächsten Scan leeren
    scan(value);
  });

  // Fallback: einige Scanner feuern nur 'change'
  input.addEventListener('change', (e) => {
    const value = e.target.value;
    e.target.value = '';
    scan(value);
  });
});