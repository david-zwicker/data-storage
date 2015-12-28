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
import sys

import json

        
        
def import_module(path):
    """ imports a whole module path """
    module = __import__(path)
    for name in path.split(".")[1:]:
        module = getattr(module, name)
    return module        
        
        

class StorageBase(object):
    """ base functionality of a cache manager
    This class is an abstract base class, which must be subclassed. Required
    methods to overwrite are __getitem__, __setitem__, __iter__, which have to 
    return/accept a tuple (result, args, kwargs). 
    """
    
    def __init__(self, typed_keys=False, strict_keys=False):
        """ initialize the storage object """
        super(StorageBase, self).__init__()


    def get_key(self, *args):
        """ returns a key suitable for caching """
        return json.dumps(args, sort_keys=True)

    
    def retrieve(self, args=None, kwargs=None):
        """ retrieves data based on given arguments and not based on the key """
        key = self.get_key(args, kwargs)
        logging.debug('Want to retrieve key `%s`', key)
        (data_array, args, kwargs, extra_data) = self[key]
        
        if 'obj_class' in extra_data:
            # recreate the obj from storage
            try:
                module =  import_module(extra_data['obj_module'])
                cls = getattr(module, extra_data['obj_class'])
                result = cls.storage_retrieve(data_array,
                                              extra_data['obj_props'])
            except KeyError:
                # reraise KeyError as different exception to distinguish it from
                # data key not existing
                e_type, e_value, traceback = sys.exc_info()
                args = ("Format of stored data is unexpected", e_type, e_value)
                raise (ValueError, args, traceback)
            
        else:
            # assume that a simple numpy array was stored
            result = data_array
        
        return (result, args, kwargs, extra_data)

    
    def store(self, result, args=None, kwargs=None, internal_data=None):
        """ store data based on given arguments """
        key = self.get_key(args, kwargs)
        
        extra_data = {'time_stored': time.time()}
        if internal_data:
            extra_data.update(internal_data)
        
        try:
            # assume that result is an object that supports the storage protocol
            data_array, properties = result.storage_prepare()
            class_name = result.__class__.__name__
            extra_data['obj_module'] = result.__class__.__module__ 
            extra_data['obj_class'] = class_name
            extra_data['obj_props'] = properties
            logging.debug('Store object `%s` to key `%s`', class_name, key)
            
        except AttributeError:
            # otherwise, we assume that it is already a simple numpy array
            data_array = result
            logging.debug('Store numpy array to key `%s`', key)
        
        self[key] = (data_array, args, kwargs, extra_data)
       
        
    def iterdata(self, kwargs, ret_extra_data=False):
        """ iterates through all data that is stored with the given kwargs """
        for value in self.itervalues():
            c_result, c_args, c_kwargs, c_extra_data = value
            if c_kwargs == kwargs:
                if ret_extra_data:
                    yield c_result, c_args, c_extra_data
                else:
                    yield c_result, c_args
        
        
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

        