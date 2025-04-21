document.addEventListener("DOMContentLoaded", function () {
    const rows = document.querySelectorAll(".js-select-row");
    const detailLink = document.getElementById("detail-link");
    const editLink = document.getElementById("edit-link");

    if (!detailLink || !editLink) return;

    let selectedRow = null;

    rows.forEach(row => {
        row.addEventListener("click", () => {
            // Vorherige Auswahl entfernen
            if (selectedRow) {
                selectedRow.classList.remove("row-selected");
            }

            // Neue Auswahl markieren
            selectedRow = row;
            selectedRow.classList.add("row-selected");

            // Links setzen
            const { urlDetail, urlUpdate } = row.dataset;

            if (!urlDetail || !urlUpdate) {
                console.error("Fehler: URL fehlt");
                return;
            }

            detailLink.href = urlDetail;
            editLink.href = urlUpdate;

            detailLink.classList.remove("disabled");
            editLink.classList.remove("disabled");
        });
    });
});
