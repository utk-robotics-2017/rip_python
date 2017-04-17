import __main__
import logging
import logging.handlers
import os
import sys
import time
import atexit
from .colors import color

logger = None


def Logger():
    global logger

    if logger is not None:
        return logger
    else:
        if hasattr(__main__, '__file__'):
            name = __main__.__file__[:-3]  # remove '.py'
        else:
            name = 'unknown'
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        fmt = '%(relativeCreated)6d - %(threadName)s - %(filename)s - %(levelname)s - %(message)s'
        # create file handler which logs even debug messages
        logfn = '/var/log/spine/{0:s}_{1:d}.log'.format(name, int(time.time()))

        class GroupWriteRotatingFileHandler(logging.handlers.RotatingFileHandler):
            def _open(self):
                prevumask = os.umask(0o000)
                rtv = logging.handlers.RotatingFileHandler._open(self)
                os.umask(prevumask)
                return rtv
        fh_ = GroupWriteRotatingFileHandler(logfn, maxBytes=1024 * 1024 * 5, backupCount=10)
        fh_.setLevel(logging.DEBUG)
        fh = logging.handlers.MemoryHandler(1024 * 1024 * 10, logging.ERROR, fh_)

        formatter = logging.Formatter(fmt)
        fh_.setFormatter(formatter)

        # create console handler with a higher log level
        class RepeatedMessageSteamHandler(logging.StreamHandler):
            previous_message = ""
            repeat_times = 0

            def __init__(self, *args, **kwargs):
                logging.StreamHandler.__init__(self, *args, **kwargs)

            def emit(self, record):
                global new_message
                if self.previous_message == record.getMessage():
                    new_message = False
                    self.repeat_times += 1
                    record.msg += " x%(repeat_times)d"
                    if isinstance(record.args, dict):
                        record.args['repeat_times'] = self.repeat_times
                        record.args['new_message'] = False
                    else:
                        record.args = {'repeat_times': self.repeat_times, 'new_message': False}
                else:
                    if isinstance(record.args, dict):
                        record.args['new_message'] = True
                    else:
                        record.args = {'new_message': True}
                    self.repeat_times = 1
                    self.previous_message = record.getMessage()
                    record.msg = record.msg
                super().emit(record)

        ch = RepeatedMessageSteamHandler()
        ch.setLevel(logging.INFO)

        class AnsiColorFormatter(logging.Formatter):
            def __init__(self, msgfmt=None, datefmt=None):
                self.formatter = logging.Formatter(msgfmt)
                self.first_time = True

            def format(self, record):
                s = self.formatter.format(record)

                if record.levelname == 'CRITICAL':
                    s = color(s, fg='red', style='negative')
                elif record.levelname == 'ERROR':
                    s = color(s, fg='red')
                elif record.levelname == 'WARNING':
                    s = color(s, fg='yellow')
                elif record.levelname == 'DEBUG':
                    s = color(s, fg='blue')
                elif record.levelname == 'INFO':
                    pass
                if record.args['new_message']:
                    if not self.first_time:
                        s = '\n' + s
                    else:
                        self.first_time = False
                return s
        ch.setFormatter(AnsiColorFormatter('\r' + fmt))

        ch.terminator = ''

        # add the handlers to logger
        logger.addHandler(fh)
        logger.addHandler(ch)

        def my_excepthook(excType, excValue, traceback, logger=logging):
            logger.error("Logging an uncaught exception", exc_info=(excType, excValue, traceback))
        sys.excepthook = my_excepthook
        return logger


@atexit.register
def del_logger():
    global logger
    for handler in logger.handlers:
        if handler.__class__.__name__ == 'RepeatedMessageSteamHandler':
            handler.stream.write('\n')
            handler.stream.flush()
