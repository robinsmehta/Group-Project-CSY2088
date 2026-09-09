document.addEventListener('DOMContentLoaded', async () => {
            const user = getLoggedInUser();
            if (!user || user.role !== 'admin') {
                window.location.href = resolveSitePath('auth/login.html');
                return;
            }
            renderNavbar('approvals');
            renderFooter();

            const searchInput = document.getElementById('company-search-input');
            function debounce(fn, delay) {
                let timer = null;
                return function(...args) { clearTimeout(timer); timer = setTimeout(() => fn.apply(this, args), delay); };
            }
            if (searchInput) searchInput.addEventListener('input', debounce(() => loadPendingCompanies(), 300));

            await loadPendingCompanies();
        });

        async function loadPendingCompanies() {
            const tbody = document.getElementById('companies-tbody');
            if (!tbody) return;

            tbody.innerHTML = `<tr><td colspan="5" class="admin-style-d7eb25">Loading...</td></tr>`;

            const searchTerm = (document.getElementById('company-search-input')?.value || '').trim();
            const { ok, data } = await apiGetPendingCompanies(searchTerm);

            if (!ok) {
                tbody.innerHTML = `<tr><td colspan="5" class="admin-style-ff776f">Failed to load.</td></tr>`;
                return;
            }

            const companies = data.companies || (Array.isArray(data) ? data : []);

            if (companies.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="admin-style-d7eb25">No pending requests.</td></tr>`;
                return;
            }

            tbody.innerHTML = companies.map(c => `
                <tr class="admin-style-093d93">
                    <td class="admin-style-32e12a">${escHtml(c.company_name)}</td>
                    <td class="admin-style-ea4b92">${escHtml(c.industry || 'Software')}</td>
                    <td class="admin-style-ea4b92">${(c.created_at || '').split('T')[0] || '—'}</td>
                    <td class="admin-style-79d501">
                        <span class="admin-style-5217df">
                            <span class="admin-style-9c18fb"></span>
                            Pending
                        </span>
                    </td>
                    <td class="admin-style-79d501">
                        <div class="admin-style-13262f">
                            <button data-action="approve" data-company-id="${c.id}" class="admin-style-b207cb">Approve</button>
                            <button data-action="reject" data-company-id="${c.id}" class="admin-style-4ca86d">Reject</button>
                        </div>
                    </td>
                </tr>
            `).join('');
        }

        document.getElementById('companies-tbody')?.addEventListener('click', (event) => {
            const button = event.target.closest('button[data-action]');
            if (!button) return;
            const companyId = Number(button.dataset.companyId);
            if (button.dataset.action === 'approve') handleApprove(companyId);
            if (button.dataset.action === 'reject') handleReject(companyId);
        });

        async function handleApprove(companyId) {
            const { ok, data } = await apiApproveCompany(companyId);
            if (ok) { showToast('Company approved!', 'success'); await loadPendingCompanies(); }
            else showToast(data.error || 'Failed to approve company.', 'error');
        }

        async function handleReject(companyId) {
            if (!confirm('Reject this company?')) return;
            const { ok, data } = await apiRejectCompany(companyId);
            if (ok) { showToast('Company rejected.', 'success'); await loadPendingCompanies(); }
            else showToast(data.error || 'Failed to reject company.', 'error');
        }

        function escHtml(str) {
            const d = document.createElement('div');
            d.textContent = str || '';
            return d.innerHTML;
        }
