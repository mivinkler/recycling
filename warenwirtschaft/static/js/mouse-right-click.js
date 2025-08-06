document.addEventListener("DOMContentLoaded", () => {
  // Das Template-Element mit dem Kontextmenü holen
  const template = document.getElementById("context-menu-template");
  if (!template) return;

  // Menü aus dem Template klonen und zum Dokument hinzufügen
  const menu = template.content.firstElementChild.cloneNode(true);
  document.body.appendChild(menu);

  let currentRow = null;        // Aktuell ausgewählte Tabellenzeile
  let hideTimeout = null;       // Timeout zum Ausblenden des Menüs

  // Rechtsklick auf Tabellenzeilen mit Kontextmenü aktivieren
  document.querySelectorAll(".js-select-row").forEach(row => {
    row.addEventListener("contextmenu", e => {
      e.preventDefault();       // Standard-Rechtsklick deaktivieren
      currentRow = row;

      // Nur Menüeinträge anzeigen, wenn die URL vorhanden ist
      menu.querySelectorAll("li").forEach(li => {
        const key = toCamel(li.dataset.action);
        li.style.display = currentRow.dataset[key] ? "block" : "none";
      });

      // Menü an Mausposition anzeigen
      menu.style.top = `${e.pageY}px`;
      menu.style.left = `${e.pageX}px`;
      menu.style.display = "block";
    });
  });

  // Klick auf einen Menüeintrag: zur Ziel-URL weiterleiten
  menu.addEventListener("click", e => {
    const li = e.target.closest("li");
    if (!li || !currentRow) return;

    const key = toCamel(li.dataset.action);
    const url = currentRow.dataset[key];

    if (url) {
      window.location.href = url;
    }

    hideMenu();
  });

  // Wenn Maus das Menü verlässt: Menü nach kurzer Zeit ausblenden
  menu.addEventListener("mouseleave", () => {
    hideTimeout = setTimeout(hideMenu, 1000);
  });

  // Wenn Maus zurück ins Menü kommt: Ausblenden abbrechen
  menu.addEventListener("mouseenter", () => {
    clearTimeout(hideTimeout);
  });

  // Klick außerhalb des Menüs: Menü ausblenden
  document.addEventListener("click", e => {
    if (!menu.contains(e.target)) {
      hideMenu();
    }
  });

  // ESC-Taste: Menü ausblenden
  document.addEventListener("keydown", e => {
    if (e.key === "Escape") {
      hideMenu();
    }
  });

  // Menü ausblenden
  function hideMenu() {
    menu.style.display = "none";
  }

  // Hilfsfunktion: konvertiert kebab-case in camelCase
  function toCamel(str) {
    return str.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
  }
});
