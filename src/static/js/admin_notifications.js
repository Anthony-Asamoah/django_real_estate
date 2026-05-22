(function () {
    const COUNTS_URL = '/cms/notifications/counts/';
    const MARK_READ_URL = '/cms/notifications/mark-read/';

    const HREF_MAP = {
        project: '/cms/snippets/inquiries/projectinquiry/',
        general: '/cms/snippets/inquiries/generalinquiry/',
        testimonial: '/cms/snippets/pages/testimonial/',
    };

    function getCsrf() {
        const match = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
        return match ? decodeURIComponent(match.split('=')[1]) : '';
    }

    async function fetchCounts() {
        try {
            const res = await fetch(COUNTS_URL, { credentials: 'same-origin' });
            return res.ok ? await res.json() : null;
        } catch { return null; }
    }

    function updateBadges(counts) {
        document.querySelectorAll('.notif-badge').forEach(el => el.remove());
        for (const [key, count] of Object.entries(counts)) {
            if (!count) continue;
            const href = HREF_MAP[key];
            if (!href) continue;
            const link = document.querySelector(`a[href="${href}"]`);
            if (!link) continue;
            const badge = document.createElement('span');
            badge.className = 'notif-badge';
            badge.textContent = count;
            link.appendChild(badge);
        }
    }

    async function markRead(model) {
        const body = new FormData();
        body.append('model', model);
        try {
            const res = await fetch(MARK_READ_URL, {
                method: 'POST',
                credentials: 'same-origin',
                headers: { 'X-CSRFToken': getCsrf() },
                body,
            });
            return res.ok ? await res.json() : null;
        } catch { return null; }
    }

    document.addEventListener('click', async (e) => {
        const btn = e.target.closest('.unread-mark-btn');
        if (!btn) return;

        const model = btn.dataset.model;
        btn.disabled = true;
        btn.textContent = 'Marking…';

        const result = await markRead(model);
        if (result?.ok) {
            btn.closest('.unread-row')?.remove();
            const panel = document.querySelector('.unread-notifications-panel');
            if (panel && !panel.querySelector('.unread-row')) panel.remove();

            const counts = await fetchCounts();
            if (counts) updateBadges(counts);
        } else {
            btn.disabled = false;
            btn.textContent = 'Mark all read';
        }
    });

    async function poll() {
        const counts = await fetchCounts();
        if (counts) updateBadges(counts);
    }

    function waitForSidebar(cb) {
        if (document.querySelector('a[href^="/cms/snippets/"]')) {
            cb();
            return;
        }
        const obs = new MutationObserver(() => {
            if (document.querySelector('a[href^="/cms/snippets/"]')) {
                obs.disconnect();
                cb();
            }
        });
        obs.observe(document.body, { childList: true, subtree: true });
    }

    function start() {
        waitForSidebar(async () => {
            await poll();
            setInterval(poll, 60_000);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }
})();
