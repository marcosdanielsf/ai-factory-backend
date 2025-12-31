"""
Gunicorn configuration for AI Factory API
==========================================
Performance-optimized configuration for Railway deployment.
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = max(2, multiprocessing.cpu_count() * 2 - 1)
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 120
keepalive = 5

# Process naming
proc_name = "ai-factory-api"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None
ssl_version = None
cert_reqs = 0
ca_certs = None
suppress_ragged_eof = True
do_handshake_on_connect = True
suppress_ragged_eof = True

# Application
preload_app = False
reload = False
reload_extra_files = []

# Server mechanics
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 30

# Optimization settings
raw_env = []
env = {
    "PYTHONUNBUFFERED": "true"
}

# Headers
permit_obsolete_folding = False
secure_scheme_header = "X-FORWARDED-PROTO"
secure_proxy_ssl_header = ("X-FORWARDED-PROTO", "https")
x_forwarded_for_header = "X-FORWARDED-FOR"
x_forwarded_proto_header = "X-FORWARDED-PROTO"
x_forwarded_port_header = "X-FORWARDED-PORT"
x_forwarded_host_header = "X-FORWARDED-HOST"

# Server mechanics
when_ready = None
before_fork = None
after_fork = None
before_exec = None
after_exec = None
pre_request = None
post_request = None
child_exit = None
server_int = None
server_close = None
init = None
cfg = None

# Settings from environment
if "GUNICORN_WORKERS" in os.environ:
    workers = int(os.getenv("GUNICORN_WORKERS"))

if "GUNICORN_WORKER_CLASS" in os.environ:
    worker_class = os.getenv("GUNICORN_WORKER_CLASS")

if "GUNICORN_TIMEOUT" in os.environ:
    timeout = int(os.getenv("GUNICORN_TIMEOUT"))

if "GUNICORN_BIND" in os.environ:
    bind = os.getenv("GUNICORN_BIND")
