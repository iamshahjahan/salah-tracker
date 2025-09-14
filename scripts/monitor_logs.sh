#!/bin/bash

# Script to monitor SalahTracker logs in real-time

echo "📊 SalahTracker Log Monitor"
echo "=========================="

# Get today's date for log file naming
TODAY=$(date +%Y%m%d)

echo "📁 Available log files:"
echo "   1. Main application logs (salah_tracker_${TODAY}.log)"
echo "   2. Celery logs (celery_${TODAY}.log)"
echo "   3. Error logs (errors_${TODAY}.log)"
echo "   4. Flask app output (flask_app.log)"
echo "   5. Celery worker output (celery_worker.log)"
echo "   6. Celery beat output (celery_beat.log)"
echo "   7. All logs combined"
echo "   8. Exit"
echo ""

while true; do
    echo -n "Select log file to monitor (1-8): "
    read choice
    
    case $choice in
        1)
            echo "📝 Monitoring main application logs..."
            echo "Press Ctrl+C to stop"
            tail -f logs/salah_tracker_${TODAY}.log
            ;;
        2)
            echo "👷 Monitoring Celery logs..."
            echo "Press Ctrl+C to stop"
            tail -f logs/celery_${TODAY}.log
            ;;
        3)
            echo "❌ Monitoring error logs..."
            echo "Press Ctrl+C to stop"
            tail -f logs/errors_${TODAY}.log
            ;;
        4)
            echo "🚀 Monitoring Flask app output..."
            echo "Press Ctrl+C to stop"
            tail -f logs/flask_app.log
            ;;
        5)
            echo "👷 Monitoring Celery worker output..."
            echo "Press Ctrl+C to stop"
            tail -f logs/celery_worker.log
            ;;
        6)
            echo "⏰ Monitoring Celery beat output..."
            echo "Press Ctrl+C to stop"
            tail -f logs/celery_beat.log
            ;;
        7)
            echo "📊 Monitoring all logs combined..."
            echo "Press Ctrl+C to stop"
            tail -f logs/salah_tracker_${TODAY}.log logs/celery_${TODAY}.log logs/errors_${TODAY}.log logs/flask_app.log logs/celery_worker.log logs/celery_beat.log
            ;;
        8)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Please select 1-8."
            ;;
    esac
    
    echo ""
    echo "Press Enter to continue..."
    read
done
