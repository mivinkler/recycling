document.addEventListener('DOMContentLoaded', () => {
  const input   = document.getElementById('barcode');
  const select  = document.querySelector('select[name="delivery_unit"]');
  const imgOn   = document.getElementById('barcode-active');
  const imgOff  = document.getElementById('barcode-inactive');
  const label   = document.querySelector('label[for="barcode"]');
  const apiUrl  = input?.dataset.api || '';

  if (!input || !select || !apiUrl) return;

  // --- helpers ---
  const toggleIcon = (active) => {
    if (imgOn)  imgOn.hidden  = !active;
    if (imgOff) imgOff.hidden =  active;
  };

  const ensureOption = (id, text = `Einheit #${id}`) => {
    let opt = select.querySelector(`option[value="${id}"]`);
    if (!opt) {
      opt = new Option(text, id);
      select.appendChild(opt);
    }
    select.value = String(id);
  };

  const scan = async (code) => {
    const q = code.trim().toUpperCase();
    if (!q) return;
    const res = await fetch(`${apiUrl}?code=${encodeURIComponent(q)}`);
    if (!res.ok) throw new Error('not-found');
    const data = await res.json();
    if (data.type === 'delivery_unit' && data.delivery_unit_id != null) {
      ensureOption(data.delivery_unit_id);
    }
  };

  // --- focus UX ---
  input.focus();
  label?.addEventListener('click', () => input.focus());
  input.addEventListener('focus', () => toggleIcon(true));
  input.addEventListener('blur',  () => toggleIcon(false));

  // --- handle Enter from scanner ---
  input.addEventListener('keydown', async (e) => {
    if (e.key !== 'Enter') return;
    e.preventDefault();
    const value = input.value;
    input.value = ''; // sofort reinigen, um sofort für den nächsten Scan bereit zu sein
    try {
      await scan(value);
    } catch {
      alert('Barcode nicht erkannt oder Fehler beim Verarbeiten.');
    }
  });
});
