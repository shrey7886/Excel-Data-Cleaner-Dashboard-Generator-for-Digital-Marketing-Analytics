"""
Gunicorn configuration file for production deployment.
"""

import multiprocessing
import os
import sys
from pathlib import Path

# Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes - optimized for different environments
def get_workers():
    """Get optimal number of workers based on environment."""
    cpu_count = multiprocessing.cpu_count()

    # For Render free tier or low-resource environments
    if (os.environ.get('RENDER', False) or
            os.environ.get('MEMORY_LIMIT', '512M') == '512M'):
        return 2

    # For production with more resources
    return min(cpu_count * 2 + 1, 4)


workers = get_workers()
worker_class = "sync"
worker_connections = 1000
timeout = 120  # Increased from 30 to 120 seconds
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "targetorate"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if using HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Preload app for better performance
preload_app = True

# Worker timeout
graceful_timeout = 30


def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Server is ready. Spawning workers")
    server.log.info(f"Workers: {workers}")
    server.log.info(f"Bind: {bind}")
    server.log.info(
        f"Settings: {os.environ.get('DJANGO_SETTINGS_MODULE', 'sales_dashboard.settings')}"
    )


def worker_int(worker):
    """Called just after a worker has been initialized."""
    worker.log.info("Worker received INT or QUIT signal")


def pre_fork(server, worker):
    """Called just before a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)


def worker_abort(worker):
    """Called when a worker received SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")


def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("Forked child, re-executing.")


def on_reload(server):
    """Called to recycle workers during reload via SIGHUP."""
    server.log.info("Reloading workers")


def on_exit(server):
    """Called just before exiting Gunicorn."""
    server.log.info("Exiting gunicorn")


def worker_exit(server, worker):
    """Called when a worker exits."""
    server.log.info("Worker exited (pid: %s)", worker.pid)


def nworkers_changed(server, new_value, old_value):
    """Called when the number of workers is changed."""
    server.log.info("Number of workers changed from %s to %s", old_value, new_value)


def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting gunicorn server") 

