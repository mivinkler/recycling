// 🇩🇪 Minimalistische Lock/Unlock-Logik für beide Tabellen
// - Alle Zeilen starten gesperrt (per Init).
// - Klick auf Schloss öffnet genau diese Zeile, schließt alle anderen.
// - Beim Öffnen wird der Zeilen-Checkbox gesetzt (checked) und bei anderen entfernt.
// - Solange gesperrt: alle Eingaben disabled (keine Änderungen möglich).
(function () {
  "use strict";

  const ROW = "tr.itemcard-table-row";
  const BTN_LOCK = ".btn.btn-lock";
  const ICON_LOCK_CLOSED = ".icon-lock-closed";
  const ICON_LOCK_OPEN = ".icon-lock-open";

  // 🇩🇪 Hilfen: geschlossene/ offene Aktionszelle der Zeile finden
  function getCells(row) {
    const closed = row.querySelector(ICON_LOCK_CLOSED)?.closest("td");
    const open   = row.querySelector(ICON_LOCK_OPEN)?.closest("td");
    return { closedCell: closed || null, openCell: open || null };
  }

  // 🇩🇪 Alle Formular-Controls einer Zeile (außer den Lock-Buttons) sammeln
  function getControls(row) {
    const all = row.querySelectorAll("input, select, textarea, button");
    return [...all].filter(el => {
      // Lock-Buttons bleiben immer bedienbar
      if (el.closest(".itemcard-action") && el.matches(BTN_LOCK)) return false;
      return true;
    });
  }

  // 🇩🇪 Zeile sperren: offene Aktionszelle verbergen, geschlossene zeigen, Controls deaktivieren
  function lockRow(row) {
    const { closedCell, openCell } = getCells(row);
    if (closedCell) closedCell.hidden = false;
    if (openCell)   openCell.hidden = true;

    getControls(row).forEach(el => {
      // Inputs/Selects komplett sperren
      el.disabled = true;
      if ("readOnly" in el) el.readOnly = true;
      el.setAttribute("aria-disabled", "true");
      el.tabIndex = -1;
    });
  }

  // 🇩🇪 Zeile entsperren: geschlossene Aktionszelle verbergen, offene zeigen, Controls aktivieren
  function unlockRow(row) {
    const { closedCell, openCell } = getCells(row);
    if (closedCell) closedCell.hidden = true;
    if (openCell)   openCell.hidden = false;

    getControls(row).forEach(el => {
      el.disabled = false;
      if ("readOnly" in el) el.readOnly = false;
      el.removeAttribute("aria-disabled");
      el.removeAttribute("tabindex");
    });
  }

  // 🇩🇪 Checkbox der Zeile (erste Spalte) finden
  function getRowCheckbox(row) {
    return row.querySelector('td input[type="checkbox"]');
  }

  // 🇩🇪 Initial: alle Zeilen sperren, offene Blöcke verstecken
  function initLockedState() {
    document.querySelectorAll(ROW).forEach(lockRow);
  }

  // 🇩🇪 Klick-Handler: nur eine Zeile offen, Checkbox dieser Zeile aktiv
  function onClick(e) {
    const btn = e.target.closest(BTN_LOCK);
    if (!btn) return;

    const row = btn.closest(ROW);
    if (!row) return;

    const rows = [...document.querySelectorAll(ROW)];

    // 1) Alle anderen schließen + Checkboxen entfernen
    rows.forEach(r => {
      if (r !== row) {
        lockRow(r);
        const cb = getRowCheckbox(r);
        if (cb) cb.checked = false;
      }
    });

    // 2) Aktuelle Zeile toggeln
    const { closedCell, openCell } = getCells(row);
    const isLockedNow = !openCell || openCell.hidden === true; // offen = openCell sichtbar

    if (isLockedNow) {
      unlockRow(row);
      // Checkbox setzen
      const cb = getRowCheckbox(row);
      if (cb) cb.checked = true;
      // Optional: ersten sinnvollen Input fokussieren
      const focusEl =
        row.querySelector('input[type="number"]:not([disabled])') ||
        row.querySelector('input[type="text"]:not([disabled])') ||
        row.querySelector("select:not([disabled])") ||
        row.querySelector("textarea:not([disabled])");
      if (focusEl) {
        focusEl.focus({ preventScroll: false });
        if (focusEl.select) { try { focusEl.select(); } catch(_) {} }
      }
    } else {
      // war offen -> wieder schließen + Checkbox dieser Zeile entfernen
      lockRow(row);
      const cb = getRowCheckbox(row);
      if (cb) cb.checked = false;
    }
  }

  function init() {
    initLockedState();
    document.addEventListener("click", onClick, { passive: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
