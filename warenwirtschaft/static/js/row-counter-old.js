function traeger() {
    const anzahl = parseInt(document.getElementById('traeger_anzahl').value, 10);
    const container = document.getElementById('traeger');
  
    // Alle Blöcke löschen, außer dem ersten
    const firstBlock = container.querySelector('.block');
    container.innerHTML = '';
    container.appendChild(firstBlock);
  
    // Zusätzliche Blöcke hinzufügen
    for (let i = 2; i <= anzahl; i++) {
      const newBlock = firstBlock.cloneNode(true);
  
      // Inhalt des neuen Blocks aktualisieren
      newBlock.querySelector('.form-item-title').textContent = `Ladungseinheit ${i}:`;
  
      // Aktualisiert die Attribute von Elementen in einem neuen Block
      newBlock.querySelectorAll('label, select, input').forEach((element) => {
        const oldId = element.getAttribute('id');
        if (oldId) {
          const newId = oldId.replace(/\d+$/, i); // Nummer durch die aktuelle ersetzen
          element.setAttribute('id', newId);
          if (element.tagName === 'LABEL') {
            element.setAttribute('for', newId);
          }
        }
      });
  
      container.appendChild(newBlock);
    }
  }