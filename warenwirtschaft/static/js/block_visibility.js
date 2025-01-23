document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.querySelector(".toggle-button");
    const hiddenBlock = document.querySelector(".hidden-block");

    toggleButton.addEventListener("click", function () {
        hiddenBlock.hidden = !hiddenBlock.hidden;
    });
});