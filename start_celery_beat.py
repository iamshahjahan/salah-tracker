#!/usr/bin/env python3
"""
Celery Beat scheduler startup script.

This script starts the Celery Beat scheduler for periodic tasks.
Run this script to start the scheduler that will trigger prayer reminders
and other scheduled jobs.
"""

import os
import sys
from celery import Celery

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
from logging_config import setup_logging, get_logger
setup_logging(log_level=os.getenv('LOG_LEVEL', 'INFO'))
logger = get_logger(__name__)

# Import the Celery app
from celery_config import celery_app

if __name__ == '__main__':
    logger.info("Starting Celery Beat scheduler...")
    # Start the Celery Beat scheduler
    celery_app.start([
        'beat',
        '--loglevel=info',
        '--scheduler=celery.beat:PersistentScheduler'
    ])
