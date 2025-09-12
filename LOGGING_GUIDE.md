# 📊 SalahTracker Logging System

This guide explains how to use the comprehensive logging system implemented for SalahTracker.

## 🎯 Overview

The logging system captures all application activities, errors, and debugging information across:
- **Flask Application** - Main web application logs
- **Celery Workers** - Background task processing logs
- **Celery Beat Scheduler** - Scheduled task execution logs
- **Prayer Reminders** - Email notification system logs
- **Database Operations** - SQLAlchemy query logs
- **Error Tracking** - All errors and exceptions

## 📁 Log File Structure

```
logs/
├── salah_tracker_YYYYMMDD.log    # Main application logs
├── celery_YYYYMMDD.log           # Celery task logs
├── errors_YYYYMMDD.log           # Error-only logs
├── flask_app.log                 # Flask application output
├── celery_worker.log             # Celery worker output
├── celery_beat.log               # Celery beat scheduler output
├── flask.pid                     # Flask process ID
├── worker.pid                    # Celery worker process ID
└── beat.pid                      # Celery beat process ID
```

## 🚀 Quick Start

### 1. Start Services with Logging
```bash
./restart_with_logging.sh
```

### 2. Monitor Logs in Real-Time
```bash
# Monitor main application logs
tail -f logs/salah_tracker_$(date +%Y%m%d).log

# Monitor Celery logs
tail -f logs/celery_$(date +%Y%m%d).log

# Monitor error logs
tail -f logs/errors_$(date +%Y%m%d).log
```

### 3. Use the Log Viewer
```bash
# Interactive log viewer
./view_logs.py

# List all log files
./view_logs.py --list

# View specific log file
./view_logs.py --view logs/salah_tracker_20250912.log

# Search logs
./view_logs.py --search "prayer reminder"

# Follow log file (like tail -f)
./view_logs.py --view logs/salah_tracker_20250912.log --follow
```

## 📋 Log Levels

The system supports different log levels controlled by the `LOG_LEVEL` environment variable:

- **DEBUG** - Detailed information for debugging
- **INFO** - General information about application flow
- **WARNING** - Warning messages for potential issues
- **ERROR** - Error messages for failed operations
- **CRITICAL** - Critical errors that may cause application failure

### Set Log Level
```bash
export LOG_LEVEL=DEBUG  # For detailed debugging
export LOG_LEVEL=INFO   # For normal operation (default)
export LOG_LEVEL=ERROR  # For error-only logging
```

## 🔍 Log Monitoring Commands

### Real-Time Monitoring
```bash
# Monitor all logs simultaneously
tail -f logs/salah_tracker_$(date +%Y%m%d).log logs/celery_$(date +%Y%m%d).log logs/errors_$(date +%Y%m%d).log

# Monitor specific service
tail -f logs/flask_app.log
tail -f logs/celery_worker.log
tail -f logs/celery_beat.log
```

### Search and Filter
```bash
# Search for specific terms
grep "prayer reminder" logs/salah_tracker_$(date +%Y%m%d).log
grep "ERROR" logs/errors_$(date +%Y%m%d).log
grep "email sent" logs/celery_$(date +%Y%m%d).log

# Count occurrences
grep -c "reminder sent" logs/celery_$(date +%Y%m%d).log
```

### Log Analysis
```bash
# View last 100 lines
tail -100 logs/salah_tracker_$(date +%Y%m%d).log

# View logs from specific time
grep "2025-09-12 20:" logs/salah_tracker_$(date +%Y%m%d).log

# View only errors
grep "ERROR\|CRITICAL" logs/salah_tracker_$(date +%Y%m%d).log
```

## 📊 Log File Rotation

The logging system automatically rotates log files to prevent them from growing too large:

- **Main Logs**: Rotate at 10MB, keep 5 backup files
- **Error Logs**: Rotate at 5MB, keep 3 backup files
- **Daily Rotation**: New log files created daily with date suffix

## 🛠️ Service Management

### Start Services
```bash
./restart_with_logging.sh
```

### Stop Services
```bash
# Stop all services
pkill -f 'python3 main.py'
pkill -f 'start_celery_worker.py'
pkill -f 'start_celery_beat.py'

# Or use the PIDs
kill $(cat logs/flask.pid)
kill $(cat logs/worker.pid)
kill $(cat logs/beat.pid)
```

### Check Service Status
```bash
# Check if services are running
ps aux | grep "python3 main.py"
ps aux | grep "start_celery_worker.py"
ps aux | grep "start_celery_beat.py"
```

## 🔧 Configuration

### Environment Variables
```bash
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
export LOG_LEVEL=INFO

# Log directory (default: logs)
export LOG_DIR=logs
```

### Customizing Log Format
Edit `logging_config.py` to modify:
- Log message format
- File rotation settings
- Log level thresholds
- Output destinations

## 📈 Monitoring Prayer Reminders

### Check Reminder Status
```bash
# Search for reminder activities
grep "prayer reminder" logs/celery_$(date +%Y%m%d).log

# Check for errors in reminders
grep "Error processing user" logs/celery_$(date +%Y%m%d).log

# Monitor email sending
grep "email sent" logs/celery_$(date +%Y%m%d).log
```

### Debug Reminder Issues
```bash
# Set debug level for detailed logging
export LOG_LEVEL=DEBUG
./restart_with_logging.sh

# Monitor in real-time
tail -f logs/celery_$(date +%Y%m%d).log
```

## 🚨 Troubleshooting

### Common Issues

1. **No log files created**
   - Check if `logs/` directory exists
   - Verify write permissions
   - Check if services are running

2. **Logs not updating**
   - Restart services with `./restart_with_logging.sh`
   - Check if processes are running
   - Verify log file permissions

3. **Too many log files**
   - Log rotation should handle this automatically
   - Manually clean old files if needed: `rm logs/*.log.1`

4. **Missing error logs**
   - Check if errors are being logged to main log file
   - Verify error log file permissions
   - Check log level settings

### Debug Commands
```bash
# Check log file sizes
ls -lh logs/

# Check log file permissions
ls -la logs/

# Check if services are writing to logs
lsof logs/salah_tracker_$(date +%Y%m%d).log
```

## 📝 Log Examples

### Successful Prayer Reminder
```
2025-09-12 20:58:00 - app.tasks.prayer_reminders - INFO - Starting prayer reminders task
2025-09-12 20:58:00 - app.tasks.prayer_reminders - INFO - Found 1 eligible users for reminders
2025-09-12 20:58:00 - app.tasks.prayer_reminders - INFO - Processing user: user@example.com (ID: 1)
2025-09-12 20:58:01 - app.tasks.prayer_reminders - INFO - Prayer reminders task completed: {'status': 'completed', 'reminders_sent': 1, 'errors': 0}
```

### Error Example
```
2025-09-12 20:58:00 - app.tasks.prayer_reminders - ERROR - Error processing user user@example.com: Connection timeout
```

## 🎯 Best Practices

1. **Regular Monitoring**: Check logs daily for errors and issues
2. **Log Rotation**: Let the system handle log rotation automatically
3. **Error Alerts**: Set up monitoring for ERROR and CRITICAL log levels
4. **Backup Logs**: Keep important log files for debugging
5. **Performance**: Use appropriate log levels to avoid performance impact

## 📞 Support

If you encounter issues with the logging system:
1. Check this guide first
2. Review the log files for error messages
3. Verify service status and configuration
4. Check file permissions and disk space

---

**Happy Logging! 📊✨**
