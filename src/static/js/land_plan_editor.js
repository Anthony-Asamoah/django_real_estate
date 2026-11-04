/* Land plan editor (admin).
   Pick any photo, draw a boundary polygon, label its edges and place one location pin on it. Every photo keeps its
   own annotations. Coordinates are stored normalised (0–1) so the overlay scales with the image.

   Changes autosave in the background: each request is a full snapshot (all annotations + undo/redo history), sent one at
   a time, retried with backoff, and guarded by a server revision so late or duplicate requests cannot overwrite newer data.
   The hidden form field always mirrors the latest state, so the normal Save button still works as a fallback. */
(function () {
  var MAX_LABEL = 50, MAX_DIM = 20, MAX_HISTORY = 50;
  var SAVE_DEBOUNCE_MS = 700, REQUEST_TIMEOUT_MS = 12000, MAX_BODY_CHARS = 550000;
  var NS = 'http://www.w3.org/2000/svg';
  // Must match PALETTE in domains/projects/models.py (the server rejects anything else).
  var PALETTE = {
    '#ffc107': 'Amber', '#dc3545': 'Red', '#0d6efd': 'Blue', '#198754': 'Green',
    '#6f42c1': 'Purple', '#fd7e14': 'Orange', '#ffffff': 'White', '#212529': 'Black'
  };
  var DEFAULT_BOUNDARY = '#ffc107', DEFAULT_PIN = '#dc3545';
  var reducedMotion = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var PIN_MIN = 0.6, PIN_MAX = 2, PIN_STEP = 0.1;   // pin size is a scale factor; must match PIN_MIN_SIZE/PIN_MAX_SIZE in models.py
  function clampSize(v) { v = +v; return isFinite(v) ? Math.min(PIN_MAX, Math.max(PIN_MIN, Math.round(v * 100) / 100)) : 1; }

  function el(tag, cls, parent) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (parent) parent.appendChild(e);
    return e;
  }

  function round4(v) { return Math.round(v * 10000) / 10000; }

  // A row of colour swatches (radio group). `current()` is read on each repaint.
  function swatchGroup(parent, label, current, onPick) {
    var g = el('div', 'lp-swatches', parent);
    g.setAttribute('role', 'radiogroup'); g.setAttribute('aria-label', label);
    function paint() {
      [].forEach.call(g.children, function (b) { b.setAttribute('aria-checked', b.dataset.color === current()); });
    }
    Object.keys(PALETTE).forEach(function (c) {
      var b = el('button', 'lp-swatch', g); b.type = 'button'; b.dataset.color = c;
      b.style.setProperty('--sw', c); b.setAttribute('role', 'radio');
      b.setAttribute('aria-label', PALETTE[c]); b.title = PALETTE[c];
      b.addEventListener('click', function (e) { e.stopPropagation(); onPick(c); paint(); });
    });
    paint();
    g.repaint = paint;   // called after undo/redo/photo switches change the value from outside
    return g;
  }

  // Coerce stored/untrusted data into the shape the editor expects: one pin always present.
  function normEntry(e) {
    e = e || {};
    return {
      color: PALETTE[e.color] ? e.color : DEFAULT_BOUNDARY,
      boundary: (e.boundary || []).map(function (p) { return { x: +p.x, y: +p.y, dim: p.dim || '' }; }),
      pins: [e.pins && e.pins[0]
        ? { x: +e.pins[0].x, y: +e.pins[0].y, label: e.pins[0].label || '', color: e.pins[0].color || '', size: clampSize(e.pins[0].size || 1) }
        : { x: 0.5, y: 0.5, label: '', color: '', size: 1 }]
    };
  }

  function init(root) {
    var input = document.getElementById(root.dataset.input);
    var cfg = {
      slots: JSON.parse(root.dataset.slots),            // [[slotName, label], ...]
      images: JSON.parse(root.dataset.images || '{}'),  // slotName -> {id, url, thumb, title} for saved photos
      land: JSON.parse(root.dataset.land || '[]').map(String),   // service ids this editor is enabled for
      endpoint: root.dataset.endpoint,                  // .../image-info/0/ ; the 0 is replaced by an image id
      saveUrl: root.dataset.saveUrl,                    // '' until the project has been saved once
      history: JSON.parse(root.dataset.history || '{}')
    };
    var wrap = root.closest('.w-field') || root;
    var wsWrap = root.closest('.w-panel__wrapper'), panel = root.closest('.w-panel__content'), host = panel && panel.parentElement, formWidth = host && host.closest('.w-form-width');
    var slotNames = cfg.slots.map(function (s) { return s[0]; });
    var csrf = (document.querySelector('input[name=csrfmiddlewaretoken]') || {}).value || '';
    var clientId = (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : Math.random().toString(36).slice(2) + Date.now().toString(36);

    // ── State ──
    var all = {};   // slot -> {color, boundary, pins}: every annotated photo
    try {
      var saved = (JSON.parse(input.value || '{}').photos) || {};
      slotNames.forEach(function (s) { if (saved[s]) all[s] = normEntry(saved[s]); });
    } catch (e) { all = {}; }
    var fresh = new WeakSet();   // items added this session: only these get the pop-in animation
    var active = all[cfg.history.active] ? cfg.history.active : '';   // photo being edited ('' = none)
    var data = active ? all[active] : null;                           // the active photo's annotations
    var pts = [], edges = [], pins = [];

    // ── Layout: workspace header, empty state, then the editing box ──
    var head = el('div', 'lp-ws-head', root);
    var titleWrap = el('div', 'lp-ws-title', head);
    el('i', 'fas fa-draw-polygon lp-ws-icon', titleWrap).setAttribute('aria-hidden', 'true');
    el('h4', '', titleWrap).textContent = 'Boundary & pin';
    var subtitle = el('span', 'lp-ws-sub', titleWrap);   // which photo is open
    var headRight = el('div', 'lp-ws-right', head);
    var statusEl = el('div', 'lp-status', headRight);
    statusEl.setAttribute('role', 'status'); statusEl.setAttribute('aria-live', 'polite');
    var btnClose = el('button', 'lp-btn lp-btn-quiet', headRight); btnClose.type = 'button'; btnClose.textContent = 'Close';
    btnClose.title = 'Close this photo'; btnClose.addEventListener('click', function () { selectPhoto(''); });

    var emptyState = el('div', 'lp-empty-state', root);
    emptyState.innerHTML = '<svg class="lp-empty-art" viewBox="0 0 160 110" aria-hidden="true"><rect x="6" y="6" width="148" height="98" rx="10" class="lp-art-frame"/>'
      + '<polygon points="34,78 52,34 108,28 128,70 80,92" class="lp-art-poly"/><circle cx="34" cy="78" r="4.5" class="lp-art-pt"/><circle cx="52" cy="34" r="4.5" class="lp-art-pt"/>'
      + '<circle cx="108" cy="28" r="4.5" class="lp-art-pt"/><circle cx="128" cy="70" r="4.5" class="lp-art-pt"/><circle cx="80" cy="92" r="4.5" class="lp-art-pt"/>'
      + '<g class="lp-art-pin"><path d="M82 62c-9-10-12-15-12-20a12 12 0 0124 0c0 5-3 10-12 20z"/><circle cx="82" cy="42" r="4.6"/></g></svg>'
      + '<h5 class="lp-empty-title"></h5><p class="lp-empty-text"></p>';
    var emptyTitle = emptyState.querySelector('.lp-empty-title'), emptyText = emptyState.querySelector('.lp-empty-text');

    var box = el('div', 'lp-box', root);
    var bar = el('div', 'lp-toolbar', box);
    var gHist = el('div', 'lp-group', bar);
    var btnU = el('button', 'lp-btn', gHist); btnU.type = 'button'; btnU.textContent = '↶ Undo';
    btnU.title = 'Undo (Ctrl/Cmd+Z)'; btnU.setAttribute('aria-label', 'Undo');
    var btnR = el('button', 'lp-btn', gHist); btnR.type = 'button'; btnR.textContent = '↷ Redo';
    btnR.title = 'Redo (Ctrl/Cmd+Shift+Z or Ctrl+Y)'; btnR.setAttribute('aria-label', 'Redo');
    var gEdit = el('div', 'lp-group', bar);
    var btnC = el('button', 'lp-btn', gEdit); btnC.type = 'button'; btnC.textContent = 'Clear boundary';
    var btnX = el('button', 'lp-btn lp-btn-danger', gEdit); btnX.type = 'button'; btnX.textContent = 'Remove from photo';
    btnX.title = 'Remove all annotations from this photo';
    var gColor = el('div', 'lp-group lp-group-color', bar);
    el('span', 'lp-group-label', gColor).textContent = 'Boundary';
    var boundarySw = swatchGroup(gColor, 'Boundary colour', function () { return data ? data.color : DEFAULT_BOUNDARY; }, function (c) {
      if (!data) return;
      data.color = c; stage.style.setProperty('--lp-boundary', c); save(); commit();
    });

    var stage = el('div', 'lp-stage lp-editing', box);
    var img = el('img', '', stage); img.draggable = false; img.alt = '';
    // The photo is sized to fit the screen height (see CSS), which needs its aspect ratio.
    img.addEventListener('load', function () { if (img.naturalHeight) box.style.setProperty('--lp-aspect', img.naturalWidth / img.naturalHeight); });
    var svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('class', 'lp-svg'); svg.setAttribute('viewBox', '0 0 1 1'); svg.setAttribute('preserveAspectRatio', 'none');
    var poly = document.createElementNS(NS, 'polygon'); poly.setAttribute('class', 'lp-poly');
    svg.appendChild(poly); stage.appendChild(svg);
    var layer = el('div', '', stage);
    var hint = el('p', 'lp-hint', box);
    hint.innerHTML = '<i class="fas fa-circle-info" aria-hidden="true"></i> Click the photo to add corners. Drag corners and the pin to move them. Right-click (or tap) a corner to remove it, or the pin to change its colour and size. Type a dimension on each edge.';

    // ── Serialisation ──
    function payload() {   // canonical snapshot of every annotated photo, in slot order
      var photos = {};
      slotNames.forEach(function (s) {
        var d = all[s];
        if (!d) return;
        photos[s] = {
          color: d.color,
          boundary: d.boundary.map(function (p) { return { x: round4(p.x), y: round4(p.y), dim: p.dim || '' }; }),
          pins: d.pins.map(function (p) { return { x: round4(p.x), y: round4(p.y), label: p.label || '', color: p.color || '', size: clampSize(p.size) }; })
        };
      });
      return JSON.stringify({ photos: photos });
    }
    function save() { input.value = payload(); markDirty(SAVE_DEBOUNCE_MS); }

    // ── Undo / redo: a stack of serialised states, one entry per finished action ──
    var undoStack = (cfg.history.undo || []).slice(-MAX_HISTORY), redoStack = (cfg.history.redo || []).slice(-MAX_HISTORY);
    var current = payload(), nudgeTimer = 0, focused = false;

    function updateHistoryButtons() {
      btnU.disabled = !undoStack.length; btnR.disabled = !redoStack.length;
      btnU.setAttribute('aria-disabled', btnU.disabled); btnR.setAttribute('aria-disabled', btnR.disabled);
    }
    function commit() {   // call after an action finishes; no-op if nothing actually changed
      clearTimeout(nudgeTimer); nudgeTimer = 0;
      var s = payload();
      if (s === current) return;
      undoStack.push(current); if (undoStack.length > MAX_HISTORY) undoStack.shift();
      redoStack = []; current = s; updateHistoryButtons();
      markDirty(0);   // the history is part of every request
    }
    function commitSoon() { clearTimeout(nudgeTimer); nudgeTimer = setTimeout(commit, 500); }   // groups a run of arrow-key nudges

    function restore(s) {
      var before = JSON.parse(payload()).photos, next = JSON.parse(s).photos || {};
      all = {};
      slotNames.forEach(function (sl) { if (next[sl]) all[sl] = normEntry(next[sl]); });
      // Jump to the photo the step changed, so the user sees what undo/redo did.
      var after = JSON.parse(payload()).photos;
      var changed = slotNames.filter(function (sl) { return JSON.stringify(before[sl]) !== JSON.stringify(after[sl]); });
      active = changed.length ? (all[changed[0]] ? changed[0] : '') : (all[active] ? active : '');
      data = active ? all[active] : null;
      closeMenu(false);
      current = payload(); input.value = current;
      applyPhoto(); refreshSlots(); render(); updateHistoryButtons(); markDirty(0);
    }
    function undo() {
      commit();   // capture any pending edit first
      if (!undoStack.length) return;
      redoStack.push(current); restore(undoStack.pop());
    }
    function redo() {
      commit();
      if (!redoStack.length) return;
      undoStack.push(current); restore(redoStack.pop());
    }
    btnU.onclick = undo; btnR.onclick = redo;
    root.addEventListener('focusin', function () { focused = true; });
    root.addEventListener('pointerdown', function () { focused = true; });
    document.addEventListener('focusin', function (e) { if (!root.contains(e.target)) focused = false; });
    document.addEventListener('keydown', function (e) {
      if (!focused || !(e.ctrlKey || e.metaKey) || e.altKey) return;
      var k = e.key.toLowerCase();
      var isUndo = k === 'z' && !e.shiftKey, isRedo = (k === 'z' && e.shiftKey) || (k === 'y' && !e.metaKey);
      if (!isUndo && !isRedo) return;
      // In a label/dimension box, leave the browser's own text undo alone.
      if (e.target.tagName === 'INPUT' && root.contains(e.target)) return;
      e.preventDefault();
      if (isUndo) undo(); else redo();
    });

    // ── Autosave: one request at a time, full snapshots, retry with backoff, revision-guarded ──
    var sync = { rev: parseInt(root.dataset.rev, 10) || 0, dirty: false, inflight: false, paused: false,
                 attempt: 0, timer: 0, retryTimer: 0, submitting: false, conflict: null };
    var statusTimer = 0;

    function setStatus(kind, msg, actions) {
      clearTimeout(statusTimer);
      statusEl.className = 'lp-status' + (kind ? ' lp-status-' + kind : '');
      statusEl.textContent = msg || '';
      (actions || []).forEach(function (a) {
        var b = el('button', 'lp-status-btn', statusEl); b.type = 'button'; b.textContent = a[0]; b.addEventListener('click', a[1]);
      });
      if (kind === 'saved') statusTimer = setTimeout(function () { statusEl.classList.add('is-hidden'); }, 2200);
    }

    function markDirty(delay) {
      sync.dirty = true;
      if (sync.paused) return;
      if (!cfg.saveUrl) { setStatus('local', 'Not saved yet — press Save to keep these changes.'); return; }
      if (!sync.inflight && !sync.retryTimer) setStatus('pending', 'Unsaved changes…');
      clearTimeout(sync.timer); sync.timer = setTimeout(flush, delay);
    }

    function buildBody() {
      var undoPart = undoStack, redoPart = redoStack, body;
      for (;;) {
        body = JSON.stringify({
          client_id: clientId, base_rev: sync.rev, state: JSON.parse(payload()),
          history: { undo: undoPart, redo: redoPart, active: active }
        });
        if (body.length <= MAX_BODY_CHARS || (!undoPart.length && !redoPart.length)) return body;
        undoPart = undoPart.slice(Math.ceil(undoPart.length / 2)); redoPart = redoPart.slice(Math.ceil(redoPart.length / 2));   // oversized: trim old history
      }
    }
    function headers() { return { 'Content-Type': 'application/json', 'X-CSRFToken': csrf }; }

    function retryLater() {
      sync.dirty = true; sync.attempt++;
      var delay = Math.min(30000, 1000 * Math.pow(2, sync.attempt - 1)) * (0.75 + Math.random() * 0.5);   // jitter avoids synchronised retries
      setStatus('retry', navigator.onLine ? 'Couldn’t save — retrying…' : 'Offline — changes will save when you reconnect.');
      clearTimeout(sync.retryTimer);
      sync.retryTimer = setTimeout(function () { sync.retryTimer = 0; flush(); }, delay);
    }

    function flush() {
      clearTimeout(sync.timer); sync.timer = 0;
      if (!sync.dirty || sync.inflight || sync.paused || !cfg.saveUrl) return;
      if (!navigator.onLine) { setStatus('offline', 'Offline — changes will save when you reconnect.'); return; }
      clearTimeout(sync.retryTimer); sync.retryTimer = 0;
      sync.dirty = false; sync.inflight = true;
      setStatus('saving', 'Saving…');
      var ctrl = window.AbortController ? new AbortController() : null;
      var to = setTimeout(function () { if (ctrl) ctrl.abort(); }, REQUEST_TIMEOUT_MS);
      fetch(cfg.saveUrl, { method: 'POST', headers: headers(), body: buildBody(), credentials: 'same-origin', signal: ctrl && ctrl.signal })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { status: r.status, j: j }; }); })
        .then(function (res) { clearTimeout(to); sync.inflight = false; handleResponse(res.status, res.j); })
        .catch(function () { clearTimeout(to); sync.inflight = false; retryLater(); });   // network error or our own timeout
    }

    function handleResponse(status, j) {
      if (status === 200) {
        sync.rev = j.rev; sync.attempt = 0;
        if (sync.dirty) flush();
        else if (j.dropped && j.dropped.length) setStatus('local', 'A newly chosen photo isn’t saved yet — press Save to keep its annotations.');
        else setStatus('saved', 'All changes saved');
      } else if (status === 409) {
        // The revision moved on. If it was our own earlier request (it timed out but was applied), rebase and resend;
        // otherwise someone else changed it, so let the user decide.
        if (j.writer === clientId) { sync.rev = j.rev; sync.dirty = true; flush(); }
        else {
          sync.paused = true; sync.conflict = j; sync.dirty = true;
          setStatus('conflict', 'Changed in another tab or by someone else.', [['Keep mine', keepMine], ['Use theirs', useTheirs]]);
        }
      } else if (status === 422) {   // not enabled for this service yet, or invalid content: wait for the next edit
        sync.attempt = 0;
        setStatus('error', j.code === 'not_enabled' ? j.error : 'Not saved: ' + (j.error || 'invalid data'));
      } else if (status === 403 || status === 413 || status === 404) {
        sync.paused = true; setStatus('error', 'Not saved: ' + (j.error || 'this change was rejected') + ' Use the Save button instead.');
      } else {
        retryLater();   // 5xx / 429 / anything unexpected
      }
    }

    function keepMine() {
      sync.rev = sync.conflict.rev; sync.paused = false; sync.conflict = null; sync.dirty = true; flush();
    }
    function useTheirs() {
      var c = sync.conflict, theirs = (c.state && c.state.photos) || {}, h = c.history || {};
      all = {};
      slotNames.forEach(function (s) { if (theirs[s]) all[s] = normEntry(theirs[s]); });
      undoStack = (h.undo || []).slice(-MAX_HISTORY); redoStack = (h.redo || []).slice(-MAX_HISTORY);
      active = all[h.active] ? h.active : ''; data = active ? all[active] : null;
      sync.rev = c.rev; sync.paused = false; sync.conflict = null; sync.dirty = false;
      closeMenu(false); current = payload(); input.value = current;
      applyPhoto(); refreshSlots(); render(); updateHistoryButtons(); setStatus('saved', 'Loaded the latest version');
    }

    window.addEventListener('online', function () { sync.attempt = 0; clearTimeout(sync.retryTimer); sync.retryTimer = 0; flush(); });
    window.addEventListener('offline', function () { if (sync.dirty || sync.inflight) setStatus('offline', 'Offline — changes will save when you reconnect.'); });
    document.addEventListener('visibilitychange', function () { if (document.visibilityState === 'visible') flush(); });   // background timers get throttled
    var form = root.closest('form');
    if (form) form.addEventListener('submit', function () { sync.submitting = true; });   // the Save button carries the same state
    window.addEventListener('beforeunload', function (e) {
      if (!sync.submitting && !sync.paused && cfg.saveUrl && (sync.dirty || sync.inflight)) { e.preventDefault(); e.returnValue = ''; }
    });
    window.addEventListener('pagehide', function () {   // last-chance flush; keepalive survives the page going away
      if (!cfg.saveUrl || sync.paused || sync.submitting || !(sync.dirty || sync.inflight)) return;
      var body = buildBody();
      if (body.length < 60000) fetch(cfg.saveUrl, { method: 'POST', headers: headers(), body: body, credentials: 'same-origin', keepalive: true });
    });

    // ── Canvas ──
    // Reposition existing elements without rebuilding them, so drags stay 1:1 with the pointer.
    function layout() {
      if (!data) return;
      var b = data.boundary, n = b.length;
      poly.setAttribute('points', n > 1 ? b.map(function (p) { return p.x + ',' + p.y; }).join(' ') : '');
      pts.forEach(function (e, i) { e.style.left = b[i].x * 100 + '%'; e.style.top = b[i].y * 100 + '%'; });
      edges.forEach(function (e, i) {
        var a = b[i], c = b[(i + 1) % n];
        // Clamped so a chip never sticks out past the photo (matches the public page).
        e.style.left = Math.min(Math.max((a.x + c.x) / 2 * 100, 5), 95) + '%'; e.style.top = Math.min(Math.max((a.y + c.y) / 2 * 100, 4), 96) + '%';
      });
      data.pins.forEach(function (p, i) { pins[i].style.left = p.x * 100 + '%'; pins[i].style.top = p.y * 100 + '%'; });
    }

    function drag(handle, item, host) {
      var raf = 0;
      handle.tabIndex = 0; handle.setAttribute('role', 'button');
      handle.setAttribute('aria-label', item.label !== undefined ? 'Pin: arrow keys move, plus and minus resize' : 'Boundary corner: arrow keys move, Delete removes');
      handle.addEventListener('pointerdown', function (e) {
        e.preventDefault(); e.stopPropagation();
        handle.setPointerCapture(e.pointerId);
        host.classList.add('lp-dragging');
        var rect = stage.getBoundingClientRect();
        // Keep the grab point under the pointer so the item does not jump on pick-up.
        var offX = item.x - (e.clientX - rect.left) / rect.width, offY = item.y - (e.clientY - rect.top) / rect.height;
        var startX = e.clientX, startY = e.clientY, moved = false;
        function move(ev) {
          if (Math.abs(ev.clientX - startX) + Math.abs(ev.clientY - startY) > 6) moved = true;
          item.x = Math.min(1, Math.max(0, (ev.clientX - rect.left) / rect.width + offX));
          item.y = Math.min(1, Math.max(0, (ev.clientY - rect.top) / rect.height + offY));
          if (!raf) raf = requestAnimationFrame(function () { raf = 0; layout(); });
        }
        function up(ev) {
          handle.removeEventListener('pointermove', move);
          handle.removeEventListener('pointerup', up);
          handle.removeEventListener('pointercancel', up);
          host.classList.remove('lp-dragging');
          host.classList.add('lp-drop');   // little settle animation on drop
          host.addEventListener('animationend', function end(a) { if (a.target === host || host.contains(a.target)) { host.classList.remove('lp-drop'); host.removeEventListener('animationend', end); } });
          save(); commit();
          // A tap (not a drag) on a touch screen opens the same menu a right-click does.
          if (ev && ev.type === 'pointerup' && ev.pointerType === 'touch' && !moved) {
            var sr = stage.getBoundingClientRect();
            openMenu(ev.clientX - sr.left, ev.clientY - sr.top, handle, isPin, item, remove);
          }
        }
        handle.addEventListener('pointermove', move);
        handle.addEventListener('pointerup', up);
        handle.addEventListener('pointercancel', up);
      });
      var isPin = item.label !== undefined;
      function remove() {
        if (isPin) return;   // the pin can only be moved
        host.classList.add('lp-out');   // animate out, then drop from data
        setTimeout(function () {
          data.boundary.splice(data.boundary.indexOf(item), 1);
          save(); commit(); render();
        }, 180);
      }
      handle.addEventListener('dblclick', function (e) { e.stopPropagation(); remove(); });
      // Right-click (or the keyboard Menu key / Shift+F10) opens a small menu: colour (pin) or remove (corner).
      handle.addEventListener('contextmenu', function (e) {
        if (e.target.tagName === 'INPUT') return;   // keep the normal text menu in label boxes
        e.preventDefault(); e.stopPropagation();
        var hb = handle.getBoundingClientRect(), sr = stage.getBoundingClientRect();
        // Keyboard-triggered events report 0,0: anchor to the handle instead.
        var cx = e.clientX || hb.left + hb.width / 2, cy = e.clientY || hb.top + hb.height / 2;
        openMenu(cx - sr.left, cy - sr.top, handle, isPin, item, remove);
      });
      handle.addEventListener('keydown', function (e) {
        if (e.target !== handle) return;   // typing in the pin label must not move or delete the pin
        var step = e.shiftKey ? 0.02 : 0.005, k = e.key;
        if (!isPin && (k === 'Delete' || k === 'Backspace')) { e.preventDefault(); remove(); return; }
        if (isPin && (k === '+' || k === '=' || k === '-' || k === '_')) {   // resize within the allowed range
          e.preventDefault();
          item.size = clampSize((item.size || 1) + (k === '+' || k === '=' ? PIN_STEP : -PIN_STEP));
          host.style.setProperty('--lp-pin-size', item.size); save(); commitSoon(); return;
        }
        var d = { ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step] }[k];
        if (!d) return;
        e.preventDefault();
        item.x = Math.min(1, Math.max(0, item.x + d[0])); item.y = Math.min(1, Math.max(0, item.y + d[1]));
        layout(); save(); commitSoon();
      });
    }

    var menu = null, menuOpener = null;
    function closeMenu(restoreFocus) {
      if (!menu) return;
      var m = menu; menu = null;
      m.classList.add('lp-out'); setTimeout(function () { m.remove(); }, 150);
      if (restoreFocus && menuOpener && menuOpener.isConnected) menuOpener.focus({ preventScroll: true });
    }
    function openMenu(x, y, opener, isPin, item, remove) {
      closeMenu(false);
      menuOpener = opener;
      menu = el('div', 'lp-menu lp-in', stage);
      menu.setAttribute('role', 'menu');
      if (isPin) {
        swatchGroup(menu, 'Pin colour', function () { return item.color || DEFAULT_PIN; }, function (c) {
          item.color = c; render(); save(); commit();
        });
        var row = el('label', 'lp-size-row', menu); row.appendChild(document.createTextNode('Size'));
        var range = el('input', '', row); range.type = 'range'; range.min = PIN_MIN; range.max = PIN_MAX; range.step = PIN_STEP;
        range.value = clampSize(item.size || 1); range.setAttribute('aria-label', 'Pin size');
        var shown = el('output', '', row); shown.textContent = Math.round(range.value * 100) + '%';
        range.addEventListener('input', function () {   // live preview while dragging the slider
          item.size = clampSize(range.value); shown.textContent = Math.round(item.size * 100) + '%';
          if (pins[0]) pins[0].style.setProperty('--lp-pin-size', item.size);   // current element: a colour pick rebuilds the pin
          save();
        });
        range.addEventListener('change', commit);       // one undo step per adjustment
      } else {
        var rm = el('button', 'lp-menu-item', menu); rm.type = 'button'; rm.setAttribute('role', 'menuitem');
        rm.textContent = 'Remove corner';
        rm.addEventListener('click', function (e) { e.stopPropagation(); closeMenu(false); remove(); });
      }
      // Place near the pointer, kept inside the image.
      var w = menu.offsetWidth, h = menu.offsetHeight;
      menu.style.left = Math.max(4, Math.min(x, stage.clientWidth - w - 4)) + 'px';
      menu.style.top = Math.max(4, Math.min(y, stage.clientHeight - h - 4)) + 'px';
      menu.querySelector('button').focus({ preventScroll: true });
    }
    document.addEventListener('pointerdown', function (e) { if (menu && !menu.contains(e.target)) closeMenu(false); });
    document.addEventListener('keydown', function (e) { if (menu && e.key === 'Escape') { e.preventDefault(); closeMenu(true); } });
    window.addEventListener('scroll', function () { closeMenu(false); }, true);
    window.addEventListener('resize', function () { closeMenu(false); });

    function textInput(cls, max, value, ph, onChange, label) {
      var i = el('input', cls); i.setAttribute('aria-label', label); i.type = 'text'; i.maxLength = max; i.value = value; i.placeholder = ph;
      var fit = function () { i.style.width = Math.max(ph.length, i.value.length) + 2 + 'ch'; };
      i.addEventListener('input', function () { onChange(i.value); fit(); save(); });
      i.addEventListener('change', commit);
      // Enter would otherwise submit the whole Wagtail form; just commit the text.
      i.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); i.blur(); } });
      i.addEventListener('pointerdown', function (e) { e.stopPropagation(); });
      i.addEventListener('click', function (e) { e.stopPropagation(); });
      i.addEventListener('dblclick', function (e) { e.stopPropagation(); });
      fit();
      return i;
    }

    function render() {
      layer.innerHTML = ''; pts = []; edges = []; pins = [];
      if (!data) { poly.setAttribute('points', ''); return; }
      var b = data.boundary, n = b.length;
      b.forEach(function (p, i) {
        if (i < (n > 2 ? n : n - 1)) {
          var d = textInput('lp-dim', MAX_DIM, p.dim || '', 'e.g. 45 m', function (v) { p.dim = v; }, 'Edge dimension (max ' + MAX_DIM + ' characters)');
          layer.appendChild(d); edges.push(d);
        }
      });
      b.forEach(function (p) {
        var h = el('div', 'lp-pt' + (fresh.has(p) ? ' lp-in' : ''), layer);
        drag(h, p, h); pts.push(h);
      });
      data.pins.forEach(function (p) {
        var host = el('div', 'lp-pin' + (fresh.has(p) ? ' lp-in' : ''), layer);
        if (p.color) host.style.setProperty('--lp-pin', p.color);
        host.style.setProperty('--lp-pin-size', clampSize(p.size));
        var lab = textInput('lp-pin-label', MAX_LABEL, p.label || '', 'Label', function (v) { p.label = v; }, 'Pin label (max ' + MAX_LABEL + ' characters)');
        host.appendChild(lab);
        el('i', 'fas fa-map-marker-alt lp-pin-icon', host).setAttribute('aria-hidden', 'true');
        drag(host, p, host); pins.push(host);
      });
      layout();
      b.concat(data.pins).forEach(function (p) { fresh.delete(p); });
    }

    stage.addEventListener('click', function (e) {
      if (!data || e.target.closest('.lp-pt, .lp-pin, .lp-dim, .lp-menu')) return;
      var rect = stage.getBoundingClientRect();
      var item = { x: (e.clientX - rect.left) / rect.width, y: (e.clientY - rect.top) / rect.height, dim: '' };
      fresh.add(item); data.boundary.push(item);
      save(); commit(); render();
    });

    btnC.onclick = function () {
      if (!data || !data.boundary.length) return;
      if (!confirm('Remove all boundary corners on this photo? The pin is kept.')) return;
      layer.classList.add('lp-out');
      setTimeout(function () {
        layer.classList.remove('lp-out');
        data.boundary = []; save(); commit(); render();
      }, 180);
    };
    btnX.onclick = function () {   // un-annotate this photo (undoable): the plain photo is shown again publicly
      if (!active) return;
      if (!confirm('Remove all annotations from this photo? You can undo this.')) return;
      delete all[active]; active = ''; data = null;
      save(); commit(); applyPhoto(); refreshSlots(); render();
    };

    // ── Photo strip, live image lookup and land-only gating ──
    var pending = {};
    function slotId(s) { var i = document.getElementById('id_' + s); return i ? i.value : ''; }
    function info(s) { var c = cfg.images[s]; return c && String(c.id) === slotId(s) ? c : null; }
    function fetchInfo(s) {   // a photo chosen this session isn't saved yet, so ask the server for its URL
      var id = slotId(s);
      if (!id || pending[s] === id) return;
      pending[s] = id;
      fetch(cfg.endpoint.replace(/0\/$/, id + '/'), { credentials: 'same-origin' })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (j) {
          if (j && String(j.id) === slotId(s)) { cfg.images[s] = j; refreshSlots(); if (active === s) applyPhoto(); }
        })
        .catch(function () { pending[s] = ''; });   // a later change/refresh can retry
    }
    function applyPhoto() {
      var c = active && info(active), showing = !!(c && data);
      box.hidden = !showing;
      emptyState.hidden = showing;
      btnClose.hidden = !active;
      subtitle.hidden = !showing;
      subtitle.textContent = showing ? (cfg.slots.filter(function (sl) { return sl[0] === active; })[0] || ['', ''])[1] : '';
      if (c && img.getAttribute('src') !== c.url) img.src = c.url;
      if (data) stage.style.setProperty('--lp-boundary', data.color);
      boundarySw.repaint();
    }
    function selectPhoto(s) {   // switching is not an edit: nothing is cleared, each photo keeps its own annotations
      if (s === active) return;
      closeMenu(false);
      active = s;
      if (s && !all[s]) {   // first time on this photo: it becomes annotated, with the pin placed in the centre
        all[s] = normEntry(null); fresh.add(all[s].pins[0]);
        data = all[s]; save(); commit();
      } else { data = s ? all[s] : null; markDirty(300); }   // remember which photo was open
      applyPhoto(); refreshSlots(); render();
      if (s) root.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth', block: 'nearest' });   // matters when the workspace sits below the cards
    }
    // Each photo card gets its own Annotate button; the card being edited is highlighted, annotated ones are ticked.
    var slotUI = {};
    cfg.slots.forEach(function (sl) {
      var inp = document.getElementById('id_' + sl[0]), card = inp && inp.closest('.w-panel__wrapper');
      if (!card) return;
      card.classList.add('lp-slot');
      var actions = el('div', 'lp-slot-actions', card);
      var b = el('button', 'lp-annotate', actions); b.type = 'button';
      b.addEventListener('click', function () { selectPhoto(active === sl[0] ? '' : sl[0]); });
      slotUI[sl[0]] = { card: card, btn: b, actions: actions };
    });
    function refreshSlots() {
      var any = false;
      cfg.slots.forEach(function (sl) {
        var ui = slotUI[sl[0]], has = !!slotId(sl[0]);
        if (has) { any = true; if (!info(sl[0])) fetchInfo(sl[0]); }
        if (!ui) return;
        var isActive = active === sl[0], done = !!all[sl[0]];
        ui.card.classList.toggle('is-annotating', isActive);
        ui.card.classList.toggle('is-annotated', done);
        ui.btn.hidden = !has; ui.actions.hidden = !has;   // no photo, no button (and no empty gap)
        ui.btn.setAttribute('aria-pressed', isActive);
        ui.btn.textContent = isActive ? 'Editing — click to close' : (done ? '✓ Annotated · Edit' : '＋ Annotate this photo');
        ui.btn.setAttribute('aria-label', (isActive ? 'Close annotations for ' : 'Annotate ') + sl[1] + (done ? ' (already annotated)' : ''));
      });
      var loading = active && !info(active);
      emptyState.classList.toggle('is-loading', !!loading);
      if (loading) { emptyTitle.textContent = 'Loading photo…'; emptyText.textContent = ''; }
      else if (any) { emptyTitle.textContent = 'Pick a photo to annotate'; emptyText.textContent = 'Press “Annotate” on a photo to draw its plot boundary, dimensions and a location pin. Customers see the drawing on the project page.'; }
      else { emptyTitle.textContent = 'Add a photo first'; emptyText.textContent = 'Choose a photo on the left, then annotate it here.'; }
      if (active && !slotId(active)) { active = ''; data = null; applyPhoto(); render(); markDirty(300); }   // the open photo was removed from its slot
    }
    function applyGate() {
      var sid = (document.getElementById('id_service') || {}).value, on = cfg.land.indexOf(String(sid)) >= 0;
      wrap.style.display = on ? '' : 'none';
      // The photos panel becomes a two-column workspace only for services with annotations enabled.
      if (host) { host.classList.toggle('lp-photos-host', on); if (panel) panel.classList.toggle('lp-photos-grid', on); if (formWidth) formWidth.classList.toggle('lp-wide', on); }
      if (wsWrap) wsWrap.classList.toggle('lp-workspace', on);
    }
    document.addEventListener('change', function (e) {   // photo/service choosers fire change on their hidden inputs
      var id = e.target && e.target.id;
      if (id === 'id_service') applyGate();
      else if (/^id_photo_(main|[1-6])$/.test(id)) { refreshSlots(); applyPhoto(); }
    });

    updateHistoryButtons();
    refreshSlots(); applyPhoto(); applyGate(); render();
  }

  function boot() { document.querySelectorAll('.lp-editor').forEach(init); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
