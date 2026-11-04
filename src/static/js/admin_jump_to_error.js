/* After a failed save, take the editor straight to the first validation error: open the tab and any collapsed
   panels around it, scroll it into view, focus the field and flash it so it is easy to spot. */
(function () {
  var reduced = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  function reveal(field) {
    // Wrong tab? Switch to the one that holds the error.
    var pane = field.closest('[role="tabpanel"]');
    while (pane) {
      if (pane.hidden || getComputedStyle(pane).display === 'none') {
        var tab = document.querySelector('[role="tab"][aria-controls="' + pane.id + '"]');
        if (tab) tab.click();
      }
      pane = pane.parentElement && pane.parentElement.closest('[role="tabpanel"]');
    }
    // Collapsed panels (Wagtail panels toggle with aria-expanded on their header button).
    var panel = field.closest('.w-panel');
    while (panel) {
      var toggle = panel.querySelector(':scope > .w-panel__header [aria-expanded="false"]');
      if (toggle) toggle.click();
      panel = panel.parentElement && panel.parentElement.closest('.w-panel');
    }
  }

  function jump() {
    var field = document.querySelector('.w-field--error');   // the first one in page order (not just the first <form>: the sidebar search is one too)
    if (!field) return;
    reveal(field);
    // Give the tab/panel a moment to open before measuring and scrolling.
    setTimeout(function () {
      field.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'center' });
      var target = field.querySelector('input:not([type="hidden"]), select, textarea, [contenteditable="true"], button');
      if (target) target.focus({ preventScroll: true });
      field.classList.add('lp-error-flash');
      setTimeout(function () { field.classList.remove('lp-error-flash'); }, 2200);
    }, 180);
  }

  var css = document.createElement('style');
  css.textContent = '.lp-error-flash { animation: lp-error-flash 1.1s ease-in-out 2; border-radius: 6px; }'
    + '@keyframes lp-error-flash { 0%, 100% { box-shadow: 0 0 0 0 rgba(201, 41, 41, 0); background: transparent; }'
    + '50% { box-shadow: 0 0 0 6px rgba(201, 41, 41, .22); background: rgba(201, 41, 41, .05); } }'
    + '@media (prefers-reduced-motion: reduce) { .lp-error-flash { animation: none; box-shadow: 0 0 0 3px rgba(201, 41, 41, .35); } }';
  document.head.appendChild(css);

  // After the page (and Wagtail's own panel setup) has finished loading.
  if (document.readyState === 'complete') setTimeout(jump, 150);
  else window.addEventListener('load', function () { setTimeout(jump, 150); });
})();
