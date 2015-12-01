'''
Created on Nov 7, 2015

@author: David Zwicker <dzwicker@seas.harvard.edu>
'''

from __future__ import division

import unittest
import tempfile

from data_storage import StorageMemory
from data_storage.backend.hdf5 import StorageHDF5 


        
def Square(CachedCalculation):

    def __init__(self, x, cache_manager):
        self.x = x
    
    def calculate(self):
        self.res = self.x**2
        
    @classmethod
    def from_data(cls, data, attributes):
        """ reconstruct the object from the stored data """
        obj = cls(attributes['x'])
        obj.res = data
        return obj
        
    def to_data(self):
        """ serialize the object into a numpy array and attributes """
        return self.res, {'x': self.x}


        
def SquareExtra(Square):

    def __init__(self, x, attr):
        self.attr = attr
    
    @classmethod
    def from_data(cls, data, attributes):
        """ reconstruct the object from the stored data """
        obj = cls(attributes['x'])
        obj.res = data
        return obj
        
    def to_data(self):
        """ serialize the object into a numpy array and attributes """
        attr = self.attr
        attr.update(self.x)
        return self.res, {'x': self.x}



class TestClassCache(unittest.TestCase):
    """ test caches using a simple dictionary as the storage backend """

    _multiprocess_can_split_ = True #< let nose know that tests can run parallel
    
    
    def setUp(self):
        """ initialize tests """
        self.storage = StorageMemory()



        
        
class TestClassCacheHDF5(TestClassCache):
    """ test caches using a hdf5 as the storage backend """            
            
            
    def setUp(self):
        """ initialize tests """
        file_tmp = tempfile.NamedTemporaryFile(suffix='hdf5', delete=False)
        self.storage = StorageHDF5(file_tmp.name, truncate=True) 
        
        
    def tearDown(self):
        """ finalize tests """
        self.storage.delete_file()
