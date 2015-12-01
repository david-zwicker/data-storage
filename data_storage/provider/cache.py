'''
Created on Nov 2, 2015

@author: zwicker
'''

import functools
      
      

def cached(storage, ignore_kwargs=None):
    """ function that caches the result of the decorated function in the
    supplied storage provider """
    def cached_decorator(func):
        
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            if ignore_kwargs:
                kwargs_cache = {k: v
                                for k, v in kwargs.iteritems()
                                if k not in ignore_kwargs}
            else:
                kwargs_cache = kwargs
            
            try:
                return storage.retrieve(args, kwargs_cache)[0]
            except KeyError:
                result = func(*args, **kwargs)
                storage.store(result, args=args, kwargs=kwargs_cache)
                return result
            
        return func_wrapper
    return cached_decorator

