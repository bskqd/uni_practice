from gunicorn import glogging

bind = '0.0.0.0:8000'
workers = 1
reload = True

accesslog = '-'

logging_format = '%(asctime)s [%(levelname)s] %(message)s'
glogging.Logger.access_fmt = logging_format
glogging.Logger.error_fmt = logging_format
