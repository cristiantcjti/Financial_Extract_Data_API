#!/usr/bin/env python
"""
Main entry point for the Financial Data API Django project.
Designed for PyCharm Run/Debug configurations.
"""
import argparse
import os
import sys
from pathlib import Path


def setup_django_environment():
    """Set up Django environment and configuration."""
    # Add the project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.config.settings')

    # Initialize Django
    import django
    django.setup()


def run_server(host='127.0.0.1', port='8000'):
    """Run Django development server."""
    from django.core.management import call_command
    print(f"🚀 Starting Financial Data API server at http://{host}:{port}")
    call_command('runserver', f'{host}:{port}')


def run_migrations():
    """Run database migrations."""
    from django.core.management import call_command
    print("🔄 Running database migrations...")
    call_command('migrate')
    print("✅ Migrations completed")


def run_tests():
    """Run the test suite."""
    from django.core.management import call_command
    print("🧪 Running tests...")
    call_command('test')


def create_superuser():
    """Create a Django superuser interactively."""
    from django.core.management import call_command
    print("👤 Creating superuser...")
    call_command('createsuperuser')


def run_celery_worker():
    """Run Celery worker."""
    import subprocess
    print("🔄 Starting Celery worker...")
    subprocess.run([
        'celery', '-A', 'src.config.celery', 'worker', '--loglevel=info'
    ])


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(description='Financial Data API Management')
    parser.add_argument(
        'command',
        nargs='?',
        default='runserver',
        choices=['runserver', 'migrate', 'test', 'createsuperuser', 'celery'],
        help='Command to run (default: runserver)'
    )
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host to bind the server to (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port',
        default='8001',
        help='Port to bind the server to (default: 8001)'
    )

    args = parser.parse_args()

    # Setup Django environment
    setup_django_environment()

    # Execute the requested command
    if args.command == 'runserver':
        run_server(args.host, args.port)
    elif args.command == 'migrate':
        run_migrations()
    elif args.command == 'test':
        run_tests()
    elif args.command == 'createsuperuser':
        create_superuser()
    elif args.command == 'celery':
        run_celery_worker()


if __name__ == '__main__':
    main()
