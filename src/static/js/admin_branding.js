(function () {
    if (!window.location.pathname.includes('/brandingsettings/')) return;

    function getCsrfToken() {
        var match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
    }

    // Build a preset swatch button element (used when inserting newly saved presets)
    function buildSwatch(name, primary, secondary) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'color-swatch-btn';
        btn.dataset.primary = primary;
        btn.dataset.secondary = secondary;
        btn.title = name;
        btn.innerHTML =
            '<span style="display:flex;width:38px;height:38px;border-radius:50%;' +
            'overflow:hidden;flex-shrink:0;box-shadow:0 1px 4px rgba(0,0,0,.35)">' +
            '<span style="display:block;width:50%;height:100%;background:' + primary + '"></span>' +
            '<span style="display:block;width:50%;height:100%;background:' + secondary + '"></span>' +
            '</span>' +
            '<span class="swatch-label">' + name + '</span>';
        return btn;
    }

    // Attach a monospace hex text input next to each native color picker
    function attachHexCompanion(pickerId) {
        var picker = document.getElementById(pickerId);
        if (!picker) return;

        var wrap = document.createElement('div');
        wrap.className = 'color-input-group';
        picker.parentNode.insertBefore(wrap, picker);
        wrap.appendChild(picker);

        var hex = document.createElement('input');
        hex.type = 'text';
        hex.className = 'color-hex-companion';
        hex.value = picker.value;
        hex.maxLength = 7;
        hex.placeholder = '#000000';
        hex.setAttribute('aria-label', 'Hex color value');
        wrap.appendChild(hex);

        // Picker → hex text
        picker.addEventListener('input', function () { hex.value = picker.value; });

        // Hex text → picker (only when valid)
        hex.addEventListener('input', function () {
            if (/^#[0-9a-fA-F]{6}$/.test(hex.value)) {
                picker.value = hex.value;
                picker.dispatchEvent(new Event('input', { bubbles: true }));
                picker.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });

        // Snap back to last valid value on blur
        hex.addEventListener('blur', function () {
            if (!/^#[0-9a-fA-F]{6}$/.test(hex.value)) {
                hex.value = picker.value;
            }
        });
    }

    // Set both pickers (and their hex companions) to the given colors
    function applyColors(primary, secondary) {
        var primaryInput = document.getElementById('id_primary_color');
        var secondaryInput = document.getElementById('id_secondary_color');

        function setColor(input, value) {
            if (!input || !value) return;
            input.value = value;
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
        }

        setColor(primaryInput, primary);
        setColor(secondaryInput, secondary);
    }

    // Click: preset swatch or history restore → fill pickers
    document.addEventListener('click', function (e) {
        var btn = e.target.closest('[data-primary]');
        if (!btn) return;
        // Ignore if it's the form itself somehow
        if (btn.tagName === 'FORM') return;
        applyColors(btn.dataset.primary, btn.dataset.secondary);
    });

    // Click: Save as Preset button
    document.addEventListener('click', function (e) {
        if (!e.target.classList.contains('save-preset-btn')) return;

        var form = e.target.closest('.save-preset-form');
        if (!form) return;

        var nameInput = form.querySelector('.preset-name-input');
        var feedback = form.querySelector('.save-preset-feedback');
        var submitBtn = e.target;
        var name = nameInput.value.trim();

        if (!name) {
            feedback.textContent = 'Enter a name first.';
            feedback.className = 'save-preset-feedback feedback-error';
            nameInput.focus();
            return;
        }

        var primary = (document.getElementById('id_primary_color') || {}).value || '';
        var secondary = (document.getElementById('id_secondary_color') || {}).value || '';

        submitBtn.disabled = true;
        feedback.textContent = 'Saving…';
        feedback.className = 'save-preset-feedback';

        fetch('/cms/branding-preset/save/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ name: name, primary_color: primary, secondary_color: secondary }),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                submitBtn.disabled = false;
                if (data.status === 'ok') {
                    feedback.textContent = 'Saved!';
                    feedback.className = 'save-preset-feedback feedback-ok';
                    nameInput.value = '';

                    var row = document.querySelector('.presets-row');
                    if (row) {
                        var existing = row.querySelector('[title="' + name + '"]');
                        if (existing) {
                            var halves = existing.querySelectorAll('span > span');
                            if (halves[0]) halves[0].style.background = primary;
                            if (halves[1]) halves[1].style.background = secondary;
                            existing.dataset.primary = primary;
                            existing.dataset.secondary = secondary;
                        } else {
                            row.appendChild(buildSwatch(name, primary, secondary));
                        }
                    }

                    setTimeout(function () { feedback.textContent = ''; }, 2500);
                } else {
                    feedback.textContent = data.message || 'Something went wrong.';
                    feedback.className = 'save-preset-feedback feedback-error';
                }
            })
            .catch(function () {
                submitBtn.disabled = false;
                feedback.textContent = 'Request failed.';
                feedback.className = 'save-preset-feedback feedback-error';
            });
    });

    // Init on DOM ready
    document.addEventListener('DOMContentLoaded', function () {
        attachHexCompanion('id_primary_color');
        attachHexCompanion('id_secondary_color');
    });
})();
