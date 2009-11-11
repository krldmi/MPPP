import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

LOG = logging.getLogger("pp").addHandler(NullHandler())

