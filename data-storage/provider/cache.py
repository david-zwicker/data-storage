'''
Created on Nov 2, 2015

@author: zwicker
'''

import functools
      
      
# class CacheResult(object):
#     """ mixin class to make a class cacheable """ 
# 
#     def __init__(self, data, args, kwargs):
#         self.data = data
#         self.args = args
#         self.kwargs = kwargs
# 
#     @classmethod
#     def from_data(cls, data, attributes):
#         """ reconstruct the object from the stored data """
#         return cls(data, attributes)
#         
#         
#     def to_data(self):
#         """ serialize the object into a numpy array and attributes """
#         raise NotImplementedError
#         
#         
#     @classmethod
#     def from_data(cls, data, parameters, attributes):
#         """ reconstruct the object from the stored data """
#         obj = cls(attributes['function_name'])
#         obj.result = data
#         return obj
#         
#         
#     def to_data(self):
#         """ serialize the object into a numpy array and attributes """
#         return self.result, {'function_name': self.function_name}

      

def cached(storage):
    def cached_decorator(func):
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            key = storage.get_key(args, kwargs)
            try:
                return storage.retrieve(key, arg, kwargs)[0] #< only return data array
            except KeyError:
                result = function(*args, **kwargs)
                storage.store(key, result, args=args, kwargs=kwargs)
                return value
        return func_wrapper
    return cached_decorator

