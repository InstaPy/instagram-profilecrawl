import logging
import os
import sys
import time
from .settings import Settings


class InstaLogger:
    logfolder = ''
    loggerobj = None

    def __init__(self):
        print('init log')

    @classmethod
    def logger(self):
        return self.get_logger(self, Settings.log_output_toconsole)

    def set_logfolder(self):
        self.logfolder = Settings.log_location + os.path.sep
        if not os.path.exists(self.logfolder):
            os.makedirs(self.logfolder)

    def set_logfile(self):
        if Settings.log_file_per_run is True:
            timestr = time.strftime("%Y-%m-%d-%H-%M-%S")
            file = '{}general'.format(self.logfolder) + ' ' + timestr + '.log'
        else:
            file = '{}general.log'.format(self.logfolder)
        return file

    def get_logger(self, show_logs):
        sys.stdout.reconfigure(encoding='utf-8')
        existing_logger = Settings.loggers.get(__name__)
        if existing_logger is not None:
            #print('logger already exists')
            return existing_logger
        else:
            #print('logger catch new one')
            self.set_logfolder(self)
            # initialize and setup logging system
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.DEBUG)

            logfile = self.set_logfile(self)
            file_handler = logging.FileHandler(logfile, encoding = 'UTF-8')

            file_handler.setLevel(logging.DEBUG)
            logger_formatter = logging.Formatter('%(levelname)s [%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(logger_formatter)
            logger.addHandler(file_handler)

            if show_logs == True:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.DEBUG)
                console_handler.setFormatter(logger_formatter)
                logger.addHandler(console_handler)

            # logger = logging.LoggerAdapter(logger)

            Settings.loggers[__name__] = logger
            Settings.logger = logger
            self.loggerobj = logger
            # self.get_logger(Settings.log_output_toconsole)
            return self.loggerobj
