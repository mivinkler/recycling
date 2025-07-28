document.addEventListener('DOMContentLoaded', function () {
  const addButton = document.getElementById('form-add-btn');
  const removeButton = document.getElementById('form-remove-btn');
  const tableBody = document.querySelector('.itemcard-tbody');
  const template = document.getElementById('table-row-template');
  const totalFormsInput = document.querySelector('input[name$="-TOTAL_FORMS"]');

  let formIndex = +totalFormsInput.value;

  // Считаем количество строк с классом .itemcard-table-row, у которых НЕТ класса .dynamic-row (то есть существующие строки)
  let rowNumber = tableBody.querySelectorAll('tr.itemcard-table-row:not(.dynamic-row)').length;

  addButton.addEventListener('click', function () {
    const clone = template.content.cloneNode(true).firstElementChild;

    clone.innerHTML = clone.innerHTML
      .replace(/__prefix__/g, formIndex)
      .replace(/__index__/g, rowNumber + 1);

    tableBody.appendChild(clone);

    formIndex++;
    rowNumber++;
    totalFormsInput.value = formIndex;
  });

  removeButton.addEventListener('click', function () {
    const dynamicRows = tableBody.querySelectorAll('.dynamic-row');

    if (dynamicRows.length > 0) {
      const lastRow = dynamicRows[dynamicRows.length - 1];
      lastRow.remove();

      formIndex--;
      rowNumber--;
      totalFormsInput.value = formIndex;
    }
  });
});
