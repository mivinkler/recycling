document.addEventListener('DOMContentLoaded', () => {
    const itemCounter = document.getElementById('item-counter');
    const itemWrapper = document.getElementById('item-wrapper');
    const firstRow = itemWrapper.children[0];

    // Zeilen aktualisieren, wenn sich der Zähler ändert
    itemCounter.addEventListener('input', () => {
        updateRows(+itemCounter.value || 1);
    });

    function updateRows(count) {
        // löscht zusätzliche Zeilen, wenn mehr davon als nötig
        while (itemWrapper.children.length > count) {
            itemWrapper.lastChild.remove();
        }

        // Fehlende Zeilen hinzufügen
        while (itemWrapper.children.length < count) {
            const clone = firstRow.cloneNode(true);
            const index = itemWrapper.children.length;

            // Attribute für neue Zeile aktualisieren
            updateAttributes(clone, index);

            // Zeilennummer einfügen
            clone.querySelector('.item-number').textContent = index + 1;

            itemWrapper.appendChild(clone);
        }
    }
    // Anfangsanzahl 1
    updateRows(+itemCounter.value || 1);

    function updateAttributes(row, index) {
        row.querySelectorAll('[id], [name]').forEach((el) => {
            if (el.id) el.id = el.id.replace(/-\d+/, `-${index}`);
            if (el.name) el.name = el.name.replace(/-\d+/, `-${index}`);            
        });
    }
});
