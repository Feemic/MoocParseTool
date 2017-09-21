#count the func run time,the param 'times' is the how many the func runs
import time
from functools import wraps

def time_count(times=1):
    def outer_wrapper(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            for i in range(times):
                func(*args, **kwargs)
            print (time.time()-start)/times
        return wrapper
    return outer_wrapper



#single pattern
def singleton(cls):
    instances = {}
    @wraps(cls)
    def getinstance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return getinstance