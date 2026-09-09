document.addEventListener('DOMContentLoaded', async () => {
            const user = getLoggedInUser();
            if (!user || user.role !== 'admin') {
                window.location.href = resolveSitePath('auth/login.html');
                return;
            }
            renderNavbar('dashboard');
            renderFooter();

        });
