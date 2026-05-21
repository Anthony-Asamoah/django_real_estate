const date = new Date();
document.querySelector('.year').innerHTML = date.getFullYear();

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

