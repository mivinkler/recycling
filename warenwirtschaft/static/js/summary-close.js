document.addEventListener("click", function (event) {
    document.querySelectorAll("details.top-icon-detail[open]").forEach(details => {
    if (!details.contains(event.target)) {
        details.removeAttribute("open");
    }
    }); 
});
