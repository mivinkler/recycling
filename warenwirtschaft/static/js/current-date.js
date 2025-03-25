let dateStart = new Date();
dateStart.setMonth(dateStart.getMonth() - 1);

document.getElementById("dateStart").valueAsDate = dateStart;
document.getElementById("dateEnd").valueAsDate = new Date();