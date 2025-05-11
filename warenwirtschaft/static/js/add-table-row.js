document.addEventListener('DOMContentLoaded', function () {
    const addButton = document.getElementById('add-form-btn');
    const tableBody = document.querySelector('.table');
    const template = document.getElementById('table-row-template').innerHTML;
    const totalFormsInput = document.querySelector('input[name$="-TOTAL_FORMS"]');
    const prefix = totalFormsInput.name.replace('-TOTAL_FORMS', '');

    addButton.addEventListener('click', function () {
        const formIndex = +totalFormsInput.value;
        const newRowHtml = template
        .replace(/__prefix__/g, formIndex)
        .replace(/__index__/g, formIndex + 1);

        tableBody.insertAdjacentHTML('beforeend', newRowHtml);
        totalFormsInput.value = formIndex + 1;
    });
});
