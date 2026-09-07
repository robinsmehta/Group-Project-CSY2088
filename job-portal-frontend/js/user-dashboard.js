// User dashboard logic.
// Depends on: config.js, shared.js, api.js.

let applicationRefreshInProgress = false;

document.addEventListener('DOMContentLoaded', async () => {
    await redirectIfNotLoggedIn('user');
    renderNavbar('dashboard');
    renderFooter();
    await refreshApplicationData();
});

window.addEventListener('focus', refreshApplicationData);
window.addEventListener('pageshow', refreshApplicationData);

async function refreshApplicationData() {
    if (applicationRefreshInProgress) return;

    applicationRefreshInProgress = true;
    try {
        await Promise.all([loadApplicationStats(), initKanbanBoard()]);
    } finally {
        applicationRefreshInProgress = false;
    }
}

async function initKanbanBoard() {
    document.querySelectorAll('.kanban-column').forEach(col => {
        col.querySelector('.kanban-cards-container').innerHTML = '<div style="text-align:center;padding:20px;color:#9CA3AF;font-size:12px;">Loading...</div>';
    });

    sessionStorage.removeItem('user_kanban_applications');
    const { ok, data } = await apiGetMyApplications();
    const applications = ok ? (data?.applications || []) : [];

    const apps = applications.map(app => ({
        id: app.id,
        position: app.job?.title || app.job_title || 'Unknown Position',
        company: app.job?.company_name || app.company_name || 'Unknown Company',
        applied_date: app.applied_at || app.created_at || '',
        status: app.status || 'applied'
    }));

    renderKanbanCards(apps);
}

async function loadApplicationStats() {
    const token = sessionStorage.getItem('access_token')
        || sessionStorage.getItem('jwt_token')
        || localStorage.getItem('access_token')
        || localStorage.getItem('jwt_token');
    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    try {
        const response = await fetch(`${API_BASE_URL}/applications/stats?t=${Date.now()}`, {
            method: 'GET',
            headers,
            credentials: 'include',
            cache: 'no-store'
        });
        if (!response.ok) return;

        const data = await response.json();
        document.getElementById('stat-total-applied').textContent = data.total || 0;
        document.getElementById('stat-in-review').textContent = data.in_review || 0;
        document.getElementById('stat-shortlisted').textContent = data.shortlisted || 0;
        document.getElementById('stat-rejected').textContent = data.rejected || 0;
    } catch (error) {
        console.error('Unable to load application stats:', error);
    }
}

function renderKanbanCards(apps) {
    const statuses = ['applied', 'under_review', 'shortlisted', 'rejected'];
    const counts = { applied: 0, under_review: 0, shortlisted: 0, rejected: 0 };
    const emptyState = document.getElementById('applications-empty-state');

    document.querySelectorAll('.kanban-cards-container').forEach(container => {
        container.innerHTML = '';
    });

    if (emptyState) emptyState.hidden = apps.length !== 0;

    apps.forEach(app => {
        const st = app.status || 'applied';
        if (counts[st] !== undefined) counts[st]++;

        const container = document.getElementById(`col-${st}`);
        if (!container) return;

        const card = document.createElement('div');
        card.className = 'kanban-card';
        card.dataset.id = app.id;
        card.dataset.status = st;
        card.innerHTML = `
            <div class="kanban-card-company">${escapeHtml(app.company || 'Company')}</div>
            <div class="kanban-card-position">${escapeHtml(app.position || 'Position')}</div>
            <div>${createStatusBadge(st)}</div>
            <div class="kanban-card-footer">
                <span>Applied: ${formatDate(app.applied_date)}</span>
            </div>
        `;
        container.appendChild(card);
    });

    statuses.forEach(st => {
        const countEl = document.getElementById(`count-${st}`);
        if (countEl) countEl.textContent = counts[st] || 0;
    });
}

function createStatusBadge(status) {
    const labels = {
        applied: 'Applied',
        under_review: 'Under Review',
        shortlisted: 'Shortlisted',
        rejected: 'Rejected'
    };
    const classes = {
        applied: 'status-badge-applied',
        under_review: 'status-badge-under-review',
        shortlisted: 'status-badge-shortlisted',
        rejected: 'status-badge-rejected'
    };
    const label = labels[status] || status.replace(/_/g, ' ');
    const cls = classes[status] || 'status-badge-default';
    return `<span class="status-badge ${cls}">${escapeHtml(label)}</span>`;
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
