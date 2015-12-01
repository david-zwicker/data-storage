'''
Created on Nov 7, 2015

@author: David Zwicker <dzwicker@seas.harvard.edu>
'''

from __future__ import division

import unittest
import tempfile

from data_storage import StorageMemory, cached
from data_storage.backend.hdf5 import StorageHDF5 


      
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
        
        
    def test_ignore_args(self):
        """ test ignoring some of the arguments """
        
        self.assertEqual(len(self.storage), 0)
        
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
        
        
        
class TestFunctionCacheHDF5(TestFunctionCache):
    """ test caches using a hdf5 as the storage backend """            
            
            
    def setUp(self):
        """ initialize tests """
        file_tmp = tempfile.NamedTemporaryFile(suffix='hdf5', delete=False)
        self.storage = StorageHDF5(file_tmp.name, truncate=True) 
        
        
    def tearDown(self):
        """ finalize tests """
        self.storage.delete_file()

