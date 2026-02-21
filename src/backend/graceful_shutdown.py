"""
Graceful Shutdown Module
Complete in-flight requests before shutting down
"""

import signal
import sys
import logging
import threading
from typing import Callable, List
from datetime import datetime, timedelta


class GracefulShutdownHandler:
    """Handle graceful shutdown of Flask application"""
    
    def __init__(self, timeout_seconds: int = 30):
        """
        Initialize graceful shutdown handler
        
        Args:
            timeout_seconds: Max time to wait for in-flight requests before forcing shutdown
        """
        self.timeout = timeout_seconds
        self.logger = logging.getLogger('athsys.shutdown')
        self.shutdown_event = threading.Event()
        self.shutdown_callbacks: List[Callable] = []
        self.active_requests = 0
        self.shutdown_started = False
        self.lock = threading.Lock()
    
    def register_shutdown_callback(self, callback: Callable):
        """Register callback to execute on shutdown"""
        self.shutdown_callbacks.append(callback)
    
    def register_signal_handlers(self):
        """Register signal handlers for graceful shutdown"""
        
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        
        self.logger.info("Graceful shutdown handlers registered")
    
    def _handle_signal(self, signum, frame):
        """Handle shutdown signals"""
        
        signal_name = signal.Signals(signum).name
        self.logger.warning(f"Received signal {signal_name}, initiating graceful shutdown...")
        
        self.initiate_shutdown()
        
        # Exit after shutdown timeout
        threading.Timer(self.timeout + 5, self._force_exit).start()
    
    def _force_exit(self):
        """Force exit if shutdown takes too long"""
        self.logger.critical("Graceful shutdown timeout exceeded, forcing exit")
        sys.exit(1)
    
    def initiate_shutdown(self):
        """Initiate graceful shutdown"""
        
        with self.lock:
            if self.shutdown_started:
                return
            
            self.shutdown_started = True
        
        self.logger.info("Graceful shutdown initiated")
        
        # Execute shutdown callbacks
        for callback in self.shutdown_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Error executing shutdown callback: {e}")
        
        # Set shutdown event
        self.shutdown_event.set()
        
        # Wait for requests to complete
        self._wait_for_requests()
        
        self.logger.info("Graceful shutdown complete")
    
    def _wait_for_requests(self):
        """Wait for in-flight requests to complete"""
        
        start_time = datetime.utcnow()
        
        while self.active_requests > 0:
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            
            if elapsed > self.timeout:
                self.logger.warning(
                    f"Shutdown timeout: {self.active_requests} requests still in flight"
                )
                break
            
            self.logger.info(f"Waiting for {self.active_requests} request(s) to complete...")
            threading.Event().wait(1)  # Wait 1 second
    
    def track_request_start(self):
        """Track request start"""
        with self.lock:
            if not self.shutdown_started:
                self.active_requests += 1
                return True
            return False
    
    def track_request_end(self):
        """Track request completion"""
        with self.lock:
            if self.active_requests > 0:
                self.active_requests -= 1


# Global shutdown handler
_shutdown_handler = None


def get_shutdown_handler(timeout_seconds: int = 30) -> GracefulShutdownHandler:
    """Get or create shutdown handler"""
    global _shutdown_handler
    
    if _shutdown_handler is None:
        _shutdown_handler = GracefulShutdownHandler(timeout_seconds)
        _shutdown_handler.register_signal_handlers()
    
    return _shutdown_handler


# Flask middleware for request tracking
def create_graceful_shutdown_middleware(app):
    """Create middleware for graceful shutdown request tracking"""
    
    from flask import g
    from functools import wraps
    
    shutdown_handler = get_shutdown_handler()
    
    @app.before_request
    def track_request_start():
        """Track request start"""
        if not shutdown_handler.track_request_start():
            # Service is shutting down
            from flask import jsonify
            return jsonify({'error': 'Service is shutting down'}), 503
        
        g.shutdown_handler = shutdown_handler
    
    @app.after_request
    def track_request_end(response):
        """Track request completion"""
        if hasattr(g, 'shutdown_handler'):
            g.shutdown_handler.track_request_end()
        
        return response
    
    return shutdown_handler
