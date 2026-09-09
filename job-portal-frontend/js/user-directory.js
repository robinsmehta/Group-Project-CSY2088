document.addEventListener('DOMContentLoaded', async () => {
            const user = getLoggedInUser();
            if (!user || user.role !== 'admin') {
                window.location.href = resolveSitePath('auth/login.html');
                return;
            }
            renderNavbar('users');
            renderFooter();
            await loadUsers(1);
        });

        document.getElementById('users-tbody')?.addEventListener('click', (event) => {
            const button = event.target.closest('button[data-action]');
            if (!button) return;
            const type = button.dataset.userType;
            const id = Number(button.dataset.userId);
            if (button.dataset.action === 'revoke') handleRevoke(type, id);
            if (button.dataset.action === 'restore') handleRestore(type, id);
        });

        document.getElementById('users-pagination')?.addEventListener('click', (event) => {
            const button = event.target.closest('button[data-page]');
            if (button) loadUsers(Number(button.dataset.page));
        });

        async function loadUsers(page = 1) {
            const tbody = document.getElementById('users-tbody');
            const countEl = document.getElementById('users-count');
            const paginationEl = document.getElementById('users-pagination');
            if (!tbody) return;

            tbody.innerHTML = `<tr><td colspan="5" class="admin-style-d7eb25">Loading...</td></tr>`;

            const { ok, data } = await apiGetUsers(page, '', 5);

            if (!ok) {
                tbody.innerHTML = `<tr><td colspan="5" class="admin-style-ff776f">Failed to load.</td></tr>`;
                return;
            }

            const users = data.users || [];
            const total = data.total || 0;
            const currentPage = data.page || page;
            const perPage = data.per_page || 5;

            if (users.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="admin-style-d7eb25">No users found.</td></tr>`;
            } else {
                tbody.innerHTML = users.map(u => `
                    <tr class="admin-style-093d93">
                        <td class="admin-style-79d501">
                            <div class="admin-style-8a525a">${escHtml(u.name)}</div>
                            <div class="admin-style-d90714">${escHtml(u.email)}</div>
                        </td>
                        <td class="admin-style-79d501">
                            <span class="admin-style-803529">
                                ${u.role === 'user' ? 'Job Seeker' : escHtml(u.role)}
                            </span>
                        </td>
                        <td class="admin-style-79d501">
                            ${u.is_active
                                ? `<span class="admin-style-8d9c93">Active</span>`
                                : `<span class="admin-style-008bae">Suspended</span>`}
                        </td>
                        <td class="admin-style-ea4b92">
                            ${(u.created_at || '').split('T')[0] || '—'}
                        </td>
                        <td class="admin-style-79d501">
                            ${u.is_active
                                ? `<button data-action="revoke" data-user-type="${u.type}" data-user-id="${u.id}" class="admin-style-f4a483">Revoke Access</button>`
                                : `<button data-action="restore" data-user-type="${u.type}" data-user-id="${u.id}" class="admin-style-f4a483">Restore Access</button>`}
                        </td>
                    </tr>
                `).join('');
            }

            const start = total === 0 ? 0 : (currentPage - 1) * perPage + 1;
            const end = Math.min(total, (currentPage - 1) * perPage + users.length);
            if (countEl) countEl.textContent = `Showing ${start}–${end} of ${total} users`;

            if (paginationEl) {
                const maxPages = Math.max(1, Math.ceil(total / perPage));
                const pages = [];
                for (let i = 1; i <= Math.min(3, maxPages); i++) pages.push(i);
                if (maxPages > 3) pages.push('...', maxPages);

                paginationEl.innerHTML = pages.map(p => {
                    if (p === '...') return `<span class="admin-style-34c75f">...</span>`;
                    const isActive = p === currentPage;
                    return `<button data-page="${p}" class="admin-pagination-btn" style="border:1px solid ${isActive?'#111827':'#E5E7EB'};background:${isActive?'#111827':'#fff'};color:${isActive?'#fff':'#374151'};">${p}</button>`;
                }).join('');
            }
        }

        function escHtml(str) {
            const d = document.createElement('div');
            d.textContent = str || '';
            return d.innerHTML;
        }

        async function handleRevoke(type, id) {
            if (!confirm('Revoke this user\'s access?')) return;
            const res = type === 'user' ? await apiRevokeUser(id) : await apiRevokeCompany(id);
            if (res.ok) { showToast('Access revoked.', 'success'); await loadUsers(1); }
            else showToast(res.data?.error || 'Failed to revoke access.', 'error');
        }

        async function handleRestore(type, id) {
            const res = type === 'user' ? await apiRestoreUser(id) : await apiRestoreCompany(id);
            if (res.ok) { showToast('Access restored.', 'success'); await loadUsers(1); }
            else showToast(res.data?.error || 'Failed to restore access.', 'error');
        }
