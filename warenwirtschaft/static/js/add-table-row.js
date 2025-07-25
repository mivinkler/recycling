document.addEventListener('DOMContentLoaded', function () {
  const addButton = document.getElementById('form-add-btn');
  const removeButton = document.getElementById('form-remove-btn');
  const tableBody = document.querySelector('.itemcard-tbody');
  const template = document.getElementById('table-row-template');
  const totalFormsInput = document.querySelector('input[name$="-TOTAL_FORMS"]');

  let formIndex = +totalFormsInput.value;
  let rowNumber = formIndex;

  addButton.addEventListener('click', function () {
    const clone = template.content.cloneNode(true).firstElementChild;

    // Заменяем индексы в name/id и №
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
