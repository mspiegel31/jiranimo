from functools import wraps

def format_time(fn):
    @wraps(fn)
    def wrapper(*args):
        return fn(*args)/60.0**2
    return wrapper

def time(fn):
    """Times given function"""
    pass

def write(fn):
    """writes output of function """
    pass

def check_for_config_file(fn):
    pass
