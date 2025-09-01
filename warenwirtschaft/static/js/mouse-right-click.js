document.addEventListener("DOMContentLoaded", () => {
  const tpl = document.getElementById("context-menu-template");
  if (!tpl) return;

  document.getElementById("context-menu")?.remove();

  const menu = tpl.content.firstElementChild.cloneNode(true);
  document.body.appendChild(menu);

  if (!menu.querySelector('li[data-action="url-unload-create"]')) {
    const li = document.createElement("li");
    li.dataset.action = "url-unload-create";
    li.dataset.requireStatus = "1";
    li.textContent = "In Vorsortierung übergeben";
    menu.appendChild(li);
  }

  let currentRow = null;
  let hideTimer = null;
  const toCamel = s => s.replace(/-([a-z])/g, (_, c) => c.toUpperCase());

  const hideMenu = () => {
    clearTimeout(hideTimer);
    menu.style.display = "none";
    currentRow = null;
  };

  function showMenu(row, x, y) {
    menu.querySelectorAll("li").forEach(li => {
      const k = toCamel(li.dataset.action || "");
      const need = li.dataset.requireStatus;
      const ok = !!row.dataset[k] && (!need || row.dataset.status === need);
      li.style.display = ok ? "block" : "none";
    });

    menu.style.display = "block";
    const r = menu.getBoundingClientRect();
    const vw = document.documentElement.clientWidth;
    const vh = document.documentElement.clientHeight;
    let left = x, top = y;
    if (left + r.width > vw) left = vw - r.width - 8;
    if (top + r.height > vh) top = vh - r.height - 8;
    if (left < 0) left = 0;
    if (top < 0) top = 0;
    menu.style.left = `${left + window.scrollX}px`;
    menu.style.top = `${top + window.scrollY}px`;

    clearTimeout(hideTimer);
    hideTimer = setTimeout(hideMenu, 3000); // in 3 sek wird geschlossen
  }

  document.addEventListener("contextmenu", e => {
    const row = e.target.closest(".js-select-row");
    if (!row) return;
    e.preventDefault();
    currentRow = row;
    showMenu(row, e.clientX, e.clientY);
  });

  menu.addEventListener("click", e => {
    const li = e.target.closest("li");
    if (!li || !currentRow) return;
    const url = currentRow.dataset[toCamel(li.dataset.action || "")];
    if (url) window.location.href = url;
    hideMenu();
  });

  document.addEventListener("mousedown", e => {
    if (!menu.contains(e.target)) hideMenu();
  });

  document.addEventListener("keydown", e => {
    if (e.key === "Escape") hideMenu();
  });

  menu.addEventListener("contextmenu", e => e.preventDefault());
});
