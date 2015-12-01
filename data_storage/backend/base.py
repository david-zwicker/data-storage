'''
Created on Nov 2, 2015

@author: zwicker

Stores the results of a python function in cache to speed up calculations.
The function can take any hashable arguments and must either return a numpy
array or a instance of CacheObject, which has information of how to save and
read data.
'''

import logging

import json

        

class StorageBase(object):
    """ base functionality of a cache manager
    This class is an abstract base class, which must be subclassed. Required
    methods to overwrite are __getitem__ and __setitem__, which have to 
    return/accept a tuple (result, args, kwargs). 
    """
    
    def __init__(self, typed_keys=False, strict_keys=False):
        super(StorageBase, self).__init__()


    def get_key(self, *args):
        """ returns a key suitable for caching """
        return json.dumps(args, sort_keys=True)

    
    def retrieve(self, args=None, kwargs=None):
        """ retrieves data based on given arguments and not based on the key """
        key = self.get_key(args, kwargs)
        logging.debug('Want to retrieve key `%s`', key)
        return self[key]

    
    def store(self, result, args=None, kwargs=None):
        """ store data based on given arguments """
        key = self.get_key(args, kwargs)
        logging.debug('Want to store key `%s`', key)
        self[key] = (result, args, kwargs)



        