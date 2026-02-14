
// (function () {
//   "use strict";

//   const ROW_SELECTOR = "tr.itemcard-table-row";
//   const LOCK_BTN = ".btn.btn-lock";
//   const ICON_LOCK_CLOSED = ".icon-lock-closed";
//   const ICON_LOCK_OPEN   = ".icon-lock-open";

//   function getActionCells(row) {
//     const closed = row.querySelector(ICON_LOCK_CLOSED)?.closest("td") || null;
//     const open   = row.querySelector(ICON_LOCK_OPEN)?.closest("td")   || null;
//     return { closed, open };
//   }

//   function setLocked(row, locked) {
//     row.classList.toggle("is-locked", locked);
//     const { closed, open } = getActionCells(row);
//     if (closed) closed.hidden = !locked; 
//     if (open)   open.hidden   = locked;  
//   }

//   function setRowCheckbox(row, value, { force = false } = {}) {
//     const cb = row.querySelector('td input[type="checkbox"]');
//     if (!cb) return;
//     const isInitial = row.dataset.initialChecked === "1";
//     if (isInitial && value === false && !force) return;
//     cb.checked = !!value;
//   }

//   function initFromDOM() {
//     const rows = document.querySelectorAll(ROW_SELECTOR);
//     rows.forEach(row => {
//       const kind = row.dataset.kind; 
//       const cb = row.querySelector('td input[type="checkbox"]');
//       const serverChecked = !!(cb && cb.checked);

//       if (kind === "new") {
//         row.dataset.initialChecked = "0"; 
//         setLocked(row, false); 
//       } else {
//         row.dataset.initialChecked = serverChecked ? "1" : "0";
//         setLocked(row, true);             
//       }
//     });
//   }

//   function toggleByLock(row) {
//     const willOpen = row.classList.contains("is-locked");
//     const rows = Array.from(document.querySelectorAll(ROW_SELECTOR));

//     rows.forEach(r => setLocked(r, true));

//     if (willOpen) {
//       setLocked(row, false);
//       setRowCheckbox(row, true);
//       rows.forEach(r => { if (r !== row) setRowCheckbox(r, false); });
//     } else {
//       setLocked(row, true);

//     }
//   }

//   function onCheckboxChange(e) {
//     const cb = e.target;
//     if (!cb.matches('input[type="checkbox"]')) return;

//     const row = cb.closest(ROW_SELECTOR);
//     if (!row) return;

//     document.querySelectorAll(ROW_SELECTOR).forEach(r => setLocked(r, r !== row));
//     setLocked(row, false);
//   }

//   function onClick(e) {
//     const btn = e.target.closest(LOCK_BTN);
//     if (!btn) return;
//     const row = btn.closest(ROW_SELECTOR);
//     if (!row) return;
//     toggleByLock(row);
//   }

//   function init() {
//     initFromDOM();
//     document.addEventListener("click", onClick, { passive: true });
//     document.addEventListener("change", onCheckboxChange, { passive: true });
//   }

//   (document.readyState === "loading")
//     ? document.addEventListener("DOMContentLoaded", init)
//     : init();
// })();
