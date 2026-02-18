// Ein Scanner-Eingabefeld (#barcode) für G / S / A
document.addEventListener('DOMContentLoaded', () => {
  const barcodeInput = document.getElementById('barcode');
   const imgActive    = document.getElementById('barcode-active');
  const imgInactive  = document.getElementById('barcode-inactive');

  if (!barcodeInput) return;

  // Icons für aktiven/inaktiven Scan-Eingabefokus
  const setState = (active) => {
    if (imgActive)   imgActive.hidden   = !active;
    if (imgInactive) imgInactive.hidden =  active;
  };
  barcodeInput.addEventListener('focus', () => setState(true));
  barcodeInput.addEventListener('blur',  () => setState(false));

  const api = barcodeInput.dataset.api;
  const $  = (id) => document.getElementById(id);

  // Kopf-Felder
  const fld = {
    customer:   $('id_customer'),
    certificate:$('id_certificate'),
    transport:  $('id_transport'),
    note:       $('id_note'),
  };

  const setSelect = (sel, value) => { if (!sel || value == null) return; sel.value = String(value); sel.dispatchEvent(new Event('change',{bubbles:true})); };
  const setInput  = (inp, value) => { if (!inp || value == null) return; inp.value = String(value);  inp.dispatchEvent(new Event('change',{bubbles:true})); };

  const getCb = (name, id) => document.querySelector(`input[name="${name}"][value="${id}"]`);
  const flashRow = (cb) => { const tr = cb?.closest('tr'); if (!tr) return; tr.classList.add('scan-hit'); setTimeout(()=>tr.classList.remove('scan-hit'),800); tr.scrollIntoView({behavior:'smooth',block:'center'}); };

  const fetchApi = async (code) => {
    const res  = await fetch(`${api}?barcode=${encodeURIComponent(code)}`);
    const data = await res.json().catch(() => null);
    return { ok: res.ok, status: res.status, data };
  };

  const handle = async (raw) => {
    const code = String(raw || '').trim().toUpperCase();
    if (!code) return;

    const pfx = code[0];

    if (pfx === 'G') {
      const { ok, status, data } = await fetchApi(code);
      if (!ok) { alert(data?.error || `Fehler ${status}`); return; }
      setSelect(fld.customer,    data.customer_id);
      setInput (fld.certificate, data.certificate);
      setSelect(fld.transport,   data.transport);
      setInput (fld.note,        data.note);
      return;
    }

    if (pfx === 'S' || pfx === 'A') {
      const { ok, status, data } = await fetchApi(code);
      if (!ok) { alert(data?.error || `Fehler ${status}`); return; }
      if (data.type === 'unload') {
        const cb = getCb('selected_unload', String(data.id ?? data.unload_id));
        if (cb) { cb.checked = true; flashRow(cb); } else { alert('Gefundene Vorsortierung ist nicht in der Liste.'); }
      } else if (data.type === 'recycling') {
        const cb = getCb('selected_recycling', String(data.id ?? data.recycling_id));
        if (cb) { cb.checked = true; flashRow(cb); } else { alert('Gefundene Zerlegung ist nicht in der Liste.'); }
      } else {
        alert('Unerwartetes Antwortformat.');
      }
      return;
    }

    alert('Unbekannter Präfix. Erlaubt: G (Kopf), S/A (Liste).');
  };

  barcodeInput.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter' && e.key !== 'Tab') return;
    e.preventDefault();                    // verhindert Default (z.B. Form-Submit/Focus-Wechsel)
    const v = barcodeInput.value;
    barcodeInput.value = '';
    handle(v);                             // G → Kopf, S/A → Checkboxen
  });

  // Verhindere Formular-Submit, solange der Scanner fokussiert ist
  const form = barcodeInput.closest('form');
  if (form) {
    form.addEventListener('submit', (e) => {
      if (document.activeElement === barcodeInput) e.preventDefault();
    });
  }
});
