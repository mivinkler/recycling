document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.selectable-row').forEach(row => {
        row.addEventListener('click', function() {
            const radio = this.querySelector('.inputField');
            if (radio) {
                // Activate radio input
                radio.checked = true;
                
                // Duplicate input row
                document.getElementById('select-input').value = radio.dataset.value;
                document.getElementById('result-input').value = radio.value;
            }
        });
    });
});