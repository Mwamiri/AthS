(function () {
    if (window.__athsysProgressInit) return;
    window.__athsysProgressInit = true;

    function injectGlobalNavigation() {
        if (!document.body) return;
        if (document.getElementById('athsys-global-nav')) return;

        var currentPath = (window.location.pathname || '/').toLowerCase();

        var navItems = [
            { href: '/', label: '🏠 Front Page', match: ['/', '/index.html'] },
            { href: '/landing.html', label: '✨ Landing', match: ['/landing.html'] },
            { href: '/records-rankings.html', label: '🏆 Records', match: ['/records-rankings.html'] },
            { href: '/public-results.html', label: '📈 Results', match: ['/public-results.html', '/results.html', '/races-results.html'] },
            { href: '/races.html', label: '🏁 Races', match: ['/races.html', '/race-details.html', '/public-races.html'] },
            { href: '/athletes.html', label: '🏃 Athletes', match: ['/athletes.html', '/athlete.html'] },
            { href: '/admin', label: '🛡️ Admin', match: ['/admin', '/admin-pro', '/admin-pro-complete', '/admin-pro-complete.html', '/admin-old', '/admin-old.html', '/admin.html'] },
            { href: '/status.html', label: '🏥 Status', match: ['/status.html'] }
        ];

        var nav = document.createElement('nav');
        nav.id = 'athsys-global-nav';
        nav.className = 'athsys-global-nav';

        var inner = document.createElement('div');
        inner.className = 'athsys-global-nav__inner';

        var brand = document.createElement('a');
        brand.href = '/';
        brand.className = 'athsys-global-brand';
        brand.textContent = '🏃 AthSys';
        inner.appendChild(brand);

        navItems.forEach(function (item) {
            var link = document.createElement('a');
            link.href = item.href;
            link.className = 'athsys-global-link';
            link.textContent = item.label;

            var isActive = (item.match || []).some(function (path) {
                return currentPath === path;
            });

            if (isActive) {
                link.classList.add('is-active');
            }

            inner.appendChild(link);
        });

        nav.appendChild(inner);
        document.body.insertBefore(nav, document.body.firstChild);
    }

    injectGlobalNavigation();

    var progressRoot = document.createElement('div');
    progressRoot.id = 'athsys-progress';

    var progressBar = document.createElement('div');
    progressBar.className = 'athsys-progress-bar';
    progressRoot.appendChild(progressBar);
    document.documentElement.appendChild(progressRoot);

    var current = 0;
    var timer = null;
    var activeRequests = 0;
    var startDelayTimer = null;

    function setProgress(value) {
        current = Math.max(0, Math.min(100, value));
        progressBar.style.width = current + '%';
    }

    function resetStateClasses() {
        progressRoot.classList.remove('success');
        progressRoot.classList.remove('error');
    }

    function startProgress() {
        if (timer) window.clearInterval(timer);
        resetStateClasses();
        progressRoot.classList.add('active');
        document.body.classList.add('athsys-loading');

        if (current < 10) setProgress(10);
        timer = window.setInterval(function () {
            if (current < 85) {
                setProgress(current + Math.max(1, (85 - current) * 0.08));
            }
        }, 180);
    }

    function finishProgress(state) {
        if (timer) {
            window.clearInterval(timer);
            timer = null;
        }

        if (state === 'success') {
            progressRoot.classList.add('success');
        } else if (state === 'error') {
            progressRoot.classList.add('error');
        }

        setProgress(100);

        window.setTimeout(function () {
            progressRoot.classList.remove('active');
            document.body.classList.remove('athsys-loading');
            resetStateClasses();
            setProgress(0);
        }, 220);
    }

    function scheduleProgressStart() {
        if (startDelayTimer || progressRoot.classList.contains('active')) return;
        startDelayTimer = window.setTimeout(function () {
            startDelayTimer = null;
            startProgress();
        }, 120);
    }

    function clearScheduledStart() {
        if (!startDelayTimer) return;
        window.clearTimeout(startDelayTimer);
        startDelayTimer = null;
    }

    function requestStarted() {
        activeRequests += 1;
        if (activeRequests === 1) {
            scheduleProgressStart();
        }
    }

    function requestEnded(success) {
        activeRequests = Math.max(0, activeRequests - 1);
        if (activeRequests === 0) {
            clearScheduledStart();
            if (progressRoot.classList.contains('active')) {
                finishProgress(success ? 'success' : 'error');
            }
        }
    }

    window.addEventListener('load', function () {
        startProgress();
        window.setTimeout(function () {
            activeRequests = 0;
            finishProgress('success');
        }, 320);
    });

    document.addEventListener('click', function (event) {
        var link = event.target && event.target.closest ? event.target.closest('a[href]') : null;
        if (!link) return;

        var href = link.getAttribute('href') || '';
        if (!href || href.startsWith('#') || href.startsWith('javascript:')) return;

        var target = link.getAttribute('target');
        if (target && target !== '_self') return;

        var isSameOrigin = link.origin === window.location.origin;
        if (!isSameOrigin) return;

        startProgress();
    }, true);

    var nativeFetch = window.fetch;
    if (typeof nativeFetch === 'function') {
        window.fetch = function () {
            requestStarted();
            return nativeFetch.apply(window, arguments)
                .then(function (response) {
                    requestEnded(response.ok);
                    return response;
                })
                .catch(function (error) {
                    requestEnded(false);
                    throw error;
                });
        };
    }

    var NativeXHR = window.XMLHttpRequest;
    if (NativeXHR) {
        var open = NativeXHR.prototype.open;
        var send = NativeXHR.prototype.send;

        NativeXHR.prototype.open = function () {
            this.__athsysTracked = true;
            return open.apply(this, arguments);
        };

        NativeXHR.prototype.send = function () {
            if (this.__athsysTracked) {
                requestStarted();
                this.addEventListener('loadend', function () {
                    requestEnded(this.status >= 200 && this.status < 400);
                }, { once: true });
            }
            return send.apply(this, arguments);
        };
    }
})();
