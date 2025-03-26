document.addEventListener("DOMContentLoaded", function () {
    let selectedRow = null;
    let detailLink = document.getElementById("detail-link");
    let editLink = document.getElementById("edit-link");

    document.querySelectorAll(".selectable-row").forEach(row => {
        row.addEventListener("click", function () {
            if (selectedRow) {
                selectedRow.classList.remove("row-selected");
                selectedRow.querySelector("input[type='radio']").checked = false;
            }

            selectedRow = this;
            selectedRow.classList.add("row-selected");

            let radio = selectedRow.querySelector("input[type='radio']");
            if (radio) {
                radio.checked = true;
            }

            let detailUrl = selectedRow.dataset.urlDetail;
            let editUrl = selectedRow.dataset.urlUpdate;

            if (!detailUrl || !editUrl) {
                console.error("Ошибка: отсутствует URL");
                return;
            }

            detailLink.href = detailUrl;
            editLink.href = editUrl;

            detailLink.classList.remove("disabled");
            editLink.classList.remove("disabled");
        });
    });
});
