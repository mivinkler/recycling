// static/js/barcode/barcode-unload.js

document.addEventListener('DOMContentLoaded', () => {
  // --- Referenzen auf DOM-Elemente holen ---
  const input   = document.getElementById('barcode');              // verstecktes Barcode-Eingabefeld
  const select  = document.getElementById('id_delivery_unit');     // Ziel-Select (Wareneingang)
  const imgOn   = document.getElementById('barcode-active');       // Icon: Scanner aktiv
  const imgOff  = document.getElementById('barcode-inactive');     // Icon: Scanner inaktiv
  const label   = document.querySelector('label[for="barcode"]');  // Icon-Wrapper
  const apiUrl  = input?.dataset.api || '';                        // API-URL aus data-api
  const acceptedPrefix = (input?.dataset.accepted || '').toUpperCase(); // z.B. "L"

  // --- Grundvalidierung ---
  if (!input)  { console.warn('[SCAN] #barcode nicht gefunden'); return; }
  if (!select) { console.warn('[SCAN] #id_delivery_unit nicht gefunden'); return; }
  if (!apiUrl) { console.warn('[SCAN] data-api am #barcode fehlt'); return; }

  // === Hilfsfunktionen ======================================================

  /**
   * Icon-Zustand setzen (aktiv/inaktiv).
   * active = true  → "aktives" Icon anzeigen
   * active = false → "inaktives" Icon anzeigen
   */
  const toggleIcon = (active) => {
    if (imgOn)  imgOn.hidden  = !active;
    if (imgOff) imgOff.hidden =  active;
  };

  /**
   * Option im Select sicherstellen und auswählen.
   * Falls die Option noch nicht existiert, wird sie angelegt.
   */
  const ensureOption = (id, text = `Einheit #${id}`) => {
    let opt = select.querySelector(`option[value="${id}"]`);
    if (!opt) {
      opt = new Option(text, String(id));
      select.add(opt);
    }
    select.value = String(id);

    // Optional: Formular automatisch abschicken, um Seite neu zu laden
    const form = document.getElementById('du-select-form');
    if (form) form.submit();
  };

  /**
   * Roh-Barcode aufbereiten:
   * - Whitespace entfernen
   * - Großschreibung erzwingen
   */
  const normalize = (raw) => (raw || '').toUpperCase().trim();

  /**
   * Hauptfunktion: Barcode scannen, API aufrufen, Select setzen.
   */
  const scan = async (rawCode) => {
    const code = normalize(rawCode);
    if (!code) {
      console.warn('[SCAN] leerer Code, Scan wird ignoriert');
      return;
    }

    // Optionaler Präfix-Check (z.B. "L" für Unload)
    if (acceptedPrefix && !code.startsWith(acceptedPrefix)) {
      alert(`Falscher Präfix: "${code}". Erlaubt: "${acceptedPrefix}"`);
      return;
    }

    // URL robust aufbauen
    const url = new URL(apiUrl, window.location.origin);
    url.searchParams.set('code', code);

    let res;
    try {
      res = await fetch(url.toString(), { method: 'GET' });
    } catch (err) {
      console.error('[SCAN] Netzwerkfehler:', err);
      alert('Netzwerkfehler beim Scannen des Barcodes.');
      return;
    }

    if (!res.ok) {
      console.warn('[SCAN] API antwortete mit Status', res.status);
      let data = null;
      try {
        data = await res.json();
      } catch {
        // ignorieren, wir haben bereits den Statuscode
      }
      alert(data?.error || `Fehler beim Barcode-Scan (Status ${res.status}).`);
      return;
    }

    // Erwartetes JSON lesen
    let data;
    try {
      data = await res.json();
    } catch (err) {
      console.error('[SCAN] Ungültiges JSON', err);
      alert('Unerwartete Antwort vom Server (kein gültiges JSON).');
      return;
    }

    // Erwartetes Format:
    // { type: "delivery_unit", delivery_unit_id: <int>, label?: <string> }
    if (data?.type === 'delivery_unit' && data?.delivery_unit_id != null) {
      const text = data.label || `Einheit #${data.delivery_unit_id}`;
      ensureOption(data.delivery_unit_id, text);
    } else {
      console.warn('[SCAN] Unerwartetes Antwortformat', data);
      alert('Barcode wurde erkannt, aber die Antwort hat ein unerwartetes Format.');
    }
  };

  // === Fokus / UX für Icon & Scanner ========================================

  // Klick auf das Icon → Fokus ins versteckte Barcode-Feld setzen
  if (label) {
    label.addEventListener('click', () => {
      // Kommentar: Benutzer klickt auf das Icon → Scanner-Eingabefeld fokussieren
      input.focus();
    });
  }

  // Wenn das Barcode-Feld den Fokus bekommt, Icon "aktiv" anzeigen
  input.addEventListener('focus', () => {
    // Kommentar: Scanner-Feld hat Fokus → aktives Icon einblenden
    toggleIcon(true);
  });

  // Wenn der Fokus das Feld verlässt (Benutzer klickt in ein anderes Feld),
  // Icon wieder "inaktiv" anzeigen
  input.addEventListener('blur', () => {
    // Kommentar: Scanner-Feld verliert Fokus → inaktives Icon einblenden
    toggleIcon(false);
  });

  // Initialzustand beim Laden (wegen autofocus meistens true)
  toggleIcon(document.activeElement === input);

  // === Tastatur-Handling (Scanner sendet meistens Enter) =====================

  input.addEventListener('keydown', async (e) => {
    if (e.key !== 'Enter') return;

    // Verhindern, dass Enter das Formular direkt abschickt
    e.preventDefault();

    // Wert sichern und Feld leeren, damit der nächste Scan sauber startet
    const value = input.value;
    input.value = '';

    try {
      await scan(value);
      // Kommentar: Fokus kann nach erfolgreichem Scan im Feld bleiben,
      // damit der nächste Scan ohne zusätzlichen Klick möglich ist.
    } catch (err) {
      console.error('[SCAN] Fehler beim Scan:', err);
      alert('Barcode nicht erkannt oder Fehler beim Verarbeiten.');
    }
  });

  // Optionaler Fallback: einige Scanner feuern ein "change"-Event
  input.addEventListener('change', (e) => {
    const value = e.target.value;
    e.target.value = '';
    scan(value).catch((err) => {
      console.error('[SCAN] Fehler beim Scan (change):', err);
      alert('Barcode nicht erkannt oder Fehler beim Verarbeiten.');
    });
  });
});
