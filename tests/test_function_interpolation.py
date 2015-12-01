'''
Created on Nov 7, 2015

@author: David Zwicker <dzwicker@seas.harvard.edu>
'''

from __future__ import division

import unittest
import tempfile

from data_storage import StorageMemory, interpolated
from data_storage.backend.hdf5 import StorageHDF5 


      
class TestFunctionInterpolation(unittest.TestCase):
    """ test caches using a simple dictionary as the storage backend """

    _multiprocess_can_split_ = True #< let nose know that tests can run parallel
    
    
    def setUp(self):
        """ initialize tests """
        self.storage = StorageMemory()

    
    def test_1d_1d(self):
        """ test a simple function """
        
        self.assertEqual(len(self.storage), 0)
        
        @interpolated(self.storage, max_distance=0.6)
        def func(x):
            return x**2
        
        a = func(1)
        self.assertEqual(len(self.storage), 1)
        self.assertEqual(a, 1**2)
        
        a = func(2)
        self.assertEqual(len(self.storage), 2)
        self.assertEqual(a, 2**2)
        
        a = func(1.5)
        self.assertEqual(len(self.storage), 2)
        self.assertAlmostEqual(a, 0.5*(1**2 + 2**2))
    
    
    def test_2d_2d(self):
        """ test a simple function """
        
        self.assertEqual(len(self.storage), 0)
        
        @interpolated(self.storage, max_distance=0.75)
        def func(x, y):
            return [x**2, y]
        
        a = func(1, 1)
        self.assertEqual(len(self.storage), 1)
        self.assertEqual(a, [1**2, 1])
        
        a = func(2, 1)
        self.assertEqual(len(self.storage), 2)
        self.assertEqual(a, [2**2, 1])
        
        a = func(1, 2)
        self.assertEqual(len(self.storage), 3)
        self.assertEqual(a, [1**2, 2])
        
        a = func(2, 2)
        self.assertEqual(len(self.storage), 4)
        self.assertEqual(a, [2**2, 2])
        
        a = func(1.5, 1.5)
        self.assertEqual(len(self.storage), 4)
        self.assertAlmostEqual(a[0], 0.5*(1**2 + 2**2))
        self.assertAlmostEqual(a[1], 1.5)
        
        
    def test_kwargs(self):
        """ test a simple function with keyword arguments """
        
        self.assertEqual(len(self.storage), 0)
        
        @interpolated(self.storage, max_distance=0.6)
        def func(x, e=2):
            return x**e
        
        a = func(1, e=2)
        self.assertEqual(len(self.storage), 1)
        self.assertEqual(a, 1**2)
        
        a = func(2, e=2)
        self.assertEqual(len(self.storage), 2)
        self.assertEqual(a, 2**2)
        
        a = func(1, e=3)
        self.assertEqual(len(self.storage), 3)
        self.assertEqual(a, 1**3)
        
        a = func(2, e=3)
        self.assertEqual(len(self.storage), 4)
        self.assertEqual(a, 2**3)
        
        a = func(1.5, e=2)
        self.assertEqual(len(self.storage), 4)
        self.assertAlmostEqual(a, 0.5*(1**2 + 2**2))
            
        a = func(1.5, e=3)
        self.assertEqual(len(self.storage), 4)
        self.assertAlmostEqual(a, 0.5*(1**3 + 2**3))       
        
        
    def test_ignore_kwargs(self):
        """ test a simple function with keyword arguments """
        
        self.assertEqual(len(self.storage), 0)
        
        @interpolated(self.storage, max_distance=0.6, ignore_kwargs=['e'])
        def func(x, e=2):
            return x**e
        
        a = func(1, e=2)
        self.assertEqual(len(self.storage), 1)
        self.assertEqual(a, 1**2)
        
        a = func(2, e=3)
        self.assertEqual(len(self.storage), 2)
        self.assertEqual(a, 2**3)
        
        a = func(1.5, e=2)
        self.assertEqual(len(self.storage), 2)
        self.assertAlmostEqual(a, 0.5*(1**2 + 2**3))
            
        
        
class TestFunctionInterpolationHDF5(TestFunctionInterpolation):
    """ test caches using a hdf5 as the storage backend """            
            
            
    def setUp(self):
        """ initialize tests """
        file_tmp = tempfile.NamedTemporaryFile(suffix='hdf5', delete=False)
        self.storage = StorageHDF5(file_tmp.name, truncate=True) 
        
        
    def tearDown(self):
        """ finalize tests """
        self.storage.delete_file()

