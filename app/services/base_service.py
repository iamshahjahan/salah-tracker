"""
Base service class for common functionality.

This module provides a base service class that other services can inherit from,
providing common functionality like database session management and error handling.
"""

from typing import Any, Dict, Optional, Type, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
import logging

from database import db
from app.config.settings import Config

T = TypeVar('T')

logger = logging.getLogger(__name__)


class BaseService:
    """
    Base service class providing common functionality for all services.

    This class provides database session management, error handling, and
    common CRUD operations that can be inherited by specific service classes.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the base service.

        Args:
            config: Configuration instance. If None, will use current app config.
        """
        if config is None:
            # Try to get config from Flask app first
            try:
                self.config = current_app.config
            except RuntimeError:
                # If no app context, use default config
                from app.config.settings import get_config
                self.config = get_config()
        else:
            self.config = config
        self.logger = logger

    @property
    def db_session(self) -> Session:
        """
        Get the current database session.

        Returns:
            Session: The current SQLAlchemy database session.
        """
        return db.session

    def commit_session(self) -> None:
        """
        Commit the current database session.

        Raises:
            SQLAlchemyError: If the commit fails.
        """
        try:
            self.db_session.commit()
            self.logger.debug("Database session committed successfully")
        except SQLAlchemyError as e:
            self.db_session.rollback()
            self.logger.error(f"Database commit failed: {str(e)}")
            raise

    def rollback_session(self) -> None:
        """
        Rollback the current database session.
        """
        self.db_session.rollback()
        self.logger.debug("Database session rolled back")

    def create_record(self, model_class: Type[T], **kwargs) -> T:
        """
        Create a new database record.

        Args:
            model_class: The SQLAlchemy model class.
            **kwargs: Field values for the new record.

        Returns:
            T: The created model instance.

        Raises:
            SQLAlchemyError: If the creation fails.
        """
        try:
            record = model_class(**kwargs)
            self.db_session.add(record)
            self.commit_session()
            self.logger.info(f"Created {model_class.__name__} record with ID: {record.id}")
            return record
        except SQLAlchemyError as e:
            self.rollback_session()
            self.logger.error(f"Failed to create {model_class.__name__} record: {str(e)}")
            raise

    def get_record_by_id(self, model_class: Type[T], record_id: int) -> Optional[T]:
        """
        Get a database record by its ID.

        Args:
            model_class: The SQLAlchemy model class.
            record_id: The ID of the record to retrieve.

        Returns:
            Optional[T]: The model instance if found, None otherwise.
        """
        try:
            return model_class.query.get(record_id)
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to get {model_class.__name__} by ID {record_id}: {str(e)}")
            return None

    def update_record(self, record: T, **kwargs) -> T:
        """
        Update a database record.

        Args:
            record: The model instance to update.
            **kwargs: Field values to update.

        Returns:
            T: The updated model instance.

        Raises:
            SQLAlchemyError: If the update fails.
        """
        try:
            for key, value in kwargs.items():
                if hasattr(record, key):
                    setattr(record, key, value)

            self.commit_session()
            self.logger.info(f"Updated {record.__class__.__name__} record with ID: {record.id}")
            return record
        except SQLAlchemyError as e:
            self.rollback_session()
            self.logger.error(f"Failed to update {record.__class__.__name__} record: {str(e)}")
            raise

    def delete_record(self, record: T) -> bool:
        """
        Delete a database record.

        Args:
            record: The model instance to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            self.db_session.delete(record)
            self.commit_session()
            self.logger.info(f"Deleted {record.__class__.__name__} record with ID: {record.id}")
            return True
        except SQLAlchemyError as e:
            self.rollback_session()
            self.logger.error(f"Failed to delete {record.__class__.__name__} record: {str(e)}")
            return False

    def handle_service_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """
        Handle service errors and return a standardized error response.

        Args:
            error: The exception that occurred.
            operation: Description of the operation that failed.

        Returns:
            Dict[str, Any]: Standardized error response.
        """
        self.logger.error(f"Service error in {operation}: {str(error)}")

        return {
            'success': False,
            'error': str(error),
            'operation': operation,
            'timestamp': self._get_current_timestamp()
        }

    def _get_current_timestamp(self) -> str:
        """
        Get the current timestamp in ISO format.

        Returns:
            str: Current timestamp in ISO format.
        """
        from datetime import datetime
        return datetime.utcnow().isoformat()
