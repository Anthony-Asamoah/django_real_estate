/* Project page lightbox. Every [data-lb] element (main image, gallery thumbnails) opens here, in page order.
   Annotated photos (data-lb-overlay) are drawn with their boundary and pin, and the draw-on animation plays each
   time one is shown. Keyboard: Esc closes, ←/→ move, Tab stays inside. */
(function () {
  var reduced = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var NS = 'http://www.w3.org/2000/svg';
  var items = [], index = 0, lb = null, opener = null, token = 0;

  function el(tag, cls, parent) { var e = document.createElement(tag); if (cls) e.className = cls; if (parent) parent.appendChild(e); return e; }
  function pct(v) { return (Math.round(v * 1000) / 1000) + '%'; }

  function collect() {
    items = [].map.call(document.querySelectorAll('[data-lb]'), function (n) {
      var a = n.tagName === 'A' ? n : null, overlay = null;
      try { overlay = n.dataset.lbOverlay ? JSON.parse(n.dataset.lbOverlay) : null; } catch (e) { overlay = null; }
      return { node: n, src: n.dataset.lbSrc || (a && a.getAttribute('href')), alt: n.dataset.lbAlt || '', overlay: overlay };
    });
  }

  // The same markup the project page uses, so the shared overlay CSS and animation apply unchanged.
  function buildStage(item) {
    var st = el('div', 'lp-stage pg-lb-stage' + (item.overlay ? ' lp-view lp-armed' : ''));
    var img = el('img', '', st); img.alt = item.alt; img.draggable = false;
    if (item.overlay) {
      var o = item.overlay;
      st.style.setProperty('--lp-boundary', o.color);
      var svg = document.createElementNS(NS, 'svg');
      svg.setAttribute('class', 'lp-svg'); svg.setAttribute('viewBox', '0 0 1 1'); svg.setAttribute('preserveAspectRatio', 'none'); svg.setAttribute('aria-hidden', 'true');
      if (o.points) { var poly = document.createElementNS(NS, 'polygon'); poly.setAttribute('class', 'lp-poly'); poly.setAttribute('points', o.points); svg.appendChild(poly); }
      st.appendChild(svg);
      o.vertices.forEach(function (v) { var d = el('div', 'lp-pt lp-in', st); d.style.left = pct(v.x); d.style.top = pct(v.y); });
      o.edges.forEach(function (e) { var d = el('div', 'lp-dim lp-in', st); d.style.left = pct(e.x); d.style.top = pct(e.y); d.textContent = e.dim; });
      o.pins.forEach(function (p) {
        var d = el('div', 'lp-pin lp-in', st); d.style.left = pct(p.x); d.style.top = pct(p.y);
        if (p.color) d.style.setProperty('--lp-pin', p.color);
        d.style.setProperty('--lp-pin-size', p.size);
        if (p.label) el('span', 'lp-pin-label', d).textContent = p.label;
        el('i', 'fas fa-map-marker-alt lp-pin-icon', d).setAttribute('aria-hidden', 'true');
      });
    }
    return { stage: st, img: img };
  }

  function ensure() {
    if (lb) return;
    lb = el('div', 'pg-lb', document.body);
    lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true'); lb.setAttribute('aria-label', 'Photo viewer'); lb.hidden = true;
    var back = el('div', 'pg-lb-backdrop', lb);
    back.addEventListener('click', close);
    lb.close = el('button', 'pg-lb-btn pg-lb-close', lb); lb.close.type = 'button'; lb.close.setAttribute('aria-label', 'Close'); lb.close.innerHTML = '&times;';
    lb.prev = el('button', 'pg-lb-btn pg-lb-prev', lb); lb.prev.type = 'button'; lb.prev.setAttribute('aria-label', 'Previous photo'); lb.prev.innerHTML = '&#10094;';
    lb.next = el('button', 'pg-lb-btn pg-lb-next', lb); lb.next.type = 'button'; lb.next.setAttribute('aria-label', 'Next photo'); lb.next.innerHTML = '&#10095;';
    lb.holder = el('div', 'pg-lb-holder', lb);
    lb.caption = el('div', 'pg-lb-caption', lb); lb.caption.setAttribute('aria-live', 'polite');
    lb.close.addEventListener('click', close);
    lb.prev.addEventListener('click', function () { show(index - 1); });
    lb.next.addEventListener('click', function () { show(index + 1); });
    lb.addEventListener('keydown', onKey);
    lb.holder.addEventListener('click', function (e) { if (e.target === lb.holder) close(); });
  }

  function show(i) {
    index = (i + items.length) % items.length;
    var item = items[index], mine = ++token;
    var built = buildStage(item);
    lb.holder.classList.add('is-swapping');
    var current = lb.holder.firstChild;
    built.img.addEventListener('load', function () {
      if (mine !== token) return;   // the user already moved on
      built.stage.style.setProperty('--lp-aspect', built.img.naturalWidth / built.img.naturalHeight);
      if (current) current.remove();
      lb.holder.appendChild(built.stage);
      lb.holder.classList.remove('is-swapping');
      if (item.overlay && window.LandPlanView) window.LandPlanView.play(built.stage);   // animate every time an annotated photo opens
    });
    built.img.addEventListener('error', function () { if (mine === token) lb.holder.classList.remove('is-swapping'); });
    built.img.src = item.src;
    lb.caption.innerHTML = '';
    el('span', 'pg-lb-count', lb.caption).textContent = (index + 1) + ' / ' + items.length;
    if (item.alt) el('span', 'pg-lb-alt', lb.caption).textContent = item.alt;
    if (item.overlay) el('span', 'pg-lb-note', lb.caption).textContent = 'Indicative only. Confirm exact boundaries and dimensions before purchase.';
    lb.prev.hidden = lb.next.hidden = items.length < 2;
  }

  function open(i, from) {
    collect(); if (!items.length) return;
    ensure();
    opener = from || document.activeElement;
    lb.hidden = false;
    document.documentElement.classList.add('pg-lb-open');   // stops the page scrolling behind it
    requestAnimationFrame(function () { lb.classList.add('is-open'); });
    show(i);
    lb.close.focus();
  }

  function close() {
    if (!lb || lb.hidden) return;
    token++;
    lb.classList.remove('is-open');
    var done = function () { lb.hidden = true; lb.holder.innerHTML = ''; };
    if (reduced) done(); else setTimeout(done, 180);
    document.documentElement.classList.remove('pg-lb-open');
    if (opener && opener.focus) opener.focus();
  }

  function onKey(e) {
    if (e.key === 'Escape') { e.preventDefault(); close(); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); show(index - 1); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); show(index + 1); }
    else if (e.key === 'Tab') {   // keep focus inside the viewer
      var f = [lb.close, lb.prev, lb.next].filter(function (b) { return !b.hidden; });
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  }

  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('[data-lb]');
    if (!t || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey) return;   // let "open in new tab" through
    e.preventDefault();
    collect();
    var i = items.map(function (it) { return it.node; }).indexOf(t);
    open(Math.max(0, i), t.querySelector('.pg-expand') || t);
  });
})();
