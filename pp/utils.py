"""Module defining various utilities.
"""

def ensure_dir(filename):
    """Checks if the dir of f exists, otherwise create it.
    """
    import os
    directory = os.path.dirname(filename)
    if len(directory) and not os.path.isdir(directory):
        os.makedirs(directory)


def logging_on():
    """Turn logging on.
    """
    import logging
    import logging.config
    from pp import BASE_PATH
    import os.path
    
    logging.config.fileConfig(os.path.join(BASE_PATH, "etc", "logging.cfg"))
    #log = logging.getLogger("pp")
