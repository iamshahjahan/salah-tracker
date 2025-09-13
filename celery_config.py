"""
Celery configuration for background task processing.

This module configures Celery for handling background tasks like
prayer reminders, email notifications, and other scheduled jobs.
"""

import os
from celery import Celery
from celery.schedules import crontab
from app.config.settings import get_config

# Set up logging for Celery
from logging_config import setup_logging, get_logger
setup_logging(log_level=os.getenv('LOG_LEVEL', 'INFO'))
logger = get_logger(__name__)

# Get configuration
config = get_config()

# Create Celery instance
celery_app = Celery(
    'salah_tracker',
    broker=config.CELERY_CONFIG.broker_url,
    backend=config.CELERY_CONFIG.result_backend,
    include=['app.tasks.prayer_reminders', 'app.tasks.consistency_checks']
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'app.tasks.prayer_reminders.*': {'queue': 'prayer_reminders'},
        'app.tasks.consistency_checks.*': {'queue': 'consistency_checks'},
    },
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'send-prayer-reminders': {
            'task': 'app.tasks.prayer_reminders.send_prayer_reminders',
            'schedule': crontab(minute='*/5'),  # Every 5 minutes
        },
        'send-prayer-window-reminders': {
            'task': 'app.tasks.prayer_reminders.send_prayer_window_reminders',
            'schedule': crontab(minute='*/5'),  # Every 5 minutes
        },
        'check-consistency': {
            'task': 'app.tasks.consistency_checks.check_user_consistency',
            'schedule': crontab(hour=22, minute=0),  # Daily at 10 PM
        },
        'cleanup-old-notifications': {
            'task': 'app.tasks.prayer_reminders.cleanup_old_notifications',
            'schedule': crontab(hour=0, minute=0),  # Daily at midnight
        },
    },
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=True,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    
    # Task time limits
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['app.tasks'])

if __name__ == '__main__':
    celery_app.start()
