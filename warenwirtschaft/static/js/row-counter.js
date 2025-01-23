document.addEventListener('DOMContentLoaded', () => {
    const rowCounter = document.getElementById('row-counter');
    const tableBody = document.getElementById('table-body');
    const firstRow = tableBody.querySelector('tr'); // Первая строка таблицы
    const totalFormsInput = document.getElementById('id_form-TOTAL_FORMS');

    // Устанавливаем начальное количество строк
    updateRows(+rowCounter.value || 1);

    // Обновление строк при изменении счетчика
    rowCounter.addEventListener('input', () => {
        updateRows(+rowCounter.value || 1);
    });

    function updateRows(count) {
        // Удаляем лишние строки, если их больше, чем нужно
        while (tableBody.children.length > count) {
            tableBody.lastChild.remove();
        }

        // Добавляем недостающие строки
        while (tableBody.children.length < count) {
            const clone = firstRow.cloneNode(true);
            const index = tableBody.children.length;

            // Обновляем атрибуты для новой строки
            updateAttributes(clone, index);

            // Вставляем номер строки
            clone.querySelector('.row-number').textContent = index + 1;

            tableBody.appendChild(clone);
        }

        // Обновляем общее количество форм
        totalFormsInput.value = count;
    }

    function updateAttributes(row, index) {
        row.querySelectorAll('[id], [name]').forEach((el) => {
            if (el.id) el.id = el.id.replace(/-\d+/, `-${index}`);
            if (el.name) el.name = el.name.replace(/-\d+/, `-${index}`);
        });
    }
});
