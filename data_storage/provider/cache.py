'''
Created on Nov 2, 2015

@author: zwicker
'''

import functools
import logging

from ..backend.memory import StorageMemory
      
      

def cached(storage=None, ignore_kwargs=None):
    """ function that caches the result of the decorated function in the
    supplied storage provider """
    
    if storage is None:
        storage = StorageMemory()
    
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
                logging.debug('Calculate function because of missed cache')
                result = func(*args, **kwargs)
                storage.store(result, args=args, kwargs=kwargs_cache)
                return result
            
        return func_wrapper
    return cached_decorator

