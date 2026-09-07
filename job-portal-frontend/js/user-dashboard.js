// User dashboard logic.
// Depends on: config.js, shared.js, api.js.

document.addEventListener('DOMContentLoaded', async () => {
    await redirectIfNotLoggedIn('user');
    renderNavbar('dashboard');
    renderFooter();
    await loadApplicationStats();
    await initKanbanBoard();
});

async function initKanbanBoard() {
    document.querySelectorAll('.kanban-column').forEach(col => {
        col.querySelector('.kanban-cards-container').innerHTML = '<div style="text-align:center;padding:20px;color:#9CA3AF;font-size:12px;">Loading...</div>';
    });

    sessionStorage.removeItem('user_kanban_applications');
    const { ok, data } = await apiGetMyApplications();
    const applications = ok ? (data?.applications || []) : [];
    if (!applications.length) {
        showEmpty(
            'kanban-board',
            "You haven't applied to any jobs yet",
            'Browse available jobs and submit your first application.',
            '<a href="../jobs/listing.html">Browse Jobs</a>'
        );
        return;
    }

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
    const { ok, data } = await apiGetMyApplicationStats();
    if (!ok) return;

    document.getElementById('stat-total-applied').textContent = data.total_applied || 0;
    document.getElementById('stat-in-review').textContent = data.under_review || 0;
    document.getElementById('stat-shortlisted').textContent = data.shortlisted || 0;
    document.getElementById('stat-rejected').textContent = data.rejected || 0;
}

function renderKanbanCards(apps) {
    const statuses = ['applied', 'under_review', 'shortlisted', 'rejected'];
    const counts = { applied: 0, under_review: 0, shortlisted: 0, rejected: 0 };

    statuses.forEach(st => {
        const container = document.getElementById(`col-${st}`);
        if (container) container.innerHTML = '';
    });

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
