document.addEventListener("DOMContentLoaded", () => {
  const body = document.querySelector("[data-formset-body]");
  const template = document.querySelector("[data-formset-template]");
  const addBtn = document.querySelector("[data-formset-add]");
  const removeBtn = document.querySelector("[data-formset-remove]");

  if (!body || !template || !addBtn || !removeBtn) return;

  const prefix = body.dataset.formsetPrefix;
  const totalForms = document.getElementById(`id_${prefix}-TOTAL_FORMS`);

  if (!prefix || !totalForms) {
    console.error("Formset prefix oder TOTAL_FORMS nicht gefunden.", { prefix, totalForms });
    return;
  }

  let formIndex = parseInt(totalForms.value, 10) || 0;

  const getRowNumber = () => body.querySelectorAll("tr").length + 1;

  addBtn.addEventListener("click", () => {
    const clone = template.content.firstElementChild.cloneNode(true);

    clone.innerHTML = clone.innerHTML
      .replace(/__prefix__/g, String(formIndex))
      .replace(/__index__/g, String(getRowNumber()));

    body.appendChild(clone);

    formIndex += 1;
    totalForms.value = String(formIndex);
  });

  removeBtn.addEventListener("click", () => {
    const dynamicRows = body.querySelectorAll("tr[data-formset-row]");
    if (dynamicRows.length === 0) return;

    dynamicRows[dynamicRows.length - 1].remove();

    formIndex = Math.max(0, formIndex - 1);
    totalForms.value = String(formIndex);
  });
});
