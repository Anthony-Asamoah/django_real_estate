// The CMS is built for desktop. On phone-sized screens, cover it with a notice.
(function () {
    const query = window.matchMedia('(max-width: 767.98px)');
    let overlay = null;

    function build() {
        const el = document.createElement('div');
        el.setAttribute('role', 'alertdialog');
        el.setAttribute('aria-label', 'Desktop required');
        el.style.cssText = 'position:fixed;inset:0;z-index:2147483647;display:flex;flex-direction:column;' +
            'align-items:center;justify-content:center;gap:1rem;padding:2rem;text-align:center;' +
            'background:#10284e;color:#fff;font-family:system-ui,sans-serif;line-height:1.5';
        el.innerHTML =
            '<h1 style="margin:0;font-size:1.4rem">Please use a computer</h1>' +
            '<p style="margin:0;max-width:22rem;opacity:.85">The website admin is designed for desktop and ' +
            'laptop screens. Open it on a larger screen to manage the site.</p>' +
            '<a href="/" style="margin-top:.5rem;padding:.7rem 1.4rem;border-radius:6px;background:#30caa0;' +
            'color:#10284e;font-weight:700;text-decoration:none">Go to the website</a>';
        return el;
    }

    function apply() {
        if (query.matches && !overlay) {
            overlay = build();
            document.body.appendChild(overlay);
            document.documentElement.style.overflow = 'hidden';
        } else if (!query.matches && overlay) {
            overlay.remove();
            overlay = null;
            document.documentElement.style.overflow = '';
        }
    }

    document.addEventListener('DOMContentLoaded', apply);
    query.addEventListener('change', apply);
})();
