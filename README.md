# Salah Tracker - Prayer Tracking Application

A modern, Flask-based prayer tracking application designed to help Muslims maintain consistency in their daily prayers with advanced features like Qada tracking, calendar views, and automatic status updates.

## 📁 Project Structure

```
salah-tracker/
├── app/                    # Main application code
│   ├── config/            # Application configuration
│   ├── models/            # Database models
│   ├── routes/            # API routes and blueprints
│   ├── services/          # Business logic services
│   ├── tasks/             # Celery background tasks
│   └── utils/             # Utility functions
├── assets/                # Static assets and screenshots
├── config/                # Configuration files
│   ├── celery_config.py   # Celery configuration
│   ├── database.py        # Database configuration
│   ├── logging_config.py  # Logging configuration
│   ├── mail_config.py     # Email configuration
│   ├── env.example        # Environment variables example
│   ├── production.env.template  # Production environment template
│   └── requirements*.txt  # Python dependencies
├── docs/                  # Documentation
│   ├── README.md          # This file
│   ├── DEPLOYMENT_GUIDE.md
│   ├── CELERY_SETUP_GUIDE.md
│   └── ...                # Other documentation files
├── logs/                  # Application logs
├── migrations/            # Database migration files
├── scripts/               # Deployment and utility scripts
│   ├── deploy_*.sh        # Deployment scripts
│   ├── manage_celery.sh   # Celery management
│   ├── start_celery_*.py  # Celery startup scripts
│   └── ...                # Other utility scripts
├── static/                # Frontend static files
│   ├── css/               # Stylesheets
│   └── js/                # JavaScript files
├── templates/             # HTML templates
├── features/              # BDD Feature Files (Gherkin)
│   ├── authentication/    # User authentication features
│   ├── email_verification/ # Email verification features
│   ├── prayer_tracking/   # Prayer completion features
│   ├── dashboard/         # Dashboard features
│   ├── notifications/     # Notification features
│   ├── api/               # API endpoint features
│   └── support/           # Step definitions and environment
├── tests/                 # All test files
│   ├── automation/        # Selenium automation tests
│   ├── critical/          # Critical functionality tests
│   ├── comprehensive/     # Integration tests
│   └── *.py               # Unit tests
├── tools/                 # Development tools
│   ├── celery_manager.py  # Celery management tool
│   ├── run_*_tests.py     # Test runners
│   └── test_*.py          # Standalone test files
├── main.py                # Application entry point
└── package.json           # Frontend dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL/PostgreSQL
- Redis
- Node.js (for frontend)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd salah-tracker
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r config/requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   npm install
   ```

4. **Set up environment variables**
   ```bash
   cp config/env.example .env
   # Edit .env with your configuration
   ```

5. **Set up the database**
   ```bash
   python main.py
   # The application will create tables automatically
   ```

6. **Start the application**
   ```bash
   python main.py
   ```

### Development

- **Run tests**: `python tools/run_all_tests.py`
- **Run critical tests**: `python tools/run_critical_tests.py`
- **Start Celery worker**: `python scripts/start_celery_worker.py`
- **Start Celery beat**: `python scripts/start_celery_beat.py`

### Deployment

See `docs/DEPLOYMENT_GUIDE.md` for detailed deployment instructions.

## 🏗️ Architecture

### Backend (Flask)
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: MySQL with proper migrations
- **Authentication**: JWT-based authentication
- **API Design**: RESTful APIs with proper error handling
- **Structure**: Blueprint-based modular architecture
- **Background Tasks**: Celery with Redis broker

### Frontend (Vanilla JS)
- **Architecture**: Modular JavaScript with separation of concerns
- **State Management**: Centralized state management
- **API Communication**: Consistent error handling and loading states
- **UI Components**: Reusable component patterns
- **Responsive Design**: Mobile-first approach

## 🔧 Configuration

All configuration files are located in the `config/` directory:

- `env.example` - Environment variables template
- `celery_config.py` - Celery configuration
- `database.py` - Database configuration
- `logging_config.py` - Logging configuration
- `mail_config.py` - Email configuration

## 📚 Documentation

All documentation is located in the `docs/` directory:

- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `CELERY_SETUP_GUIDE.md` - Celery setup guide
- `EMAIL_VERIFICATION_SETUP.md` - Email verification setup
- `LOGGING_GUIDE.md` - Logging configuration guide

## 🧪 Testing

The project follows Behavior-Driven Development (BDD) architecture with comprehensive test coverage:

### Test Structure
- **BDD Tests** (`features/`): User journey and behavior testing using Gherkin syntax
- **Step Definitions** (`features/steps/`): Implementation of BDD test steps
- **Test Configuration** (`behave.ini`): BDD test configuration

### Running Tests

```bash
# Install BDD dependencies
make install-bdd

# Run all BDD tests
make test-bdd

# Run specific test suites
make test-smoke      # Smoke tests only
make test-regression # Full regression tests
make test-api        # API tests only
make test-ui         # UI tests only

# Run BDD tests
behave --tags @smoke                    # Run smoke tests only
behave --tags @api                      # Run API tests only
behave --tags @ui                       # Run UI tests only
behave                                  # Run all BDD tests
```

### BDD Features
- **Authentication**: User registration, login, OTP verification
- **Email Verification**: Email verification workflows and rate limiting
- **Prayer Tracking**: Prayer completion, Qada tracking, timezone handling
- **Dashboard**: Statistics, calendar views, responsive design
- **Notifications**: Prayer reminders, email notifications
- **API**: Endpoint testing, authentication, rate limiting

See `docs/BDD_IMPLEMENTATION_GUIDE.md` for detailed BDD documentation.

## 🚀 Deployment Scripts

Deployment and utility scripts are located in the `scripts/` directory:

- `deploy_with_caching.sh` - Main deployment script
- `manage_celery.sh` - Celery service management
- `check_remote_status.sh` - Check service status
- `restart_remote_services.sh` - Restart all services

## 📝 Contributing

1. Follow the established project structure
2. Write tests for new features
3. Update documentation as needed
4. Follow the coding standards defined in `.cursorrules`

## 📄 License

This project is licensed under the MIT License.
