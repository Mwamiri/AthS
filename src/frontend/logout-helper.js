(function initLogoutHelper(global) {
    async function logoutWithRevocation(options = {}) {
        const {
            redirectTo = 'login.html',
            clearMode = 'selected',
            showMessage,
            delayMs = 0,
            confirmMessage,
            includeLegacyToken = true
        } = options;

        if (confirmMessage && !confirm(confirmMessage)) {
            return false;
        }

        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');

        try {
            await fetch('/api/auth/logout', {
                method: 'POST',
                headers: token ? { Authorization: `Bearer ${token}` } : {}
            });
        } catch (error) {
            console.warn('Logout API call failed:', error);
        }

        if (clearMode === 'all') {
            localStorage.clear();
            sessionStorage.clear();
        } else {
            localStorage.removeItem('authToken');
            sessionStorage.removeItem('authToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('user');
            sessionStorage.removeItem('user');
            if (includeLegacyToken) {
                localStorage.removeItem('token');
            }
        }

        if (typeof showMessage === 'function') {
            try {
                showMessage();
            } catch (error) {
                console.warn('Logout message hook failed:', error);
            }
        }

        const navigate = () => {
            if (redirectTo) {
                window.location.href = redirectTo;
            }
        };

        if (delayMs > 0) {
            setTimeout(navigate, delayMs);
        } else {
            navigate();
        }

        return true;
    }

    global.logoutWithRevocation = logoutWithRevocation;
})(window);
