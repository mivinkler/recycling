/* 🇩🇪 Lock/Unlock-Logik mit respektierter Server-Auswahl:
   - "Neue Wagen" (einzige new-Zeile) beim Laden offen.
   - "Existing": beim Laden gesperrt; Checkboxen, die vom Server checked kamen, sind "geschützt".
   - Klick aufs Schloss:
       * geklickte Zeile exklusiv öffnen,
       * ihre Checkbox beim Öffnen setzen (checked=true),
       * andere Zeilen visuell sperren, deren Checkboxen nur abwählen, wenn sie NICHT initial geschützt sind,
       * beim Schließen der geklickten Zeile Checkbox NICHT automatisch ändern (Benutzer entscheidet manuell).
   - Manueller Klick auf Checkbox:
       * öffnet/schließt nur die eigene Zeile; erlaubt auch das Abwählen eines initial geschützten Kästchens.
*/
(function () {
  "use strict";

  const ROW_SELECTOR = "tr.itemcard-table-row";
  const LOCK_BTN = ".btn.btn-lock";
  const ICON_LOCK_CLOSED = ".icon-lock-closed";
  const ICON_LOCK_OPEN   = ".icon-lock-open";

  function getActionCells(row) {
    const closed = row.querySelector(ICON_LOCK_CLOSED)?.closest("td") || null;
    const open   = row.querySelector(ICON_LOCK_OPEN)?.closest("td")   || null;
    return { closed, open };
  }

  function setLocked(row, locked) {
    row.classList.toggle("is-locked", locked);
    const { closed, open } = getActionCells(row);
    if (closed) closed.hidden = !locked; // geschlossenes Icon nur bei locked
    if (open)   open.hidden   = locked;  // offenes Icon nur bei unlocked
  }

  // 🇩🇪 Checkbox setzen; initial geschützte nur dann abwählen, wenn force=true
  function setRowCheckbox(row, value, { force = false } = {}) {
    const cb = row.querySelector('td input[type="checkbox"]');
    if (!cb) return;
    const isInitial = row.dataset.initialChecked === "1";
    if (isInitial && value === false && !force) return;
    cb.checked = !!value;
  }

  function initFromDOM() {
    const rows = document.querySelectorAll(ROW_SELECTOR);
    rows.forEach(row => {
      const kind = row.dataset.kind; // "new" | "existing"
      const cb = row.querySelector('td input[type="checkbox"]');
      const serverChecked = !!(cb && cb.checked);

      if (kind === "new") {
        row.dataset.initialChecked = "0"; // nicht geschützt
        setLocked(row, false);            // Neue Wagen offen anzeigen
        // Wenn du neue Zeile auch vorselektieren willst:
        // setRowCheckbox(row, true);
      } else {
        row.dataset.initialChecked = serverChecked ? "1" : "0";
        setLocked(row, true);             // Existing initial gesperrt anzeigen
      }
    });
  }

  function toggleByLock(row) {
    const willOpen = row.classList.contains("is-locked"); // wenn gesperrt -> öffnen
    const rows = Array.from(document.querySelectorAll(ROW_SELECTOR));

    // alle visuell sperren
    rows.forEach(r => setLocked(r, true));

    if (willOpen) {
      // geklickte öffnen + Checkbox setzen
      setLocked(row, false);
      setRowCheckbox(row, true);
      // andere abwählen, aber initial geschützte in Ruhe lassen
      rows.forEach(r => { if (r !== row) setRowCheckbox(r, false); });
    } else {
      // geklickte schließen, Checkbox NICHT automatisch ändern:
      // Benutzer kann sie manuell abwählen, um die Verknüpfung zu entfernen.
      setLocked(row, true);

      // 👉 Если хочешь также автовыключать при закрытии — раскомментируй:
      // setRowCheckbox(row, false, { force: true });
    }
  }

  function onCheckboxChange(e) {
    const cb = e.target;
    if (!cb.matches('input[type="checkbox"]')) return;

    const row = cb.closest(ROW_SELECTOR);
    if (!row) return;

    // 🇩🇪 Exklusiv öffnen – unabhängig davon, ob checked oder nicht
    document.querySelectorAll(ROW_SELECTOR).forEach(r => setLocked(r, r !== row));
    setLocked(row, false);

    // 🇩🇪 WICHTIG: Checkbox-Zustand nicht anfassen – Nutzer hat ihn gerade gesetzt.
    //             (Damit kann man auch eine "initial geschützte" abwählen und speichern.)
  }

  function onClick(e) {
    const btn = e.target.closest(LOCK_BTN);
    if (!btn) return;
    const row = btn.closest(ROW_SELECTOR);
    if (!row) return;
    toggleByLock(row);
  }

  function init() {
    initFromDOM();
    document.addEventListener("click", onClick, { passive: true });
    document.addEventListener("change", onCheckboxChange, { passive: true });
  }

  (document.readyState === "loading")
    ? document.addEventListener("DOMContentLoaded", init)
    : init();
})();
