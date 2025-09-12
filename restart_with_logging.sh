#!/bin/bash

# Script to restart all SalahTracker services with logging enabled

echo "🔄 Restarting SalahTracker services with logging..."

# Kill existing processes
echo "🛑 Stopping existing processes..."
pkill -f "python3 main.py" 2>/dev/null || true
pkill -f "start_celery_worker.py" 2>/dev/null || true
pkill -f "start_celery_beat.py" 2>/dev/null || true

# Wait a moment for processes to stop
sleep 2

# Create logs directory
mkdir -p logs

# Set log level environment variable
export LOG_LEVEL=INFO

echo "📝 Starting services with logging to files..."

# Start Flask app in background
echo "🚀 Starting Flask application..."
nohup python3 main.py > logs/flask_app.log 2>&1 &
FLASK_PID=$!
echo "   Flask app PID: $FLASK_PID"

# Start Celery worker in background
echo "👷 Starting Celery worker..."
nohup python3 start_celery_worker.py > logs/celery_worker.log 2>&1 &
WORKER_PID=$!
echo "   Celery worker PID: $WORKER_PID"

# Start Celery beat scheduler in background
echo "⏰ Starting Celery beat scheduler..."
nohup python3 start_celery_beat.py > logs/celery_beat.log 2>&1 &
BEAT_PID=$!
echo "   Celery beat PID: $BEAT_PID"

# Wait a moment for services to start
sleep 3

echo ""
echo "✅ All services started with logging enabled!"
echo ""
echo "📁 Log files location:"
echo "   - Main application logs: logs/salah_tracker_$(date +%Y%m%d).log"
echo "   - Celery logs: logs/celery_$(date +%Y%m%d).log"
echo "   - Error logs: logs/errors_$(date +%Y%m%d).log"
echo "   - Flask app output: logs/flask_app.log"
echo "   - Celery worker output: logs/celery_worker.log"
echo "   - Celery beat output: logs/celery_beat.log"
echo ""
echo "🔍 To monitor logs in real-time:"
echo "   tail -f logs/salah_tracker_$(date +%Y%m%d).log"
echo "   tail -f logs/celery_$(date +%Y%m%d).log"
echo "   tail -f logs/errors_$(date +%Y%m%d).log"
echo ""
echo "🛑 To stop all services:"
echo "   pkill -f 'python3 main.py'"
echo "   pkill -f 'start_celery_worker.py'"
echo "   pkill -f 'start_celery_beat.py'"
echo ""

# Save PIDs to file for easy management
echo "$FLASK_PID" > logs/flask.pid
echo "$WORKER_PID" > logs/worker.pid
echo "$BEAT_PID" > logs/beat.pid

echo "💾 Process IDs saved to logs/*.pid files"
