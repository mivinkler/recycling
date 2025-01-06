document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.querySelector(".table-search");
    const filterForm = document.querySelector(".table-filter");

    toggleButton.addEventListener("click", function () {
        filterForm.hidden = !filterForm.hidden;
    });
});