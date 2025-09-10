# Salah Reminders - Prayer Tracking Application

A modern, Flask-based prayer tracking application designed to help Muslims maintain consistency in their daily prayers with advanced features like Qada tracking, calendar views, and automatic status updates.

## 🏗️ Architecture Overview

This application follows senior software engineering principles with a clean, modular architecture:

### Backend Architecture
```
app/
├── config/          # Configuration management
│   ├── __init__.py
│   └── settings.py
├── models/          # SQLAlchemy data models
│   ├── user.py
│   ├── prayer.py
│   └── family.py
├── routes/          # API route blueprints
│   ├── __init__.py
│   ├── auth.py
│   ├── prayer.py
│   ├── dashboard.py
│   └── social.py
├── services/        # Business logic layer
│   ├── __init__.py
│   ├── base_service.py
│   ├── auth_service.py
│   ├── prayer_service.py
│   ├── user_service.py
│   └── notification_service.py
├── utils/           # Utility functions
│   ├── __init__.py
│   ├── validators.py
│   ├── formatters.py
│   ├── date_utils.py
│   ├── api_helpers.py
│   └── exceptions.py
└── tests/           # Comprehensive test suite
    ├── __init__.py
    ├── conftest.py
    ├── test_auth_service.py
    ├── test_prayer_service.py
    └── test_validators.py
```

### Frontend Architecture
```
static/
├── js/
│   ├── components/  # Reusable UI components
│   ├── services/    # API communication
│   ├── utils/       # Utility functions
│   ├── state/       # State management
│   └── tests/       # Frontend tests
├── css/
│   ├── components/  # Component-specific styles
│   ├── layouts/     # Layout styles
│   └── themes/      # Theme variables
└── assets/          # Images, fonts, etc.
```

## 🚀 Key Features

### Core Functionality
- **JWT-based Authentication**: Secure user authentication with token management
- **Prayer Time Tracking**: Location-based prayer times with automatic updates
- **Qada Management**: Mark missed prayers as Qada with proper validation
- **Calendar View**: Month-wise calendar with prayer status indicators
- **Dashboard Statistics**: Comprehensive prayer completion analytics
- **Automatic Status Updates**: Real-time prayer status management

### Advanced Features
- **Time-sensitive Completion**: Prayers can only be marked within valid time windows
- **Location Detection**: Automatic location detection during signup
- **Responsive Design**: Mobile-first approach with modern UI/UX
- **Real-time Updates**: Automatic UI updates every 5 minutes
- **Comprehensive Testing**: 80%+ test coverage for both backend and frontend

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: MySQL with proper migrations
- **Authentication**: JWT-based with Flask-JWT-Extended
- **API Design**: RESTful APIs with comprehensive error handling
- **Testing**: pytest with coverage reporting
- **Documentation**: Comprehensive docstrings and type hints

### Frontend
- **Architecture**: Modular JavaScript with separation of concerns
- **State Management**: Centralized state management
- **API Communication**: Consistent error handling and loading states
- **Testing**: Jest with comprehensive test coverage
- **Responsive Design**: Mobile-first CSS with modern layouts

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+
- MySQL 8.0+
- pip (Python package manager)
- npm (Node.js package manager)

## 🔧 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd salah-reminders
```

### 2. Backend Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your configuration

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 3. Frontend Setup
```bash
# Install frontend dependencies
npm install

# Install testing dependencies
npm install --save-dev jest eslint
```

### 4. Environment Configuration
Create a `.env` file with the following variables:
```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=mysql://username:password@localhost/salah_reminders
PRAYER_TIMES_API_KEY=your-api-key
GEOCODING_API_KEY=your-geocoding-api-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
FLASK_ENV=development
```

## 🏃‍♂️ Running the Application

### Development Mode
```bash
# Start the Flask application
python3 app.py

# The application will be available at http://localhost:5001
```

### Production Mode
```bash
# Use Gunicorn for production
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

## 🧪 Testing

### Run All Tests
```bash
# Run comprehensive test suite
python3 run_tests.py

# Run specific test categories
python3 run_tests.py --backend-only
python3 run_tests.py --frontend-only
python3 run_tests.py --integration-only
```

### Git Hooks for Quality Assurance
The repository includes automated Git hooks that run tests before commits and pushes:

```bash
# Install Git hooks (run once after cloning)
./install-hooks.sh

# Test hooks manually
.git/hooks/pre-commit
.git/hooks/pre-push
```

**Pre-commit Hook** checks for:
- Large files (>10MB)
- Sensitive information (passwords, API keys)
- TODO/FIXME comments
- Merge conflict markers
- Trailing whitespace
- Python syntax errors

**Pre-push Hook** runs:
- Python syntax check
- Import validation
- Application startup test
- Database models test
- Unit tests (pytest)
- Frontend tests (Jest)
- Code quality check (flake8)
- Security check (bandit)

To bypass hooks (not recommended):
```bash
git commit --no-verify
git push --no-verify
```

### Backend Tests
```bash
# Run backend tests with coverage
python3 -m pytest app/tests/ --cov=app --cov-report=html

# Run specific test file
python3 -m pytest app/tests/test_auth_service.py -v
```

### Frontend Tests
```bash
# Run frontend tests
npx jest static/js/tests/ --coverage

# Run specific test file
npx jest static/js/tests/test-utils.js
```

## 📊 Code Quality

### Linting
```bash
# Backend linting
python3 -m flake8 app/ --max-line-length=100

# Frontend linting
npx eslint static/js/ --ext .js
```

### Type Checking
```bash
# Python type checking
python3 -m mypy app/

# JavaScript type checking (if using TypeScript)
npx tsc --noEmit
```

## 🔒 Security Features

- **Input Validation**: Comprehensive validation for all user inputs
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **XSS Protection**: Input sanitization and output encoding
- **CSRF Protection**: Flask-WTF CSRF tokens
- **Rate Limiting**: API rate limiting for security
- **Secure Headers**: Security headers for production deployment

## 📈 Performance Optimizations

- **Database Indexing**: Optimized database queries with proper indexes
- **Caching**: Redis caching for frequently accessed data
- **Lazy Loading**: Efficient data loading strategies
- **API Optimization**: Minimized API calls and response sizes
- **Frontend Optimization**: Code splitting and lazy loading

## 🚀 Deployment

### Docker Deployment
```bash
# Build Docker image
docker build -t salah-reminders .

# Run container
docker run -p 5001:5001 --env-file .env salah-reminders
```

### Traditional Deployment
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `POST /api/auth/logout` - User logout

### Prayer Endpoints
- `GET /api/prayers/times` - Get today's prayer times
- `GET /api/prayers/times/<date>` - Get prayer times for specific date
- `POST /api/prayers/complete` - Mark prayer as completed
- `POST /api/prayers/mark-qada` - Mark prayer as Qada
- `POST /api/prayers/auto-update` - Auto-update prayer statuses

### User Endpoints
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile
- `PUT /api/user/location` - Update user location
- `GET /api/user/stats` - Get user statistics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow the established code patterns and architecture
- Write comprehensive tests for new features
- Maintain 80%+ test coverage
- Update documentation for API changes
- Follow the coding standards defined in `.cursor/rules`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Aladhan API** for prayer times data
- **BigDataCloud API** for geocoding services
- **Flask Community** for the excellent web framework
- **Muslim Community** for feedback and feature requests

## 📞 Support

For support, email support@salahreminders.com or create an issue in the repository.

## 🔄 Changelog

### Version 2.0.0 (Current)
- Complete architectural refactoring
- Service layer implementation
- Comprehensive test coverage
- Enhanced security features
- Performance optimizations
- Modern frontend architecture

### Version 1.0.0
- Initial release with basic prayer tracking
- JWT authentication
- Calendar view
- Qada functionality

---

**Made with ❤️ for the Muslim community**