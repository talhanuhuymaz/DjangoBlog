import multiprocessing

# Gunicorn configuration
bind = "0.0.0.0:8000"
# Calculate workers based on CPU count but cap at 8
workers = min(multiprocessing.cpu_count() * 2 + 1, 8)
worker_class = 'gthread'
threads = 2
timeout = 120
accesslog = "-"
errorlog = "-"
# Logging configuration
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'