document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".navi-icon-js").forEach((iconDetail) => {
        const toggleButton = iconDetail.querySelector(".toggle-button");
        const hiddenBlock = iconDetail.querySelector(".hidden-block");

        toggleButton.addEventListener("click", function (event) {
            // Alle anderen Blöcke werden geschlossen, wenn ein neuer Block aufgemacht wird
            document.querySelectorAll(".hidden-block").forEach((block) => {
                if (block !== hiddenBlock) {
                    block.hidden = true;
                }
            });

            // Prüft, ob der Block ausgeblendet ist
            hiddenBlock.hidden = !hiddenBlock.hidden;
            // "stopPropagation()" - verhindert, dass der Block schließt, wenn darauf klicken
            event.stopPropagation();
        });

        // Schließen eines Blocks, wenn außerhalb ihm geklickt wird
        document.addEventListener("click", function (event) {
            if (!iconDetail.contains(event.target)) {
                hiddenBlock.hidden = true;
            }
        });
    });
});