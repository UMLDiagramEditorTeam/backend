import multiprocessing
import os

bind = '0.0.0.0:8000'
worker_class = 'uvicorn.workers.UvicornWorker'
workers = int(os.getenv('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))

timeout = int(os.getenv('GUNICORN_TIMEOUT', '60'))
graceful_timeout = int(os.getenv('GUNICORN_GRACEFUL_TIMEOUT', '30'))
keepalive = int(os.getenv('GUNICORN_KEEPALIVE', '5'))

accesslog = os.getenv('GUNICORN_ACCESS_LOG', '-')
errorlog = os.getenv('GUNICORN_ERROR_LOG', '-')
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
reload = os.getenv('GUNICORN_RELOAD', 'false').lower() in {'1', 'true', 'yes', 'on'}
