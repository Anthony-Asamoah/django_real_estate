// ── Scroll reveal ──────────────────────────────────────────────
const revealObserver = new IntersectionObserver(function(entries) {
  entries.forEach(function(entry) {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });

document.querySelectorAll('.reveal').forEach(function(el) {
  revealObserver.observe(el);
});

// ── Counter animation ──────────────────────────────────────────
function runCounter(el) {
  var raw = el.textContent.trim();
  var match = raw.match(/^([\d,]+)/);
  if (!match) return;
  var end = parseInt(match[1].replace(/,/g, ''), 10);
  var suffix = raw.slice(match[0].length);
  var duration = 1600;
  var startTime = performance.now();

  (function tick(now) {
    var t = Math.min((now - startTime) / duration, 1);
    var eased = 1 - Math.pow(1 - t, 3);
    el.textContent = Math.round(eased * end).toLocaleString() + suffix;
    if (t < 1) requestAnimationFrame(tick);
  })(startTime);
}

var statsObserver = new IntersectionObserver(function(entries) {
  entries.forEach(function(entry) {
    if (entry.isIntersecting) {
      entry.target.querySelectorAll('.stat-value').forEach(runCounter);
      statsObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.3 });

document.querySelectorAll('.stats-section').forEach(function(el) {
  statsObserver.observe(el);
});
