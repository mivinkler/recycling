function duplicateSelectedItem(radioButton) {
    const selectedRow = radioButton.closest('tr');

    document.getElementById('selected-id').textContent = selectedRow.querySelector('.tbody-id-simple').textContent.trim();
    document.getElementById('selected-supplier').textContent = selectedRow.querySelector('.tbody-name').textContent.trim();
    document.getElementById('selected-container').textContent = selectedRow.querySelector('.tbody-delivery-type').textContent.trim();
    document.getElementById('selected-content').textContent = selectedRow.querySelector('.tbody-material').textContent.trim();
    document.getElementById('selected-weight').textContent = selectedRow.querySelector('.tbody-weight').textContent.trim();
}