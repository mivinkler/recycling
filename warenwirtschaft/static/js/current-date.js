document.addEventListener("DOMContentLoaded", function() {
    let dateStart = new Date();
    dateStart.setMonth(dateStart.getMonth() - 1);

    // YYYY-MM-DD
    const formatDate = date => date.toISOString().split('T')[0]; 

    const dateStartInput = document.getElementById("dateStart");
    const dateEndInput = document.getElementById("dateEnd");

    dateStartInput.value = formatDate(dateStart);
    dateEndInput.value = formatDate(new Date());

});
