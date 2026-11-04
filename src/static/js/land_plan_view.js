/* Public land plan (project detail page).
   Plays when the whole photo is on screen (or it fills the viewport, for a photo taller than the screen): the boundary
   outline draws edge by edge, each corner/dimension pops in as the line reaches it, then the pin drops. It resets once
   the photo has fully scrolled out of view, so it plays again each time it comes back into full view. */
(function () {
  var DRAW_MS = 1400;
  var reduced = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  function markers(stage) { return stage.querySelectorAll('.lp-in'); }

  function reset(stage) {   // back to the hidden, armed state; restarts the CSS animations on the next play
    stage.classList.remove('lp-play');
    // animation:none lets the next play restart the keyframes; opacity:0 keeps the markers hidden meanwhile.
    [].forEach.call(markers(stage), function (m) { m.style.animation = 'none'; m.style.opacity = '0'; });
  }

  function play(stage) {
    var poly = stage.querySelector('.lp-poly');
    var pts = poly ? poly.getAttribute('points').trim().split(/\s+/).filter(Boolean).map(function (p) { return p.split(',').map(Number); }) : [];
    [].forEach.call(markers(stage), function (m) { m.style.animation = ''; m.style.opacity = ''; });
    void stage.offsetWidth;   // flush so the markers' animations restart from the beginning
    if (reduced || pts.length < 2 || !poly.animate) { stage.classList.add('lp-play'); return; }

    // Distance (in screen px) along the outline to each corner, so timing follows the line as it is drawn.
    var r = stage.getBoundingClientRect(), n = pts.length, segs = n > 2 ? n : 1, lens = [], cum = [0], total = 0, i;
    for (i = 0; i < segs; i++) {
      var a = pts[i], b = pts[(i + 1) % n];
      lens.push(Math.hypot((b[0] - a[0]) * r.width, (b[1] - a[1]) * r.height));
      total += lens[i]; cum.push(total);
    }
    if (!total) { stage.classList.add('lp-play'); return; }
    var at = function (d) { return (d / total * DRAW_MS) + 'ms'; };

    [].forEach.call(stage.querySelectorAll('.lp-pt'), function (c, k) { c.style.setProperty('--d', at(cum[Math.min(k, segs)])); });
    // A dimension chip belongs to the edge whose midpoint is nearest; show it when that edge finishes drawing.
    [].forEach.call(stage.querySelectorAll('.lp-dim'), function (d) {
      var x = parseFloat(d.style.left) / 100, y = parseFloat(d.style.top) / 100, best = 0, bestD = Infinity;
      for (var j = 0; j < segs; j++) {
        var p = pts[j], q = pts[(j + 1) % n], dd = Math.hypot((p[0] + q[0]) / 2 - x, (p[1] + q[1]) / 2 - y);
        if (dd < bestD) { bestD = dd; best = j; }
      }
      d.style.setProperty('--d', at(cum[best + 1]));
    });
    var pin = stage.querySelector('.lp-pin');
    if (pin) pin.style.setProperty('--d', (DRAW_MS + 150) + 'ms');

    stage.classList.add('lp-play');
    poly.animate(
      [{ strokeDasharray: total + 'px', strokeDashoffset: total + 'px' }, { strokeDasharray: total + 'px', strokeDashoffset: '0px' }],
      { duration: DRAW_MS, easing: 'ease-in-out', fill: 'backwards' }
    );
    poly.animate([{ fillOpacity: 0 }, { fillOpacity: 1 }], { duration: 600, delay: DRAW_MS * 0.7, fill: 'backwards' });
  }

  // "Fully visible": nearly all of the photo is on screen, or it covers (almost) the whole viewport height if it is taller.
  function fullyVisible(e) {
    var r = e.boundingClientRect, v = e.intersectionRect;
    return e.isIntersecting && v.height >= Math.min(r.height, window.innerHeight) * 0.95 && v.width >= r.width * 0.95;
  }

  function boot() {
    var stages = document.querySelectorAll('.lp-view.lp-armed');
    if (reduced || !('IntersectionObserver' in window)) { [].forEach.call(stages, play); return; }
    var steps = []; for (var k = 0; k <= 20; k++) steps.push(k / 20);   // fine thresholds so we notice the moment it becomes fully visible
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var st = e.target;
        if (fullyVisible(e)) { if (!st._lpOn) { st._lpOn = true; play(st); } }
        else if (!e.isIntersecting && st._lpOn) { st._lpOn = false; reset(st); }   // only once it has fully left, to avoid flicker at the edges
      });
    }, { threshold: steps });
    [].forEach.call(stages, function (s) { io.observe(s); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
