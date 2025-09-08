/* 🇩🇪 Einfache Lock/Unlock-Logik ohne "disabled"
   - Alle Zeilen starten gesperrt (.is-locked).
   - Klick auf Schloss öffnet genau diese Zeile, alle anderen bleiben/werden gesperrt.
   - "Gesperrt" bedeutet: keine Interaktion (pointer-events), aber Werte werden im POST gesendet.
*/
(function () {
  "use strict";

  const ROW_SELECTOR = "tr.itemcard-table-row";
  const LOCK_BTN = ".btn.btn-lock";
  const ICON_LOCK_CLOSED = ".icon-lock-closed";
  const ICON_LOCK_OPEN = ".icon-lock-open";

  // 🇩🇪 Aktionszellen (geschlossen/offen) einer Zeile ermitteln
  function getActionCells(row) {
    const closed = row.querySelector(ICON_LOCK_CLOSED)?.closest("td") || null;
    const open   = row.querySelector(ICON_LOCK_OPEN)?.closest("td") || null;
    return { closed, open };
  }

  // 🇩🇪 Zeile sperren (keine Bearbeitung, aber alles wird gesendet)
  function lockRow(row) {
    row.classList.add("is-locked");
    const { closed, open } = getActionCells(row);
    if (closed) closed.hidden = false;
    if (open)   open.hidden = true;

    // Checkbox in der ersten Spalte abwählen (falls vorhanden)
    const cb = row.querySelector('td input[type="checkbox"]');
    if (cb) cb.checked = false;
  }

  // 🇩🇪 Zeile entsperren (Bearbeitung zulassen)
  function unlockRow(row) {
    row.classList.remove("is-locked");
    const { closed, open } = getActionCells(row);
    if (closed) closed.hidden = true;
    if (open)   open.hidden = false;

    // Checkbox der aktiven Zeile markieren
    const cb = row.querySelector('td input[type="checkbox"]');
    if (cb) cb.checked = true;

    // Fokus auf erstes sinnvolles Eingabefeld setzen
    const focusEl =
      row.querySelector('input[type="number"]') ||
      row.querySelector('input[type="text"]')   ||
      row.querySelector("select")               ||
      row.querySelector("textarea");
    if (focusEl) { try { focusEl.focus(); if (focusEl.select) focusEl.select(); } catch(_){} }
  }

  // 🇩🇪 Initial: alle Zeilen sperren
  function initLocked() {
    document.querySelectorAll(ROW_SELECTOR).forEach(lockRow);
  }

  // 🇩🇪 Delegierter Klick-Handler für Lock-Buttons
  function onClick(e) {
    const btn = e.target.closest(LOCK_BTN);
    if (!btn) return;

    const row = btn.closest(ROW_SELECTOR);
    if (!row) return;

    // Wenn die Zeile aktuell gesperrt ist -> nur diese entsperren, alle anderen sperren
    const rows = Array.from(document.querySelectorAll(ROW_SELECTOR));
    const willOpen = row.classList.contains("is-locked");

    rows.forEach(r => (r === row && willOpen) ? unlockRow(r) : lockRow(r));
  }

  // 🇩🇪 Start
  function init() {
    initLocked();
    document.addEventListener("click", onClick, { passive: true });
  }

  (document.readyState === "loading")
    ? document.addEventListener("DOMContentLoaded", init)
    : init();
})();

