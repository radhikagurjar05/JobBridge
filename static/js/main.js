/*
  static/js/main.js
  Shared JavaScript for the JobCatch application.
*/

document.addEventListener('DOMContentLoaded', () => {
  // Mobile Hamburger Menu
  const hamburger = document.getElementById('hamburger');
  const navLinks = document.getElementById('navLinks');

  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      navLinks.classList.toggle('active');
      const icon = hamburger.querySelector('i');
      if (navLinks.classList.contains('active')) {
        icon.classList.remove('fa-bars');
        icon.classList.add('fa-times');
      } else {
        icon.classList.remove('fa-times');
        icon.classList.add('fa-bars');
      }
    });
  }

  // Theme Toggle
  const themeToggle = document.getElementById('themeToggle');
  const currentTheme = localStorage.getItem('theme');
  
  if (currentTheme) {
    document.documentElement.setAttribute('data-theme', currentTheme);
    if (currentTheme === 'dark' && themeToggle) {
      themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      let theme = document.documentElement.getAttribute('data-theme');
      if (theme === 'dark') {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
        themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
      } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
      }
    });
  }
});

// Toggle password visibility (used on Login and Register pages)
function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  const icon = document.getElementById(inputId + '-eye');
  
  if (input.type === 'password') {
    input.type = 'text';
    icon.classList.remove('fa-eye');
    icon.classList.add('fa-eye-slash');
  } else {
    input.type = 'password';
    icon.classList.remove('fa-eye-slash');
    icon.classList.add('fa-eye');
  }
}
