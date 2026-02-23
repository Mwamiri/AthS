(function () {
    if (window.__athsysProgressInit) return;
    window.__athsysProgressInit = true;

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
