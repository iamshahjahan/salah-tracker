#!/usr/bin/env python3
"""Celery worker startup script.

This script starts the Celery worker for processing background tasks.
Run this script to start the worker that will process prayer reminders
and other background jobs.
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Set up logging
from config.logging_config import get_logger, setup_logging

setup_logging(log_level=os.getenv('LOG_LEVEL', 'INFO'))
logger = get_logger(__name__)

# Import the Celery app
from config.celery_config import celery_app

if __name__ == '__main__':
    logger.info("Starting Celery worker with queues: prayer_reminders,consistency_checks,default")
    # Start the Celery worker
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=4',
        '--queues=prayer_reminders,consistency_checks,default',
        '--hostname=worker@%h',
        '--without-gossip',
        '--without-mingle',
        '--without-heartbeat'
    ])
