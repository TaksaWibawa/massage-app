function toggleSubmenu(event) {
  let element = event.currentTarget;
  if (event.target.classList.contains('submenu-item')) {
    event.stopPropagation();
    return;
  }

  let submenuList = element.querySelector('.submenu-list');
  let icon = element.querySelector('i');
  if (submenuList.style.display === 'block') {
    submenuList.style.display = 'none';
    icon.classList.remove('fa-rotate-90');
  } else {
    submenuList.style.display = 'block';
    console.log('open');
    icon.classList.add('fa-rotate-90');
  }
}

document.addEventListener('DOMContentLoaded', (event) => {
  let toastElList = [].slice.call(document.querySelectorAll('.toast'));
  let toastList = toastElList.map(function (toastEl) {
    return new bootstrap.Toast(toastEl, { autohide: true });
  });
  toastList.forEach((toast) => toast.show());

  let menuItems = document.querySelectorAll('.menu');
  menuItems.forEach((menuItem) => {
    let submenuList = menuItem.querySelector('.submenu-list');
    submenuList.style.display = 'block';
  });
});
