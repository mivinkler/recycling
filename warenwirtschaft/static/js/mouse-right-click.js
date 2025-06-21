document.addEventListener("DOMContentLoaded", () => {
  const menu = createContextMenu();
  document.body.appendChild(menu);

  let currentRow = null;

  document.querySelectorAll(".js-select-row").forEach(row => {
    row.addEventListener("contextmenu", e => {
      e.preventDefault();
      currentRow = row;
      showMenuAt(menu, e.pageX, e.pageY);
    });
  });

  document.addEventListener("click", () => hideMenu(menu));
  document.addEventListener("keydown", e => e.key === "Escape" && hideMenu(menu));

  function createContextMenu() {
    const menu = document.createElement("ul");
    menu.id = "context-menu";
    menu.className = "context-menu";

    const actions = [
      { text: "Detail", key: "url-detail" },
      { text: "Ändern", key: "url-update" },
      { text: "Barcode", key: "url-unit-detail" }
    ];

    actions.forEach(({ text, key }) => {
      const li = document.createElement("li");
      li.textContent = text;
      li.dataset.action = key;
      li.addEventListener("click", () => {
        const url = currentRow?.dataset[toCamel(key)];
        if (url) window.location.href = url;
        hideMenu(menu);
      });
      menu.appendChild(li);
    });

    return menu;
  }

function showMenuAt(menu, x, y) {
  menu.style.top = `${y}px`;
  menu.style.left = `${x}px`;
  menu.style.display = "block";
}

function hideMenu(menu) {
  menu.style.display = "none";
}

function toCamel(str) {
  return str.replace(/-([a-z])/g, (_, char) => char.toUpperCase());
}
});