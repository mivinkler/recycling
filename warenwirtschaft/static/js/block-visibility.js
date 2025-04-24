document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".top-icon-js").forEach((iconBlock) => {
      const toggleButton = iconBlock.querySelector(".toggle-button");
      const sortPanel = iconBlock.querySelector(".top-icon-detail");
  
      if (!toggleButton || !sortPanel) return;
  
      toggleButton.addEventListener("click", function (event) {

        document.querySelectorAll(".top-icon-detail").forEach((panel) => {
          if (panel !== sortPanel) panel.setAttribute("hidden", "");
        });
  
        
        if (sortPanel.hasAttribute("hidden")) {
          sortPanel.removeAttribute("hidden");
        } else {
          sortPanel.setAttribute("hidden", "");
        }
  
        event.stopPropagation();
      });
  
      document.addEventListener("click", function (event) {
        if (!iconBlock.contains(event.target)) {
          sortPanel.setAttribute("hidden", "");
        }
      });
    });
  });
  