const yearEl = document.querySelector('.year');
if (yearEl) yearEl.textContent = new Date().getFullYear();

setTimeout(function() {
    $('#message').fadeOut('slow');
}, 5000);

// Navbar scroll shadow
(function () {
  var nav = document.getElementById('main-nav');
  if (!nav) return;
  function onScroll() {
    nav.classList.toggle('nav-scrolled', window.scrollY > 40);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();

// Brand name slide-in + top-bar CTA swap when mobile menu opens
(function () {
  var nav = document.getElementById('main-nav');
  var navCollapse = document.getElementById('navbarNav');
  if (!nav || !navCollapse) return;
  navCollapse.addEventListener('show.bs.collapse', function () {
    nav.classList.add('nav-menu-open');
  });
  navCollapse.addEventListener('hide.bs.collapse', function () {
    nav.classList.remove('nav-menu-open');
  });
})();

