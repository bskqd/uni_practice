import logging


def get_default_logging_configuration():
    return {
        'loggers': {
            'application.access': {
                'handlers': ['console', 'access'],
                'level': logging.INFO,
            },
            'application.errors': {
                'handlers': ['console', 'errors'],
                'level': logging.DEBUG,
            },
        },
        'handlers': {
            'console': {
                'class': logging.StreamHandler,
                'formatter': 'default',
            },
            'access': {
                'class': logging.FileHandler,
                'formatter': 'default',
                'filename': '/var/log/uni_wsgi/access.log',
            },
            'errors': {
                'class': logging.FileHandler,
                'formatter': 'default',
                'filename': '/var/log/uni_wsgi/errors.log',
            },
        },
        'formatters': {
            'default': {
                'fmt': '%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
                'datefmt': '[%Y-%m-%d %H:%M:%S %z]',
                'class': logging.Formatter,
            }
        }
    }


class FakeLogger:
    def critical(self, msg, *args, **kwargs):
        pass

    def error(self, msg, *args, **kwargs):
        pass

    def warning(self, msg, *args, **kwargs):
        pass

    def info(self, msg, *args, **kwargs):
        pass

    def debug(self, msg, *args, **kwargs):
        pass

    def exception(self, msg, *args, **kwargs):
        pass
