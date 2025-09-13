#!/bin/bash

# Celery Management Script
# This script provides easy management of Celery workers and beat scheduler

APP_DIR="/var/www/salah-tracker"
VENV_DIR="$APP_DIR/venv"
LOG_DIR="$APP_DIR/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a process is running
is_running() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$pid_file"
            return 1
        fi
    fi
    return 1
}

# Function to start Celery worker
start_worker() {
    print_status "Starting Celery worker..."
    
    if is_running "$LOG_DIR/celery_worker.pid"; then
        print_warning "Celery worker is already running"
        return 0
    fi
    
    cd "$APP_DIR" || exit 1
    source "$VENV_DIR/bin/activate"
    
    # Start worker with specific queues
    nohup python3 -m celery -A celery_config worker \
        --loglevel=info \
        --concurrency=4 \
        --queues=prayer_reminders,consistency_checks,default \
        --hostname=worker@%h \
        --pidfile="$LOG_DIR/celery_worker.pid" \
        --logfile="$LOG_DIR/celery_worker.log" \
        --without-gossip \
        --without-mingle \
        --without-heartbeat \
        > "$LOG_DIR/celery_worker.log" 2>&1 &
    
    sleep 2
    
    if is_running "$LOG_DIR/celery_worker.pid"; then
        print_success "Celery worker started successfully"
        print_status "Worker PID: $(cat "$LOG_DIR/celery_worker.pid")"
    else
        print_error "Failed to start Celery worker"
        return 1
    fi
}

# Function to start Celery beat
start_beat() {
    print_status "Starting Celery beat scheduler..."
    
    if is_running "$LOG_DIR/celery_beat.pid"; then
        print_warning "Celery beat is already running"
        return 0
    fi
    
    cd "$APP_DIR" || exit 1
    source "$VENV_DIR/bin/activate"
    
    # Start beat scheduler
    nohup python3 -m celery -A celery_config beat \
        --loglevel=info \
        --pidfile="$LOG_DIR/celery_beat.pid" \
        --logfile="$LOG_DIR/celery_beat.log" \
        --detach \
        > "$LOG_DIR/celery_beat.log" 2>&1 &
    
    sleep 2
    
    if is_running "$LOG_DIR/celery_beat.pid"; then
        print_success "Celery beat started successfully"
        print_status "Beat PID: $(cat "$LOG_DIR/celery_beat.pid")"
    else
        print_error "Failed to start Celery beat"
        return 1
    fi
}

# Function to stop Celery services
stop_services() {
    print_status "Stopping Celery services..."
    
    # Stop worker
    if is_running "$LOG_DIR/celery_worker.pid"; then
        local worker_pid=$(cat "$LOG_DIR/celery_worker.pid")
        print_status "Stopping Celery worker (PID: $worker_pid)"
        kill "$worker_pid"
        rm -f "$LOG_DIR/celery_worker.pid"
        print_success "Celery worker stopped"
    else
        print_warning "Celery worker is not running"
    fi
    
    # Stop beat
    if is_running "$LOG_DIR/celery_beat.pid"; then
        local beat_pid=$(cat "$LOG_DIR/celery_beat.pid")
        print_status "Stopping Celery beat (PID: $beat_pid)"
        kill "$beat_pid"
        rm -f "$LOG_DIR/celery_beat.pid"
        print_success "Celery beat stopped"
    else
        print_warning "Celery beat is not running"
    fi
    
    # Kill any remaining Celery processes
    pkill -f "celery.*worker" 2>/dev/null || true
    pkill -f "celery.*beat" 2>/dev/null || true
}

# Function to restart services
restart_services() {
    print_status "Restarting Celery services..."
    stop_services
    sleep 2
    start_worker
    start_beat
}

# Function to check status
check_status() {
    print_status "Checking Celery services status..."
    
    echo "=========================================="
    echo "Celery Worker Status:"
    if is_running "$LOG_DIR/celery_worker.pid"; then
        local worker_pid=$(cat "$LOG_DIR/celery_worker.pid")
        print_success "Worker is running (PID: $worker_pid)"
    else
        print_error "Worker is not running"
    fi
    
    echo ""
    echo "Celery Beat Status:"
    if is_running "$LOG_DIR/celery_beat.pid"; then
        local beat_pid=$(cat "$LOG_DIR/celery_beat.pid")
        print_success "Beat is running (PID: $beat_pid)"
    else
        print_error "Beat is not running"
    fi
    
    echo ""
    echo "Active Tasks:"
    cd "$APP_DIR" || exit 1
    source "$VENV_DIR/bin/activate"
    celery -A celery_config inspect active 2>/dev/null || print_warning "Could not inspect active tasks"
    
    echo ""
    echo "Scheduled Tasks:"
    celery -A celery_config inspect scheduled 2>/dev/null || print_warning "Could not inspect scheduled tasks"
}

# Function to show logs
show_logs() {
    print_status "Showing Celery logs..."
    
    if [ -f "$LOG_DIR/celery_worker.log" ]; then
        echo "=== Celery Worker Logs ==="
        tail -20 "$LOG_DIR/celery_worker.log"
    fi
    
    if [ -f "$LOG_DIR/celery_beat.log" ]; then
        echo ""
        echo "=== Celery Beat Logs ==="
        tail -20 "$LOG_DIR/celery_beat.log"
    fi
}

# Function to show help
show_help() {
    echo "Celery Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start Celery worker and beat"
    echo "  stop        Stop all Celery services"
    echo "  restart     Restart all Celery services"
    echo "  status      Check status of Celery services"
    echo "  logs        Show recent logs"
    echo "  worker      Start only the worker"
    echo "  beat        Start only the beat scheduler"
    echo "  help        Show this help message"
    echo ""
    echo "Queue Configuration:"
    echo "  - prayer_reminders: For prayer reminder tasks"
    echo "  - consistency_checks: For consistency check tasks"
    echo "  - default: For other tasks"
}

# Main script logic
case "${1:-help}" in
    start)
        start_worker
        start_beat
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs
        ;;
    worker)
        start_worker
        ;;
    beat)
        start_beat
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
