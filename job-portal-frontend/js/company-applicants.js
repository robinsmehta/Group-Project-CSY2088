let allApplicants = [];

        document.addEventListener('DOMContentLoaded', async () => {
            await redirectIfNotLoggedIn('company');
            renderNavbar('applicants');
            renderFooter();
            await loadApplicants();

            document.getElementById('applicant-search-input')?.addEventListener('input', renderFilteredApplicants);
        });

        async function loadApplicants() {
            const tbody = document.getElementById('applicants-table-body');
            tbody.innerHTML = `<tr><td colspan="5" class="dashboard-style-d7eb25">Loading...</td></tr>`;

            const { ok, data } = await apiGetCompanyApplicants();

            if (!ok) {
                tbody.innerHTML = `<tr><td colspan="5" class="dashboard-style-ff776f">Failed to load applicants.</td></tr>`;
                return;
            }

            allApplicants = data.applications || (Array.isArray(data) ? data : []);
            renderFilteredApplicants();
        }

        function renderFilteredApplicants() {
            const search = (document.getElementById('applicant-search-input')?.value || '').toLowerCase().trim();
            const filtered = allApplicants.filter(app =>
                !search ||
                (app.applicant_name || '').toLowerCase().includes(search) ||
                (app.job_title || '').toLowerCase().includes(search)
            );

            const tbody = document.getElementById('applicants-table-body');

            if (filtered.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="dashboard-style-d7eb25">No applicants found.</td></tr>`;
                return;
            }

            tbody.innerHTML = filtered.map(app => `
                <tr class="dashboard-style-093d93">
                    <td class="dashboard-style-79d501">
                        <div class="dashboard-style-8a525a">${escHtml(app.applicant_name || 'Anonymous')}</div>
                        <div class="dashboard-style-70a3f8">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                            ${escHtml(app.applicant_email || '')}
                        </div>
                    </td>
                    <td class="dashboard-style-15047d">${escHtml(app.job_title || 'Unknown Job')}</td>
                    <td class="dashboard-style-ea4b92">${app.created_at ? new Date(app.created_at).toISOString().split('T')[0] : 'N/A'}</td>
                    <td class="dashboard-style-d8450a" data-application-id="${app.id}">${getStatusBadge(app.status)}</td>
                    <td class="dashboard-style-79d501">
                        <button data-resume-url="${app.resume_url || '#'}" class="dashboard-style-c4b619">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                        </button>
                    </td>
                </tr>
            `).join('');
        }

        document.getElementById('applicants-table-body')?.addEventListener('click', (event) => {
            const statusCell = event.target.closest('[data-application-id]');
            if (statusCell) openModal(Number(statusCell.dataset.applicationId));
            const resumeButton = event.target.closest('button[data-resume-url]');
            if (resumeButton) window.open(resumeButton.dataset.resumeUrl, '_blank');
        });

        document.getElementById('close-applicant-modal')?.addEventListener('click', closeModal);
        document.querySelectorAll('[data-status]').forEach(button => {
            button.addEventListener('click', () => updateStatus(button.dataset.status));
        });

        function getStatusBadge(status) {
            const map = {
                pending:      ['#F3F4F6', '#6B7280', 'Pending'],
                applied:      ['#DBEAFE', '#1D4ED8', 'Applied'],
                under_review: ['#FCE7F3', '#BE185D', 'Under Review'],
                reviewing:    ['#FCE7F3', '#BE185D', 'Reviewing'],
                interview:    ['#FEF3C7', '#B45309', 'Interview'],
                shortlisted:  ['#F3E8FF', '#7E22CE', 'Shortlisted'],
                rejected:     ['#F3F4F6', '#9CA3AF', 'Rejected'],
            };
            const s = (status || 'applied').toLowerCase();
            const [bg, color, text] = map[s] || map.applied;
            return `<span class="applicant-badge" style="background: ${bg}; color: ${color};">${text}</span>`;
        }

        function openModal(id) {
            const app = allApplicants.find(a => a.id === id);
            if (!app) return;
            document.getElementById('modal-application-id').value = id;
            document.getElementById('modal-cover-letter').textContent = app.cover_letter || 'No cover letter provided.';
            document.getElementById('applicant-modal').classList.add('open');
        }

        function closeModal() {
            document.getElementById('applicant-modal').classList.remove('open');
        }

        async function updateStatus(newStatus) {
            const id = document.getElementById('modal-application-id').value;
            if (!id) return;

            const { ok, data } = await apiUpdateApplicationStatus(id, newStatus);
            if (ok) {
                showToast(`Status updated to ${newStatus}`, 'success');
                const app = allApplicants.find(a => a.id == id);
                if (app) app.status = newStatus;
                renderFilteredApplicants();
                closeModal();
            } else {
                showToast(data.error || 'Failed to update status', 'error');
            }
        }

        function escHtml(str) {
            const d = document.createElement('div');
            d.textContent = str || '';
            return d.innerHTML;
        }

        function timeAgo(isoStr) {
            if (!isoStr) return 'Recently';
            const diff = Date.now() - new Date(isoStr).getTime();
            const mins = Math.floor(diff / 60000);
            if (mins < 60) return `${mins}m ago`;
            const hrs = Math.floor(mins / 60);
            if (hrs < 24) return `${hrs}h ago`;
            return `${Math.floor(hrs / 24)}d ago`;
        }
