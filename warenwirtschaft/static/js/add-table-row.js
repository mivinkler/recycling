document.addEventListener('DOMContentLoaded', function () {
    const addButton = document.getElementById('form-add-btn');
    const removeButton = document.getElementById('form-remove-btn');
    const tableBody = document.querySelector('.add-row-js');
    const template = document.getElementById('table-row-template').innerHTML;
    const totalFormsInput = document.querySelector('input[name$="-TOTAL_FORMS"]');

    addButton.addEventListener('click', function () {
        const formIndex = +totalFormsInput.value;
        const existingRowCount = tableBody.querySelectorAll('.table-row-id').length;

        const newRowHtml = template
            .replace(/__prefix__/g, formIndex)
            .replace(/__index__/g, existingRowCount + 1);

        tableBody.insertAdjacentHTML('beforeend', newRowHtml);
        totalFormsInput.value = formIndex + 1;
    });

    removeButton.addEventListener('click', function () {
        const currentFormCount = +totalFormsInput.value;

        if (currentFormCount > 0) {
            const rows = tableBody.querySelectorAll('.table-row');
            if (rows.length > 0) {
                const lastRow = rows[rows.length - 1];
                if (!lastRow.querySelector('input[type="checkbox"]')) {
                    lastRow.remove();
                    totalFormsInput.value = currentFormCount - 1;
                }
            }
        }
    });
});
