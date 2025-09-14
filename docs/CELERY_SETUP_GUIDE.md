# 🚀 Celery Background Tasks Setup Guide

This guide will help you set up Celery for automated prayer reminders and background task processing in your Salah Tracker application.

## 📋 Prerequisites

1. **Redis Server**: Celery uses Redis as a message broker
2. **Python Dependencies**: Celery and Redis packages
3. **Email Configuration**: SMTP settings for sending reminders

## 🛠️ Installation & Setup

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Redis (macOS)
brew install redis

# Install Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# Install Redis (Windows)
# Download from: https://github.com/microsoftarchive/redis/releases
```

### 2. Start Redis Server

```bash
# Start Redis server
redis-server

# Or start as a service (macOS)
brew services start redis

# Or start as a service (Ubuntu/Debian)
sudo systemctl start redis-server
```

### 3. Configure Environment Variables

Add these to your `.env` file:

```env
# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 🚀 Running the System

### 1. Start the Flask Application

```bash
python3 main.py
```

### 2. Start the Celery Worker

```bash
# Start the worker (in a new terminal)
python3 start_celery_worker.py

# Or use celery command directly
celery -A celery_config worker --loglevel=info --concurrency=4
```

### 3. Start the Celery Beat Scheduler

```bash
# Start the scheduler (in a new terminal)
python3 start_celery_beat.py

# Or use celery command directly
celery -A celery_config beat --loglevel=info
```

## 📅 Scheduled Tasks

The system automatically runs these tasks:

| Task | Schedule | Description |
|------|----------|-------------|
| **Prayer Reminders** | Every 5 minutes | Sends email reminders to users before prayer times |
| **Consistency Check** | Daily at 10 PM | Analyzes prayer completion and sends motivational nudges |
| **Cleanup** | Daily at midnight | Removes old notifications to keep database clean |

## 🎯 Task Details

### Prayer Reminders (`send_prayer_reminders`)

- **Frequency**: Every 5 minutes
- **Purpose**: Sends email reminders to users before their prayer times
- **Logic**:
  - Checks all users with email notifications enabled
  - Calculates reminder time based on user's preferences
  - Sends reminder if within 5-minute window
  - Prevents duplicate reminders for the same prayer

### Consistency Checks (`check_user_consistency`)

- **Frequency**: Daily at 10 PM
- **Purpose**: Analyzes prayer completion and sends motivational messages
- **Logic**:
  - Checks prayer completion over last 3 days
  - Sends nudge if completion rate < 60%
  - Includes inspirational Quranic verses and Hadith

### Cleanup (`cleanup_old_notifications`)

- **Frequency**: Daily at midnight
- **Purpose**: Maintains database performance
- **Logic**:
  - Removes notifications older than 30 days
  - Configurable retention period

## 🛠️ Management Commands

Use the `celery_manager.py` script to manage tasks:

```bash
# Test the reminder system
python3 celery_manager.py test-reminders

# Send manual reminder to a user
python3 celery_manager.py send-reminder 1 dhuhr 12:00

# Trigger consistency check
python3 celery_manager.py consistency-check

# Clean up old notifications
python3 celery_manager.py cleanup --days 30

# Analyze user prayer patterns
python3 celery_manager.py analyze 1 --days 30

# Check task status
python3 celery_manager.py status <task-id>

# List active tasks
python3 celery_manager.py list-active

# List scheduled tasks
python3 celery_manager.py list-scheduled
```

## 📊 Monitoring

### 1. Check Worker Status

```bash
# Check active workers
celery -A celery_config inspect active

# Check scheduled tasks
celery -A celery_config inspect scheduled

# Check worker stats
celery -A celery_config inspect stats
```

### 2. Monitor Task Execution

```bash
# Watch task execution in real-time
celery -A celery_config events

# Check task results
celery -A celery_config result <task-id>
```

### 3. View Logs

```bash
# Worker logs
tail -f celery_worker.log

# Beat scheduler logs
tail -f celery_beat.log
```

## 🔧 Configuration Options

### Celery Configuration (`celery_config.py`)

- **Broker**: Redis (configurable)
- **Result Backend**: Redis (configurable)
- **Task Serialization**: JSON
- **Timezone**: UTC
- **Concurrency**: 4 workers
- **Task Time Limits**: 5 minutes soft, 10 minutes hard

### Task Queues

- `prayer_reminders`: Prayer reminder tasks
- `consistency_checks`: Consistency analysis tasks
- `default`: General tasks

## 🚨 Troubleshooting

### Common Issues

1. **Redis Connection Error**
   ```bash
   # Check if Redis is running
   redis-cli ping
   # Should return: PONG
   ```

2. **Worker Not Processing Tasks**
   ```bash
   # Check worker status
   celery -A celery_config inspect active
   ```

3. **Tasks Not Scheduled**
   ```bash
   # Check beat scheduler
   celery -A celery_config inspect scheduled
   ```

4. **Email Not Sending**
   - Check SMTP configuration in `.env`
   - Verify email credentials
   - Check email service logs

### Debug Mode

```bash
# Run worker in debug mode
celery -A celery_config worker --loglevel=debug

# Run beat in debug mode
celery -A celery_config beat --loglevel=debug
```

## 📈 Performance Optimization

### 1. Worker Scaling

```bash
# Increase concurrency
celery -A celery_config worker --concurrency=8

# Run multiple workers
celery -A celery_config worker --hostname=worker1@%h
celery -A celery_config worker --hostname=worker2@%h
```

### 2. Redis Optimization

```bash
# Configure Redis for better performance
# In redis.conf:
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### 3. Database Optimization

- Index frequently queried columns
- Use connection pooling
- Regular cleanup of old data

## 🔒 Security Considerations

1. **Redis Security**
   - Use password authentication
   - Bind to localhost only
   - Use SSL in production

2. **Task Security**
   - Validate all task inputs
   - Use proper error handling
   - Log security events

3. **Email Security**
   - Use secure SMTP connections
   - Validate email addresses
   - Rate limit email sending

## 🚀 Production Deployment

### 1. Use Process Manager

```bash
# Install supervisor
sudo apt-get install supervisor

# Create supervisor config
sudo nano /etc/supervisor/conf.d/salah-tracker.conf
```

### 2. Supervisor Configuration

```ini
[program:salah-tracker-worker]
command=celery -A celery_config worker --loglevel=info
directory=/path/to/salah-tracker
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/salah-tracker/worker.log

[program:salah-tracker-beat]
command=celery -A celery_config beat --loglevel=info
directory=/path/to/salah-tracker
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/salah-tracker/beat.log
```

### 3. Environment Variables

```env
# Production settings
CELERY_BROKER_URL=redis://redis-server:6379/0
CELERY_RESULT_BACKEND=redis://redis-server:6379/0
FLASK_ENV=production
```

## 📝 API Integration

### Trigger Tasks via API

You can trigger tasks through your Flask API:

```python
from app.tasks.prayer_reminders import send_individual_reminder

# In your route
@app.route('/api/trigger-reminder', methods=['POST'])
@jwt_required()
def trigger_reminder():
    user_id = get_jwt_identity()
    result = send_individual_reminder.delay(user_id, 'dhuhr', '12:00')
    return jsonify({'task_id': result.id})
```

## 🎉 Success!

Your Celery background task system is now set up and running! The system will:

- ✅ Send prayer reminders every 5 minutes
- ✅ Check user consistency daily
- ✅ Clean up old data automatically
- ✅ Provide comprehensive monitoring
- ✅ Scale with your user base

## 📞 Support

If you encounter any issues:

1. Check the logs for error messages
2. Verify Redis is running
3. Ensure email configuration is correct
4. Use the management commands for debugging

Happy coding! 🚀
