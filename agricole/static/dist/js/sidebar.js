// Sidebar functionality
document.addEventListener('DOMContentLoaded', function() {
  // Submenu toggle functionality
  const submenuToggles = document.querySelectorAll('.submenu-toggle');
  
  submenuToggles.forEach(toggle => {
    toggle.addEventListener('click', function(e) {
      e.preventDefault();
      const parentItem = this.closest('.has-submenu');
      parentItem.classList.toggle('menu-open');
    });
  });
  
  // Search functionality
  const searchInput = document.querySelector('.search-input');
  const navItems = document.querySelectorAll('.nav-item:not(.nav-section)');
  
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      const searchTerm = this.value.toLowerCase();
      
      navItems.forEach(item => {
        const navText = item.querySelector('.nav-text');
        if (navText) {
          const text = navText.textContent.toLowerCase();
          if (text.includes(searchTerm) || searchTerm === '') {
            item.style.display = 'block';
          } else {
            item.style.display = 'none';
          }
        }
      });
    });
  }
});
