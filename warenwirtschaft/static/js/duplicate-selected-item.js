function duplicateSelectedItem(radioButton) {
    const selectedRow = radioButton.closest('tr');

    document.getElementById('selected-id').textContent = selectedRow.querySelector('.item-id').textContent.trim();
    document.getElementById('selected-supplier').textContent = selectedRow.querySelector('.item-supplier').textContent.trim();
    document.getElementById('selected-container').textContent = selectedRow.querySelector('.item-container').textContent.trim();
    document.getElementById('selected-content').textContent = selectedRow.querySelector('.item-content').textContent.trim();
    document.getElementById('selected-weight').textContent = selectedRow.querySelector('.item-weight').textContent.trim();
}