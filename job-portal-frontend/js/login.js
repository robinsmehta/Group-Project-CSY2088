// TODO — TASK-005 (Ugeesha / C1): Wire up Login on the new page
        // NOTE: The login logic below (calling apiLogin, saving the user
        // with setLoggedInUser, redirecting by role) already works today.
        // The element IDs it looks for (login-form, login-email,
        // login-password, login-role, login-message) are unchanged from
        // the old page, so this should keep working as-is. Double check:
        // correct role is used, correct redirect happens, and a clear
        // error message shows for a wrong password.
        document.addEventListener('DOMContentLoaded', () => {
            renderNavbar('login');
            renderFooter();

            const form = document.getElementById('login-form');
            const submitBtn = form.querySelector('.btn-submit');
            const errorBox = document.getElementById('login-message');

            const toggleIcon = document.querySelector('.password-toggle-icon');
            const passInput = document.getElementById('login-password');
            if (toggleIcon && passInput) {
                toggleIcon.addEventListener('click', () => {
                    const type = passInput.getAttribute('type') === 'password' ? 'text' : 'password';
                    passInput.setAttribute('type', type);
                    if (type === 'text') toggleIcon.style.color = '#3B82F6';
                    else toggleIcon.style.color = '';
                });
            }

            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                errorBox.style.display = 'none';
                const email = document.getElementById('login-email').value.trim();
                const password = passInput.value;

                submitBtn.disabled = true;
                submitBtn.querySelector('span').textContent = 'Signing in…';

                const { ok, data } = await apiLogin(email, password, null);

                if (ok) {
                    const user = data.user || {};
                    const role = user.role;
                    const userObj = {
                        id: user.id || null,
                        email: user.email || email,
                        role: role,
                        name: user.name || user.company_name || email.split('@')[0],
                        company_name: user.company_name || null,
                        status: user.status || null
                    };
                    setLoggedInUser(userObj);
                    showToast('Logged in successfully!', 'success');
                    setTimeout(() => {
                        if (role === 'company') window.location.href = resolveSitePath('company/dashboard.html');
                        else if (role === 'admin') window.location.href = resolveSitePath('admin/dashboard.html');
                        else window.location.href = resolveSitePath('user/dashboard.html');
                    }, 600);
                } else {
                    const msg = data.error || data.message || 'Invalid email or password.';
                    errorBox.textContent = msg;
                    errorBox.style.display = 'block';
                    submitBtn.disabled = false;
                    submitBtn.querySelector('span').textContent = 'Login to your account';
                }
            });
        });
