import multiprocessing

bind = '0.0.0.0:8000'
worker_class = 'uvicorn.workers.UvicornWorker'
workers = multiprocessing.cpu_count() * 2 + 1
worker_connections = 1000

max_requests = 1000
max_requests_jitter = 50
timeout = 30
graceful_timeout = 30
keepalive = 5
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
reload_app = True
preload_app = True
