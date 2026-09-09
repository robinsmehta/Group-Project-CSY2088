let allJobs = [];

        document.addEventListener('DOMContentLoaded', async () => {
            await redirectIfNotLoggedIn('company');
            renderNavbar('dashboard');
            renderFooter();

            const user = getLoggedInUser();
            if (user) {
                const nameEl = document.getElementById('company-name-display');
                if (nameEl) nameEl.textContent = user.company_name || user.name || 'Employer';

                const descEl = document.getElementById('company-desc-display');
                if (descEl && user.description) descEl.textContent = user.description;

                const bannerEl = document.getElementById('pending-approval-banner');
                if (bannerEl && (user.status === 'pending' || user.status === 'rejected')) {
                    bannerEl.style.display = 'inline-flex';
                }
            }

            await loadCompanyJobs();

            const searchInput = document.getElementById('job-search-input');
            if (searchInput) searchInput.addEventListener('input', renderFilteredJobs);
        });

        async function loadCompanyJobs() {
            const tbody = document.getElementById('jobs-table-body');
            if (tbody) tbody.innerHTML = `<tr><td colspan="6" class="dashboard-style-d7eb25">Loading...</td></tr>`;

            const user = getLoggedInUser();
            const { ok, data } = await apiGetJobs();
            const jobs = ok ? (data.jobs || (Array.isArray(data) ? data : [])) : null;

            if (!ok || !jobs) {
                if (tbody) tbody.innerHTML = `<tr><td colspan="6" class="dashboard-style-ff776f">Failed to load jobs. Make sure the backend is running.</td></tr>`;
                return;
            }

            if (user) {
                const compId = user.id || user.company_id;
                allJobs = jobs.filter(job => job.company_id == user.id || job.company_id == user.company_id || String(job.company_id) === String(compId));
            } else {
                allJobs = jobs;
            }

            const activeCount = allJobs.filter(j => j.status !== 'closed').length;
            const appCount = allJobs.reduce((acc, curr) => acc + (curr.application_count || 0), 0);

            const activeEl = document.getElementById('stat-active-listings');
            if (activeEl) activeEl.textContent = activeCount;
            const appEl = document.getElementById('stat-total-applicants');
            if (appEl) appEl.textContent = appCount;

            renderFilteredJobs();
        }

        function renderFilteredJobs() {
            const search = (document.getElementById('job-search-input')?.value || '').toLowerCase().trim();
            const filtered = allJobs.filter(job =>
                !search ||
                (job.title || '').toLowerCase().includes(search) ||
                (job.location || '').toLowerCase().includes(search)
            );

            const tbody = document.getElementById('jobs-table-body');

            if (filtered.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" class="dashboard-style-d7eb25">No job postings found. <a href="post-job.html" class="dashboard-style-61fc2b">Post a job →</a></td></tr>`;
                return;
            }

            tbody.innerHTML = filtered.map(job => {
                const isActive = job.status !== 'closed';
                const statusColor = isActive ? '#10B981' : '#6B7280';
                const statusBg = isActive ? '#D1FAE5' : '#F3F4F6';
                const statusText = isActive ? 'ACTIVE' : 'CLOSED';
                const category = job.category || 'Other';
                
                return `
                <tr class="dashboard-style-093d93">
                    <td class="dashboard-style-a06415">
                        <div class="dashboard-style-8a525a">${escHtml(job.title)}</div>
                        <div class="dashboard-style-1aa5c4">ENGINEERING</div>
                    </td>
                    <td class="dashboard-style-14bdd8">
                        ${escHtml(category)}
                    </td>
                    <td class="dashboard-style-a06415">
                        <span class="company-status-badge" style="background: ${statusBg}; color: ${statusColor};">
                            ${statusText}
                        </span>
                    </td>
                    <td class="dashboard-style-acc1d6">
                        ${typeof job.application_count === 'number' ? job.application_count : '0'}
                    </td>
                    <td class="dashboard-style-0ecc32">
                        ${timeAgo(job.created_at)}
                    </td>
                    <td class="dashboard-style-a06415">
                        <a href="post-job.html?id=${job.id}" class="dashboard-style-004d0a">
                            Edit
                        </a>
                    </td>
                </tr>
                `;
            }).join('');
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
