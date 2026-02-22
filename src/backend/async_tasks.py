"""
Async Tasks Module
Background job processing using Celery or simple queue tasks
Handles email sending, report generation, data exports, and long-running operations
"""

import logging
import json
from typing import Any, Dict, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
import os

try:
    from celery import Celery, Task
    from celery.result import AsyncResult
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class AsyncTask:
    """Base async task definition"""
    
    def __init__(self, task_id: str, task_type: str, status: str = 'pending'):
        self.task_id = task_id
        self.task_type = task_type
        self.status = status  # pending, processing, completed, failed
        self.result = None
        self.error = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.progress = 0  # 0-100
    
    def to_dict(self) -> Dict:
        """Convert task to dictionary"""
        return {
            'task_id': self.task_id,
            'task_type': self.task_type,
            'status': self.status,
            'progress': self.progress,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class TaskQueue:
    """Simple task queue using Redis or memory"""
    
    def __init__(self, use_redis: bool = True):
        self.use_redis = use_redis and REDIS_AVAILABLE
        self.logger = logging.getLogger('athsys.async')
        
        if self.use_redis:
            self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(self.redis_url)
        else:
            self.tasks_memory = {}
    
    def queue_task(self, task_type: str, task_data: Dict, priority: int = 5) -> str:
        """
        Queue a new task
        
        Args:
            task_type: Type of task (send_email, export_data, generate_report, etc.)
            task_data: Task parameters
            priority: Task priority (1-10, higher = more important)
            
        Returns:
            Task ID
        """
        import uuid
        task_id = str(uuid.uuid4())
        
        task_obj = AsyncTask(task_id, task_type)
        task_dict = task_obj.to_dict()
        task_dict['data'] = task_data
        task_dict['priority'] = priority
        
        if self.use_redis:
            self.redis_client.set(
                f"task:{task_id}",
                json.dumps(task_dict),
                ex=86400  # 24 hour expiry
            )
            # Add to priority queue
            self.redis_client.zadd(f"task_queue:{task_type}", {task_id: -priority})
        else:
            self.tasks_memory[task_id] = task_dict
        
        self.logger.info(f"Task queued: {task_id} ({task_type})")
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get task status"""
        if self.use_redis:
            task_data = self.redis_client.get(f"task:{task_id}")
            return json.loads(task_data) if task_data else None
        else:
            return self.tasks_memory.get(task_id)
    
    def update_task_status(self, task_id: str, status: str, progress: int = None, result: Any = None, error: str = None):
        """Update task status"""
        task = self.get_task_status(task_id)
        if not task:
            return
        
        task['status'] = status
        task['updated_at'] = datetime.utcnow().isoformat()
        
        if progress is not None:
            task['progress'] = progress
        
        if result is not None:
            task['result'] = result
        
        if error:
            task['error'] = error
        
        if self.use_redis:
            self.redis_client.set(
                f"task:{task_id}",
                json.dumps(task),
                ex=86400
            )
        else:
            self.tasks_memory[task_id] = task
        
        self.logger.info(f"Task updated: {task_id} -> {status}")
    
    def get_pending_tasks(self, task_type: str) -> list:
        """Get pending tasks of a specific type"""
        if self.use_redis:
            task_ids = self.redis_client.zrange(f"task_queue:{task_type}", 0, -1)
            return [self.get_task_status(tid.decode()) for tid in task_ids if tid]
        else:
            return [t for t in self.tasks_memory.values() 
                   if t.get('task_type') == task_type and t.get('status') == 'pending']
    
    def complete_task(self, task_id: str, result: Any):
        """Mark task as completed"""
        self.update_task_status(task_id, 'completed', progress=100, result=result)
    
    def fail_task(self, task_id: str, error: str):
        """Mark task as failed"""
        self.update_task_status(task_id, 'failed', error=error)


# Initialize task queue
_task_queue = None


def get_task_queue() -> TaskQueue:
    """Get or create task queue"""
    global _task_queue
    
    if _task_queue is None:
        _task_queue = TaskQueue(use_redis=REDIS_AVAILABLE or CELERY_AVAILABLE)
    
    return _task_queue


def async_task(task_type: str, priority: int = 5):
    """
    Decorator for async task functions
    
    Example:
        @async_task('send_email', priority=8)
        def send_welcome_email(user_id, email):
            # Long-running operation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> str:
            queue = get_task_queue()
            
            # Prepare task data
            task_data = {
                'function': func.__name__,
                'args': args,
                'kwargs': kwargs
            }
            
            # Queue task
            task_id = queue.queue_task(task_type, task_data, priority)
            
            # Mark as processing and execute immediately (can be async with worker)
            queue.update_task_status(task_id, 'processing')
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                queue.complete_task(task_id, result)
                return task_id
            except Exception as e:
                queue.fail_task(task_id, str(e))
                raise
        
        return wrapper
    return decorator


# Common async task functions
def queue_send_email(to_email: str, template: str, context: Dict, user_id: int = None) -> str:
    """Queue email sending task"""
    queue = get_task_queue()
    task_data = {
        'to_email': to_email,
        'template': template,
        'context': context,
        'user_id': user_id
    }
    return queue.queue_task('send_email', task_data, priority=7)


def queue_generate_report(report_type: str, filters: Dict, user_id: int) -> str:
    """Queue report generation task"""
    queue = get_task_queue()
    task_data = {
        'report_type': report_type,
        'filters': filters,
        'user_id': user_id
    }
    return queue.queue_task('generate_report', task_data, priority=6)


def queue_data_export(resource_type: str, format: str, filters: Dict, user_id: int) -> str:
    """Queue data export task"""
    queue = get_task_queue()
    task_data = {
        'resource_type': resource_type,
        'format': format,
        'filters': filters,
        'user_id': user_id
    }
    return queue.queue_task('export_data', task_data, priority=5)


def queue_bulk_import(resource_type: str, file_path: str, user_id: int) -> str:
    """Queue bulk import task"""
    queue = get_task_queue()
    task_data = {
        'resource_type': resource_type,
        'file_path': file_path,
        'user_id': user_id
    }
    return queue.queue_task('bulk_import', task_data, priority=4)


def queue_notification(notification_type: str, recipient_id: int, message: str, data: Dict = None) -> str:
    """Queue notification task"""
    queue = get_task_queue()
    task_data = {
        'notification_type': notification_type,
        'recipient_id': recipient_id,
        'message': message,
        'data': data or {}
    }
    return queue.queue_task('send_notification', task_data, priority=7)


def get_task_status(task_id: str) -> Optional[Dict]:
    """Get async task status"""
    queue = get_task_queue()
    return queue.get_task_status(task_id)
