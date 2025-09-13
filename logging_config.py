#!/usr/bin/env python3
"""
Logging configuration for SalahTracker application.

This module sets up comprehensive logging for the Flask application,
Celery workers, and all services with proper file rotation and formatting.
"""

import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

def setup_logging(log_level='INFO', log_dir='logs'):
    """
    Set up comprehensive logging configuration with unified log file.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
    """
    
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(exist_ok=True)
    
    # Get current timestamp for log file naming
    timestamp = datetime.now().strftime('%Y%m%d')
    
    # Define unified log file path
    unified_log_file = os.path.join(log_dir, f'salah_tracker_{timestamp}.log')
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Unified file handler for all logs (with rotation)
    file_handler = logging.handlers.RotatingFileHandler(
        unified_log_file,
        maxBytes=20*1024*1024,  # 20MB (increased for unified logging)
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler (for development)
    if os.getenv('FLASK_ENV', 'development') == 'development':
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    # Set up specific loggers to use the unified file
    setup_celery_logging(file_handler)
    setup_flask_logging()
    setup_sqlalchemy_logging()
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("="*60)
    logger.info("SalahTracker Logging System Initialized")
    logger.info(f"Log Level: {log_level}")
    logger.info(f"Log Directory: {log_dir}")
    logger.info(f"Unified Log File: {unified_log_file}")
    logger.info("="*60)

def setup_celery_logging(file_handler):
    """Set up Celery-specific logging to use unified file."""
    
    # Celery logger
    celery_logger = logging.getLogger('celery')
    celery_logger.setLevel(logging.INFO)
    celery_logger.addHandler(file_handler)
    
    # Celery task logger
    celery_task_logger = logging.getLogger('celery.task')
    celery_task_logger.setLevel(logging.INFO)
    celery_task_logger.addHandler(file_handler)

def setup_flask_logging():
    """Set up Flask-specific logging."""
    
    # Flask logger
    flask_logger = logging.getLogger('werkzeug')
    flask_logger.setLevel(logging.WARNING)  # Reduce Flask request logs
    
    # Our app logger
    app_logger = logging.getLogger('salah_tracker')
    app_logger.setLevel(logging.INFO)

def setup_sqlalchemy_logging():
    """Set up SQLAlchemy logging."""
    
    # SQLAlchemy logger
    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    sqlalchemy_logger.setLevel(logging.WARNING)  # Reduce SQL query logs
    
    # SQLAlchemy pool logger
    sqlalchemy_pool_logger = logging.getLogger('sqlalchemy.pool')
    sqlalchemy_pool_logger.setLevel(logging.WARNING)

def get_logger(name):
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)

# Initialize logging when module is imported
if __name__ != '__main__':
    setup_logging()
