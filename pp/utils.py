
def ensure_dir(f):
    """Checks if the dir of f exists, otherwise create it.
    """
    import os
    d = os.path.dirname(f)
    if len(d) and not os.path.isdir(d):
        os.makedirs(d)

