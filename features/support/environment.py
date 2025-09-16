"""Environment configuration for BDD tests."""

import os
import sys

from behave import fixture, use_fixture

from app.config.settings import get_config
from config.database import db
from main import app

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


@fixture
def flask_app(context):
    """Create Flask app for testing."""
    print("Creating Flask app fixture...")
    # Configure app for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        context.app = app
        context.db = db
        print("Flask app and database setup complete")
        yield app
        print("Cleaning up database...")
        db.drop_all()


def before_all(context):
    """Set up before all tests."""
    print("Setting up test environment...")
    # Set up test environment
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'true'

    # Set up configuration
    print("Loading configuration...")
    context.app_config = get_config()
    print(f"Config loaded: DEFAULT_TIMEZONE = {context.app_config.DEFAULT_TIMEZONE}")

    # Use the Flask app fixture
    print("Using Flask app fixture...")
    use_fixture(flask_app, context)
    print("Flask app fixture setup complete")


def before_scenario(context, scenario):
    """Set up before each scenario."""
    # Clean up any existing data
    if hasattr(context, 'db'):
        # Clear all tables
        for table in reversed(context.db.metadata.sorted_tables):
            context.db.session.execute(table.delete())
        context.db.session.commit()

    # Initialize context variables
    context.current_user = None
    context.is_logged_in = False
    context.current_page = None
    context.test_data = {}


def after_scenario(context, scenario):
    """Clean up after each scenario."""
    # Clean up any test data
    if hasattr(context, 'db'):
        context.db.session.rollback()

    # Clear context variables
    context.current_user = None
    context.is_logged_in = False
    context.current_page = None
    context.test_data = {}


def after_all(context):
    """Clean up after all tests."""
    # Final cleanup
    if hasattr(context, 'db'):
        context.db.session.close()
