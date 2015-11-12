'''
Created on Nov 2, 2015

@author: zwicker

Stores the results of a python function in cache to speed up calculations.
The function can take any hashable arguments and must either return a numpy
array or a instance of CacheObject, which has information of how to save and
read data.
'''

import functools

from .kids_cache import hashing
 
            
            
class hashabledict(dict):
    def __hash__(self): 
        return hash(frozenset(self.iteritems()))            
  
        

class StorageBase(object):
    """ base functionality of a cache manager """
    
    def __init__(self, typed_keys=False, strict_keys=False):
        self._index = {}

        # choose a function that makes a key        
        self.get_key = hashing(typed_keys, strict_keys)

        
    def __call__(self, function):
        """
        return a cached version of the supplied function. This makes it possible
        to use the instance as a decorator.
        """
        # create the cached function        
        cached = CachedFunction(function, self)
        return cached

        # copy doc string and other details        
        return functools.wraps(function)(cached)
        
        
    def _arguments(self, args=None, kwargs=None):        
        
        attributes = kwargs.copy() if kwargs else {}
        
        if args:
            for k, value in enumerate(args):
                attributes['arg_%d' % k] = value

        return attributes
        
    
    def retrieve(self, args=None, kwargs=None, key=None):
        if key is None:
            key = self.get_key(args, kwargs)
        if self._index[key] == self._arguments(result, args, kwargs):
            return self[key]
        else:
            raise KeyError('Arguments did not match due to a hash collision.')

    
    def store(self, key, result, args=None, kwargs=None):
        arguments = self._arguments(args, kwargs)
        self[key] = (result, arguments)
        self._index[key] = arguments



        