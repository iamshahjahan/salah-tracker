"""
Pytest configuration and fixtures for the Salah Tracker application.

This module provides common test fixtures and configuration for all test modules.
"""

import pytest
import os
import tempfile
from datetime import datetime, date, time
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from main import app
from database import db
from app.models.user import User
from app.models.prayer import Prayer, PrayerCompletion
from app.config.settings import TestingConfig


@pytest.fixture(scope='session')
def app():
    """
    Create and configure a test Flask application.

    Returns:
        Flask: Configured test application.
    """
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()

    # Configure test database
    os.environ['TEST_DATABASE_URL'] = f'sqlite:///{db_path}'

    # Create test app
    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

    # Clean up
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """
    Create a test client for the Flask application.

    Args:
        app: Flask application instance.

    Returns:
        FlaskClient: Test client.
    """
    return app.test_client()


@pytest.fixture
def db_session(app):
    """
    Create a database session for testing.

    Args:
        app: Flask application instance.

    Returns:
        Session: Database session.
    """
    with app.app_context():
        yield db.session
        db.session.rollback()


@pytest.fixture
def sample_user_data():
    """
    Sample user data for testing.

    Returns:
        dict: Sample user registration data.
    """
    return {
        'username': 'testuser@example.com',
        'email': 'testuser@example.com',
        'password': 'TestPassword123!',
        'first_name': 'Test',
        'last_name': 'User',
        'phone_number': '1234567890',
        'location_lat': 12.9716,
        'location_lng': 77.5946,
        'timezone': 'Asia/Kolkata'
    }


@pytest.fixture
def sample_user(db_session, sample_user_data):
    """
    Create a sample user for testing.

    Args:
        db_session: Database session.
        sample_user_data: Sample user data.

    Returns:
        User: Created user instance.
    """
    user = User(
        username=sample_user_data['username'],
        email=sample_user_data['email'],
        password_hash='hashed_password',
        first_name=sample_user_data['first_name'],
        last_name=sample_user_data['last_name'],
        phone_number=sample_user_data['phone_number'],
        location_lat=sample_user_data['location_lat'],
        location_lng=sample_user_data['location_lng'],
        timezone=sample_user_data['timezone']
    )

    db_session.add(user)
    db_session.commit()

    return user


@pytest.fixture
def sample_prayer_data():
    """
    Sample prayer data for testing.

    Returns:
        dict: Sample prayer data.
    """
    return {
        'name': 'Fajr',
        'prayer_time': time(5, 30),  # 5:30 AM
        'prayer_date': date.today()
    }


@pytest.fixture
def sample_prayer(db_session, sample_user, sample_prayer_data):
    """
    Create a sample prayer for testing.

    Args:
        db_session: Database session.
        sample_user: Sample user instance.
        sample_prayer_data: Sample prayer data.

    Returns:
        Prayer: Created prayer instance.
    """
    prayer = Prayer(
        user_id=sample_user.id,
        name=sample_prayer_data['name'],
        prayer_time=sample_prayer_data['prayer_time'],
        prayer_date=sample_prayer_data['prayer_date']
    )

    db_session.add(prayer)
    db_session.commit()

    return prayer


@pytest.fixture
def sample_prayer_completion(db_session, sample_prayer, sample_user):
    """
    Create a sample prayer completion for testing.

    Args:
        db_session: Database session.
        sample_prayer: Sample prayer instance.
        sample_user: Sample user instance.

    Returns:
        PrayerCompletion: Created prayer completion instance.
    """
    completion = PrayerCompletion(
        prayer_id=sample_prayer.id,
        user_id=sample_user.id,
        completed_at=datetime.utcnow(),
        is_late=False,
        is_qada=False
    )

    db_session.add(completion)
    db_session.commit()

    return completion


@pytest.fixture
def auth_headers(client, sample_user):
    """
    Create authentication headers for testing.

    Args:
        client: Test client.
        sample_user: Sample user instance.

    Returns:
        dict: Authentication headers.
    """
    # Login to get token
    response = client.post('/api/auth/login', json={
        'email': sample_user.email,
        'password': 'TestPassword123!'
    })

    if response.status_code == 200:
        data = response.get_json()
        token = data.get('access_token')
        return {'Authorization': f'Bearer {token}'}

    return {}


@pytest.fixture
def mock_prayer_times_api(monkeypatch):
    """
    Mock the prayer times API for testing.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    def mock_fetch_prayer_times(*args, **kwargs):
        return True, {
            'Fajr': '05:30',
            'Dhuhr': '12:15',
            'Asr': '15:45',
            'Maghrib': '18:30',
            'Isha': '20:00'
        }, None

    monkeypatch.setattr('app.services.prayer_service.PrayerService._fetch_prayer_times_from_api',
                       mock_fetch_prayer_times)


@pytest.fixture
def mock_geocoding_api(monkeypatch):
    """
    Mock the geocoding API for testing.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    def mock_fetch_city_from_coordinates(*args, **kwargs):
        return True, {
            'city': 'Bangalore',
            'country': 'India',
            'timezone': 'Asia/Kolkata'
        }, None

    monkeypatch.setattr('app.services.user_service.UserService._get_city_from_coordinates',
                       mock_fetch_city_from_coordinates)


@pytest.fixture
def mock_mail_service(monkeypatch):
    """
    Mock the mail service for testing.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    def mock_send_email(*args, **kwargs):
        return True

    monkeypatch.setattr('app.services.notification_service.NotificationService._send_prayer_reminder_email',
                       mock_send_email)
    monkeypatch.setattr('app.services.notification_service.NotificationService._send_welcome_email',
                       mock_send_email)
    monkeypatch.setattr('app.services.notification_service.NotificationService._send_daily_summary_email',
                       mock_send_email)


class TestDataFactory:
    """
    Factory class for creating test data.

    This class provides methods for creating various test data objects
    with customizable parameters.
    """

    @staticmethod
    def create_user_data(**kwargs):
        """
        Create user data with default values.

        Args:
            **kwargs: Override default values.

        Returns:
            dict: User data dictionary.
        """
        default_data = {
            'username': 'testuser@example.com',
            'email': 'testuser@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '1234567890',
            'location_lat': 12.9716,
            'location_lng': 77.5946,
            'timezone': 'Asia/Kolkata'
        }

        default_data.update(kwargs)
        return default_data

    @staticmethod
    def create_prayer_data(user_id, **kwargs):
        """
        Create prayer data with default values.

        Args:
            user_id: ID of the user.
            **kwargs: Override default values.

        Returns:
            dict: Prayer data dictionary.
        """
        default_data = {
            'user_id': user_id,
            'name': 'Fajr',
            'prayer_time': time(5, 30),
            'prayer_date': date.today()
        }

        default_data.update(kwargs)
        return default_data

    @staticmethod
    def create_prayer_completion_data(prayer_id, user_id, **kwargs):
        """
        Create prayer completion data with default values.

        Args:
            prayer_id: ID of the prayer.
            user_id: ID of the user.
            **kwargs: Override default values.

        Returns:
            dict: Prayer completion data dictionary.
        """
        default_data = {
            'prayer_id': prayer_id,
            'user_id': user_id,
            'completed_at': datetime.utcnow(),
            'is_late': False,
            'is_qada': False
        }

        default_data.update(kwargs)
        return default_data


@pytest.fixture
def test_data_factory():
    """
    Provide test data factory instance.

    Returns:
        TestDataFactory: Test data factory instance.
    """
    return TestDataFactory()
