import abc
import copy
import logging
from typing import Union, Optional


def get_default_logging_configuration():
    return {
        'loggers': {
            'application.errors': {
                'handlers': [
                    {
                        'level': logging.ERROR,
                        'handler': 'console',
                        'propagate': False,
                    },
                    {
                        'level': logging.ERROR,
                        'handler': 'errors',
                        'propagate': False,
                    },
                ],
                'level': logging.ERROR,
                'propagate': False,
            },
        },
        'handlers': {
            'console': {
                'class': logging.StreamHandler,
                'formatter': 'default',
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


class LoggerABC(abc.ABC):
    @abc.abstractmethod
    def debug(self, msg, *args, **kwargs):
        pass

    @abc.abstractmethod
    def info(self, msg, *args, **kwargs):
        pass

    @abc.abstractmethod
    def warning(self, msg, *args, **kwargs):
        pass

    @abc.abstractmethod
    def exception(self, msg, *args, **kwargs):
        pass

    @abc.abstractmethod
    def error(self, msg, *args, **kwargs):
        pass

    @abc.abstractmethod
    def critical(self, msg, *args, **kwargs):
        pass


class Logger(LoggerABC):
    logger_levels_ascending_order = (logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG)

    def __init__(self, configuration: dict):
        self.__configuration = configuration
        self.loggers = {}
        self.__configure_loggers()

    @property
    def configuration(self) -> dict:
        return copy.deepcopy(self.configuration)

    @configuration.setter
    def configuration(self, configuration: dict):
        self.__configuration = configuration
        self.__configure_loggers()

    def __configure_loggers(self):
        handlers = {}
        for handler_name in self.__configuration.get('handlers', {}):
            handler_data = self.__configuration['handlers'][handler_name].copy()
            handler_class = handler_data.pop('class')
            formatter_name = handler_data.pop('formatter', None)
            handler = handler_class(**handler_data,)
            if formatter_name:
                formatter_data = self.__configuration['formatters'][formatter_name].copy()
                formatter_class = formatter_data.pop('class')
                handler.setFormatter(formatter_class(**formatter_data))
            handlers[handler_name] = handler
        for logger_name, logger_data in self.__configuration.get('loggers', {}).items():
            logger = logging.getLogger(logger_name)
            logger_level = logger_data.get('level', logging.INFO)
            logger.setLevel(logger_level)
            logger.propagate = logger_data.get('propagate', True)
            for handler_data in logger_data.get('handlers', []):
                handler = copy.copy(handlers[handler_data['handler']])
                handler.setLevel(handler_data['level'])
                handler.propagate = handler_data.get('propagate', False)
                logger.addHandler(handler)
            if logger.propagate:
                logger_level_index = self.logger_levels_ascending_order.index(logger_level)
                for logger_level in self.logger_levels_ascending_order[:logger_level_index + 1]:
                    self.loggers.setdefault(logger_level, {})[logger_name] = logger
            else:
                self.loggers.setdefault(logger_level, {})[logger_name] = logger

    def debug(self, msg, *args, specified_loggers: tuple[str] = (), **kwargs):
        if not (loggers := self.__get_loggers(logging.DEBUG, specified_loggers)):
            return
        for logger in loggers:
            logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, specified_loggers: tuple[str] = (), **kwargs):
        if not (loggers := self.__get_loggers(logging.INFO, specified_loggers)):
            return
        for logger in loggers:
            logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, specified_loggers: tuple[str] = (), **kwargs):
        if not (loggers := self.__get_loggers(logging.WARNING, specified_loggers)):
            return
        for logger in loggers:
            logger.warning(msg, *args, **kwargs)

    def exception(self, msg, *args, exc_info=True, specified_loggers: tuple[str] = (), **kwargs):
        self.error(msg, *args, exc_info=exc_info, specified_loggers=specified_loggers, **kwargs)

    def error(self, msg, *args, specified_loggers: tuple[str] = (), **kwargs):
        if not (loggers := self.__get_loggers(logging.ERROR, specified_loggers)):
            return
        for logger in loggers:
            logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, specified_loggers: tuple[str] = (), **kwargs):
        if not (loggers := self.__get_loggers(logging.CRITICAL, specified_loggers)):
            return
        for logger in loggers:
            logger.critical(msg, *args, **kwargs)

    def __get_loggers(self, level: int, specified_loggers: tuple[str]) -> Optional[Union[list, tuple]]:
        if not (loggers := self.loggers.get(level)):
            return
        if specified_loggers:
            return [logger for logger_name, logger in loggers.items() if logger_name in specified_loggers]
        return tuple(loggers.values())
