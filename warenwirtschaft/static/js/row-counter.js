// document.addEventListener('DOMContentLoaded', () => {
//     const itemCounter = document.getElementById('item-counter');
//     const itemWrapper = document.getElementById('item-wrapper');
//     const firstRow = itemWrapper.children[0];

//     itemCounter.addEventListener('input', () => {
//         updateRows(+itemCounter.value || 1);
//     });

//     function updateRows(count) {
//         while (itemWrapper.children.length > count) {
//             itemWrapper.lastChild.remove();
//         }

//         while (itemWrapper.children.length < count) {
//             const clone = firstRow.cloneNode(true);
//             const index = itemWrapper.children.length;

//             updateAttributes(clone, index);

//             clone.querySelector('.item-number').textContent = index + 1;

//             itemWrapper.appendChild(clone);
//         }
//     }
//     updateRows(+itemCounter.value || 1);

//     function updateAttributes(row, index) {
//         row.querySelectorAll('[id], [name]').forEach((el) => {
//             if (el.id) el.id = el.id.replace(/-\d+/, `-${index}`);
//             if (el.name) el.name = el.name.replace(/-\d+/, `-${index}`);            
//         });
//     }
// });
