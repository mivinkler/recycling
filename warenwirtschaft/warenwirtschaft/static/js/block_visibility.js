document.addEventListener("DOMContentLoaded", function () {
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
    });
});