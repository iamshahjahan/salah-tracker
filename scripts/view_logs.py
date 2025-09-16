#!/usr/bin/env python3
"""Simple log viewer for SalahTracker application.

This script provides a simple interface to view and search log files.
"""

import argparse
import os
from datetime import datetime


def list_log_files():
    """List all available log files."""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        print("❌ Logs directory not found!")
        return []

    log_files = []
    for file in os.listdir(log_dir):
        if file.endswith('.log'):
            file_path = os.path.join(log_dir, file)
            size = os.path.getsize(file_path)
            modified = datetime.fromtimestamp(os.path.getmtime(file_path))
            log_files.append({
                'name': file,
                'path': file_path,
                'size': size,
                'modified': modified
            })

    return sorted(log_files, key=lambda x: x['modified'], reverse=True)

def view_log_file(file_path, lines=50, follow=False):
    """View a log file."""
    if not os.path.exists(file_path):
        print(f"❌ Log file not found: {file_path}")
        return

    print(f"📄 Viewing: {file_path}")
    print("=" * 60)

    try:
        with open(file_path, encoding='utf-8') as f:
            if follow:
                # Follow mode - show last lines and continue
                print(f"Following last {lines} lines (Press Ctrl+C to stop)...")
                f.seek(0, 2)  # Go to end of file
                file_size = f.tell()
                f.seek(max(0, file_size - lines * 100))  # Approximate
                print(f.read())

                # Continue reading new lines
                while True:
                    line = f.readline()
                    if line:
                        print(line.rstrip())
                    else:
                        import time
                        time.sleep(0.1)
            else:
                # Show last N lines
                all_lines = f.readlines()
                start = max(0, len(all_lines) - lines)
                for line in all_lines[start:]:
                    print(line.rstrip())

    except KeyboardInterrupt:
        print("\n👋 Stopped following log file.")
    except Exception as e:
        print(f"❌ Error reading log file: {e}")

def search_logs(search_term, log_files=None):
    """Search for a term in log files."""
    if log_files is None:
        log_files = [f['path'] for f in list_log_files()]

    print(f"🔍 Searching for '{search_term}' in log files...")
    print("=" * 60)

    found_any = False
    for log_file in log_files:
        if not os.path.exists(log_file):
            continue

        try:
            with open(log_file, encoding='utf-8') as f:
                lines = f.readlines()
                matches = []
                for i, line in enumerate(lines, 1):
                    if search_term.lower() in line.lower():
                        matches.append((i, line.rstrip()))

                if matches:
                    found_any = True
                    print(f"\n📄 {os.path.basename(log_file)} ({len(matches)} matches):")
                    for line_num, line in matches[-10:]:  # Show last 10 matches
                        print(f"  {line_num:4d}: {line}")

        except Exception as e:
            print(f"❌ Error reading {log_file}: {e}")

    if not found_any:
        print(f"❌ No matches found for '{search_term}'")

def main():
    parser = argparse.ArgumentParser(description='SalahTracker Log Viewer')
    parser.add_argument('--list', '-l', action='store_true', help='List available log files')
    parser.add_argument('--view', '-v', help='View a specific log file')
    parser.add_argument('--lines', '-n', type=int, default=50, help='Number of lines to show (default: 50)')
    parser.add_argument('--follow', '-f', action='store_true', help='Follow log file (like tail -f)')
    parser.add_argument('--search', '-s', help='Search for a term in all log files')

    args = parser.parse_args()

    if args.list:
        log_files = list_log_files()
        if not log_files:
            print("❌ No log files found!")
            return

        print("📁 Available log files:")
        print("=" * 60)
        for log_file in log_files:
            size_mb = log_file['size'] / (1024 * 1024)
            print(f"📄 {log_file['name']}")
            print(f"   Size: {size_mb:.2f} MB")
            print(f"   Modified: {log_file['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            print()

    elif args.view:
        view_log_file(args.view, args.lines, args.follow)

    elif args.search:
        search_logs(args.search)

    else:
        # Interactive mode
        print("📊 SalahTracker Log Viewer")
        print("=" * 30)

        while True:
            print("\nOptions:")
            print("1. List log files")
            print("2. View log file")
            print("3. Search logs")
            print("4. Exit")

            choice = input("\nSelect option (1-4): ").strip()

            if choice == '1':
                log_files = list_log_files()
                if log_files:
                    print("\n📁 Available log files:")
                    for i, log_file in enumerate(log_files, 1):
                        size_mb = log_file['size'] / (1024 * 1024)
                        print(f"{i:2d}. {log_file['name']} ({size_mb:.2f} MB)")
                else:
                    print("❌ No log files found!")

            elif choice == '2':
                log_files = list_log_files()
                if not log_files:
                    print("❌ No log files found!")
                    continue

                print("\nSelect log file to view:")
                for i, log_file in enumerate(log_files, 1):
                    print(f"{i:2d}. {log_file['name']}")

                try:
                    file_choice = int(input("Enter file number: ")) - 1
                    if 0 <= file_choice < len(log_files):
                        lines = input("Number of lines to show (default 50): ").strip()
                        lines = int(lines) if lines.isdigit() else 50
                        view_log_file(log_files[file_choice]['path'], lines)
                    else:
                        print("❌ Invalid file number!")
                except ValueError:
                    print("❌ Please enter a valid number!")

            elif choice == '3':
                search_term = input("Enter search term: ").strip()
                if search_term:
                    search_logs(search_term)
                else:
                    print("❌ Please enter a search term!")

            elif choice == '4':
                print("👋 Goodbye!")
                break

            else:
                print("❌ Invalid choice!")

if __name__ == '__main__':
    main()
