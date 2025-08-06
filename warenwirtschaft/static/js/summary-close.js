document.addEventListener("click", function (event) {
    document.querySelectorAll("details.header-details[open]").forEach(details => {
    if (!details.contains(event.target)) {
        details.removeAttribute("open");
    }
    }); 
});
