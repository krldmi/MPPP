"""PP Package initializer.
"""

import logging
import os
import pp.utils

BASE_PATH = os.path.sep.join(os.path.dirname(
    os.path.realpath(__file__)).split(os.path.sep)[:-4])

class NullHandler(logging.Handler):
    """Not-doing-anything handler for logging, so as to let the user choose if
    logging should be enabled.
    """
    def emit(self, record):
        """Do no write anything.
        """
        pass

LOG = logging.getLogger("pp").addHandler(NullHandler())

