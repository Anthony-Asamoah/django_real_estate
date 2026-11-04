// The CMS is built for larger screens. On smartphones (not tablets), cover it with a notice.
// Layer 1: device type. Layer 2: viewport width under 600px (the narrowest tablets are ~600px).
(function () {
    const narrow = window.matchMedia('(max-width: 599.98px)');
    let overlay = null;
    // Width can't tell a phone from a small tablet, so go by device. Android tablets omit "Mobile"
    // from their user agent and iPadOS reports as a Mac, so neither matches.
    const ua = navigator.userAgent;
    const isPhone = (navigator.userAgentData && navigator.userAgentData.mobile) ||
        /iPhone|iPod|Android.*Mobile|Windows Phone|BlackBerry|webOS/i.test(ua);

    function build() {
        const el = document.createElement('div');
        el.setAttribute('role', 'alertdialog');
        el.setAttribute('aria-label', 'Desktop required');
        el.style.cssText = 'position:fixed;inset:0;z-index:2147483647;display:flex;flex-direction:column;' +
            'align-items:center;justify-content:center;gap:1rem;padding:2rem;text-align:center;' +
            'background:#10284e;color:#fff;font-family:system-ui,sans-serif;line-height:1.5';
        el.innerHTML =
            '<h1 style="margin:0;font-size:1.4rem;color:#fff;text-transform:none">Please use a computer</h1>' +
            '<p style="margin:0;max-width:22rem;opacity:.85">The website admin is designed for desktop and ' +
            'laptop screens. Open it on a larger screen to manage the site.</p>' +
            '<a href="/" style="margin-top:.5rem;padding:.7rem 1.4rem;border-radius:6px;background:#30caa0;' +
            'color:#10284e;font-weight:700;text-decoration:none">Go to the website</a>';
        return el;
    }

    function apply() {
        if ((isPhone || narrow.matches) && !overlay) {
            overlay = build();
            document.body.appendChild(overlay);
            document.documentElement.style.overflow = 'hidden';
        } else if (!isPhone && !narrow.matches && overlay) {
            overlay.remove();
            overlay = null;
            document.documentElement.style.overflow = '';
        }
    }

    document.addEventListener('DOMContentLoaded', apply);
    narrow.addEventListener('change', apply);
})();
