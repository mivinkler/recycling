document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll(".selectable-row").forEach(row => {
        row.addEventListener("mouseover", function() {
            let deliveryId = this.getAttribute("data-id");
            document.querySelectorAll(`[data-id='${deliveryId}']`).forEach(el => {
                el.classList.add("row-selected");
            });
        });

        row.addEventListener("mouseout", function() {
            let deliveryId = this.getAttribute("data-id");
            document.querySelectorAll(`[data-id='${deliveryId}']`).forEach(el => {
                el.classList.remove("row-selected");
            });
        });
    });
});