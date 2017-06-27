import logging


class Error(Exception):
    def __init__(self, message):
        self.message = message
        logging.debug('camera: Error % s', message)

    def __str__(self):
        return '%s' % self.message
