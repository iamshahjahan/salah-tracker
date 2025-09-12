#!/usr/bin/env python3
"""
Celery task management script.

This script provides utilities for managing Celery tasks, testing the system,
and monitoring task execution.
"""

import os
import sys
import argparse
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from celery_config import celery_app
from app.tasks.prayer_reminders import (
    send_prayer_reminders,
    send_individual_reminder,
    test_reminder_system,
    cleanup_old_notifications
)
from app.tasks.consistency_checks import (
    check_user_consistency,
    analyze_prayer_patterns,
    send_weekly_report
)


def test_reminder_system_cmd():
    """Test the reminder system by sending test reminders."""
    print("🧪 Testing reminder system...")
    result = test_reminder_system.delay()
    print(f"✅ Test task queued with ID: {result.id}")
    print("Check the worker logs for results.")


def send_manual_reminder(user_id: int, prayer_type: str, prayer_time: str):
    """Send a manual prayer reminder to a specific user."""
    print(f"📧 Sending manual reminder to user {user_id}...")
    result = send_individual_reminder.delay(user_id, prayer_type, prayer_time)
    print(f"✅ Reminder task queued with ID: {result.id}")


def trigger_consistency_check():
    """Trigger a manual consistency check."""
    print("🔍 Triggering consistency check...")
    result = check_user_consistency.delay()
    print(f"✅ Consistency check queued with ID: {result.id}")


def cleanup_notifications(days: int = 30):
    """Clean up old notifications."""
    print(f"🧹 Cleaning up notifications older than {days} days...")
    result = cleanup_old_notifications.delay(days)
    print(f"✅ Cleanup task queued with ID: {result.id}")


def analyze_user_patterns(user_id: int, days: int = 30):
    """Analyze prayer patterns for a specific user."""
    print(f"📊 Analyzing prayer patterns for user {user_id} over {days} days...")
    result = analyze_prayer_patterns.delay(user_id, days)
    print(f"✅ Analysis task queued with ID: {result.id}")


def check_task_status(task_id: str):
    """Check the status of a specific task."""
    result = celery_app.AsyncResult(task_id)
    print(f"📋 Task Status: {result.status}")
    if result.info:
        print(f"📄 Task Info: {result.info}")


def list_active_tasks():
    """List all active tasks."""
    inspect = celery_app.control.inspect()
    active_tasks = inspect.active()
    
    if active_tasks:
        print("🔄 Active Tasks:")
        for worker, tasks in active_tasks.items():
            print(f"  Worker: {worker}")
            for task in tasks:
                print(f"    - {task['name']} (ID: {task['id']})")
    else:
        print("ℹ️  No active tasks found.")


def list_scheduled_tasks():
    """List all scheduled tasks."""
    inspect = celery_app.control.inspect()
    scheduled_tasks = inspect.scheduled()
    
    if scheduled_tasks:
        print("⏰ Scheduled Tasks:")
        for worker, tasks in scheduled_tasks.items():
            print(f"  Worker: {worker}")
            for task in tasks:
                print(f"    - {task['name']} (ETA: {task['eta']})")
    else:
        print("ℹ️  No scheduled tasks found.")


def main():
    parser = argparse.ArgumentParser(description='Celery Task Manager for Salah Tracker')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Test reminder system
    subparsers.add_parser('test-reminders', help='Test the reminder system')
    
    # Send manual reminder
    manual_parser = subparsers.add_parser('send-reminder', help='Send manual reminder')
    manual_parser.add_argument('user_id', type=int, help='User ID')
    manual_parser.add_argument('prayer_type', help='Prayer type (fajr, dhuhr, asr, maghrib, isha)')
    manual_parser.add_argument('prayer_time', help='Prayer time (HH:MM)')
    
    # Consistency check
    subparsers.add_parser('consistency-check', help='Trigger consistency check')
    
    # Cleanup
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old notifications')
    cleanup_parser.add_argument('--days', type=int, default=30, help='Days old (default: 30)')
    
    # Analyze patterns
    analyze_parser = subparsers.add_parser('analyze', help='Analyze user prayer patterns')
    analyze_parser.add_argument('user_id', type=int, help='User ID')
    analyze_parser.add_argument('--days', type=int, default=30, help='Days to analyze (default: 30)')
    
    # Check task status
    status_parser = subparsers.add_parser('status', help='Check task status')
    status_parser.add_argument('task_id', help='Task ID')
    
    # List tasks
    subparsers.add_parser('list-active', help='List active tasks')
    subparsers.add_parser('list-scheduled', help='List scheduled tasks')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'test-reminders':
            test_reminder_system_cmd()
        elif args.command == 'send-reminder':
            send_manual_reminder(args.user_id, args.prayer_type, args.prayer_time)
        elif args.command == 'consistency-check':
            trigger_consistency_check()
        elif args.command == 'cleanup':
            cleanup_notifications(args.days)
        elif args.command == 'analyze':
            analyze_user_patterns(args.user_id, args.days)
        elif args.command == 'status':
            check_task_status(args.task_id)
        elif args.command == 'list-active':
            list_active_tasks()
        elif args.command == 'list-scheduled':
            list_scheduled_tasks()
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    main()
