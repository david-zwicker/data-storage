'''
Created on Nov 7, 2015

@author: David Zwicker <dzwicker@seas.harvard.edu>
'''

from __future__ import division

import os
import unittest
import tempfile

from data_storage import StorageMemory, cached
from data_storage.backend.hdf5 import StorageHDF5



class SimpleResult(object):
    """ simple object for testing storing objects """
     
    def __init__(self, data, e=2):
        """ create the simple object """
        self.data = data
        self.e = e
        
    def __repr__(self):
        """ return string representing the object """
        name = self.__class__.__name__
        return '%s(data=%s, e=%s)' % (name, self.data, self.e)
        
    def storage_prepare(self):
        """ prepare object for storage """
        return self.data, self.e
    
    @classmethod
    def storage_retrieve(cls, data_array, extra_data):
        """ create object from retrieved data """
        return cls(data_array, extra_data)
    
    def __eq__(self, other): 
        """ compare objects using their attributes """
        return self.__dict__ == other.__dict__    


      
class TestSimplestUsesage(unittest.TestCase):
    """ test caches using a simple dictionary as the storage backend """

    _multiprocess_can_split_ = True #< let nose know that tests can run parallel
    
    
    def test_simple(self):
        """ test a simple function """
        
        @cached()
        def square(x):
            return x**2
        
        a = square(2)
        self.assertEqual(a, square(2))
        
        b = square(3)
        self.assertNotEqual(a, b)
      
      
      
class TestFunctionCache(unittest.TestCase):
    """ test caches using a simple dictionary as the storage backend """

    _multiprocess_can_split_ = True #< let nose know that tests can run parallel
    
    
    def setUp(self):
        """ initialize tests """
        self.storage = StorageMemory()

    
    def test_simple(self):
        """ test a simple function """
        
        self.assertEqual(len(self.storage), 0)
        
        @cached(self.storage)
        def square(x, y):
            return x**2 + y
        
        a = square(2, 1)
        self.assertEqual(len(self.storage), 1)
        
        b = square(2, 1)
        self.assertEqual(a, b)
        self.assertEqual(len(self.storage), 1)        
        
        c = square(2, 2)
        self.assertNotEqual(a, c)
        self.assertEqual(len(self.storage), 2)        
        
        
    def test_clear(self):
        """ test clearing the cache """
        
        @cached(self.storage)
        def square(x):
            return x**2
        
        square(2)
        self.assertEqual(len(self.storage), 1)
        
        self.storage.clear()
        self.assertEqual(len(self.storage), 0)
        
        square(2)
        self.assertEqual(len(self.storage), 1)
        
        
    def test_clear_kwargs(self):
        """ test clearing the cache for particular keywords """
        
        @cached(self.storage)
        def square(x, e=2):
            return x**e
        
        square(2, e=2)
        self.assertEqual(len(self.storage), 1)
        square(2, e=3)
        self.assertEqual(len(self.storage), 2)
        
        self.storage.clear(kwargs={'e': 2})
        self.assertEqual(len(self.storage), 1)
        
        square(2, e=3)
        self.assertEqual(len(self.storage), 1)        
        square(2, e=2)
        self.assertEqual(len(self.storage), 2)        
        
        
    def test_ignore_args(self):
        """ test ignoring some of the arguments """
        
        @cached(self.storage, ignore_kwargs=['y'])
        def square(x, y):
            return x**2
        
        a = square(2, y=1)
        self.assertEqual(len(self.storage), 1)
        
        b = square(2, y=2)
        self.assertEqual(a, b)
        self.assertEqual(len(self.storage), 1)        
        
        c = square(3, 2)
        self.assertNotEqual(a, c)
        self.assertEqual(len(self.storage), 2)       
        
        
    def test_object(self):
        """ test caching of objects """
         
        @cached(self.storage)
        def square(x, e=2):
            return SimpleResult(x**e, e)
        
        a = square(2, e=2)
        self.assertEqual(len(self.storage), 1)
        self.assertEqual(a, square(2, e=2))

        b = square(2, e=3)
        self.assertEqual(len(self.storage), 2)
        self.assertEqual(b, square(2, e=3))
        
        self.storage.clear(kwargs={'e': 2})
        self.assertEqual(len(self.storage), 1)
        
        self.assertEqual(b, square(2, e=3))
        self.assertEqual(len(self.storage), 1)        

        self.assertEqual(a, square(2, e=2))
        self.assertEqual(len(self.storage), 2)  
        
                
        
class TestFunctionCacheHDF5(TestFunctionCache):
    """ test caches using a hdf5 as the storage backend """            
            
    def setUp(self):
        """ initialize tests """
        file_tmp = tempfile.NamedTemporaryFile(suffix='hdf5', delete=False)
        self.storage = StorageHDF5(file_tmp.name, temporary=True) 
        
        
    def test_repacke(self):
        """ test repacking the database """
        
        @cached(self.storage)
        def square(x, e=2):
            return x**e
        
        square(2, e=2)
        self.assertEqual(len(self.storage), 1)
        square(2, e=3)
        self.assertEqual(len(self.storage), 2)
        
        self.storage.repack()
        self.assertEqual(len(self.storage), 2)
        
        self.storage.clear(kwargs={'e': 2})
        self.assertEqual(len(self.storage), 1)

        size1 = os.stat(self.storage.filename).st_size
        self.storage.repack()
        size2 = os.stat(self.storage.filename).st_size
        self.assertEqual(len(self.storage), 1)
        
        self.assertGreater(size1, size2)
        

