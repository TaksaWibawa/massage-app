function toggleSubmenu(element) {
  let submenuList = element.querySelector('.submenu-list');
  let icon = element.querySelector('i');
  if (submenuList.style.display === 'none') {
    submenuList.style.display = 'block';
    icon.classList.add('fa-rotate-90');
  } else {
    submenuList.style.display = 'none';
    icon.classList.remove('fa-rotate-90');
  }
}
