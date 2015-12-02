'''
Created on Nov 2, 2015

@author: zwicker

Stores the results of a python function in cache to speed up calculations.
The function can take any hashable arguments and must either return a numpy
array or a instance of CacheObject, which has information of how to save and
read data.
'''

import logging
import time

import json

        

class StorageBase(object):
    """ base functionality of a cache manager
    This class is an abstract base class, which must be subclassed. Required
    methods to overwrite are __getitem__, __setitem__, __iter__, which have to 
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
        internal_data = {'time_stored': time.time()}
        logging.debug('Want to store key `%s`', key)
        self[key] = (result, args, kwargs, internal_data)
       
        
    def iterdata(self, kwargs):
        """ iterates through all data that is stored with the given kwargs """
        for value in self.itervalues():
            c_result, c_args, c_kwargs, _ = value
            if c_kwargs == kwargs:
                yield c_result, c_args, c_kwargs
        
        
    def clear(self, time_max=None, kwargs=None):
        """ clears all items from the storage that have been saved before the
        given time `time_max`. If `time_max` is None, all the data is remove
        """
        remove = []
        for key, value in self.iteritems():
            _, _, c_kwargs, c_internal_data = value
            delete_item = ((time_max is None
                            or c_internal_data['time_stored'] < time_max)
                           and (kwargs is None or c_kwargs == kwargs)) 
            if delete_item:
                remove.append(key)

        for key in remove:
            del self[key]
        

        