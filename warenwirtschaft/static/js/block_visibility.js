document.addEventListener("DOMContentLoaded", function () {
<<<<<<< HEAD
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
=======
    const toggleButton = document.querySelector(".toggle-button");
    const hiddenBlock = document.querySelector(".hidden-block");
    const iconDetail = document.querySelector(".icon-detail");

    // Открытие/закрытие блока при клике на кнопку
    toggleButton.addEventListener("click", function (event) {
        hiddenBlock.hidden = !hiddenBlock.hidden;
        event.stopPropagation(); // Предотвращаем всплытие события, чтобы клики по кнопке не закрывали блок
    });

    // Закрытие блока, если клик был вне блока
    document.addEventListener("click", function (event) {
        if (!iconDetail.contains(event.target)) {
            hiddenBlock.hidden = true; // Закрыть блок, если клик был не внутри элемента .icon-detail
        }
>>>>>>> b42dd64a0d7b84e1ff64f2c73cf4ab2eab679c50
    });
});