// Kontextmenü mit optionaler Parameter-Übergabe (?delivery_unit=ROW_ID)
document.addEventListener('DOMContentLoaded', () => {
  const tpl = document.getElementById('context-menu-template');
  if (!tpl) return;

  document.getElementById('context-menu')?.remove();
  const menu = tpl.content.firstElementChild.cloneNode(true);
  document.body.appendChild(menu);

  let row = null;

  const hide = () => { menu.classList.remove('is-open'); row = null; };

  // Hilfsfunktion: Query-Parameter setzen (bewahrt vorhandene Parameter)
  const withParam = (url, key, val) => {
    const u = new URL(url, location.origin);
    u.searchParams.set(key, val);
    return u.pathname + u.search + u.hash;
  };

  const show = (r, x, y) => {
    // Sichtbarkeit nach Status
    const st = r.dataset.status;
    menu.querySelectorAll('li').forEach(li => {
      const need = li.dataset.requireStatus;
      li.hidden = need && need !== st;
    });

    menu.classList.add('is-open');
    const { width, height } = menu.getBoundingClientRect();
    const vw = document.documentElement.clientWidth;
    const vh = document.documentElement.clientHeight;
    menu.style.left = `${Math.min(x, vw - width - 8) + window.scrollX}px`;
    menu.style.top  = `${Math.min(y, vh - height - 8) + window.scrollY}px`;
  };

  // Rechtsklick auf Zeile -> Menü
  document.addEventListener('contextmenu', e => {
    const r = e.target.closest('.js-select-row');
    if (!r) return;
    e.preventDefault();
    row = r;
    show(r, e.clientX, e.clientY);
  });

  // Klick auf Eintrag -> ggf. Parameter anhängen -> Navigieren
  menu.addEventListener('click', e => {
    const li = e.target.closest('li');
    if (!li || !row) return;

    const key = li.dataset.action;   // z.B. "urlNextstepCreate"
    let url   = row.dataset[key];    // z.B. "/pfad/zur/ansicht/"
    if (!url) return;

    // Falls data-param gesetzt ist, hänge ?<name>=<row-id> an
    const paramName = li.dataset.param; // z.B. "delivery_unit" oder "unit_id"
    if (paramName) {
      const idVal = row.dataset.id;     // Wert aus data-id der Zeile
      if (idVal) url = withParam(url, paramName, idVal);
    }

    location.href = url;
    hide();
  });

  // Außenklick / ESC -> schließen
  document.addEventListener('mousedown', e => { if (!menu.contains(e.target)) hide(); });
  document.addEventListener('keydown',   e => { if (e.key === 'Escape') hide(); });
  menu.addEventListener('contextmenu', e => e.preventDefault());
});
