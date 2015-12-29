'''
Created on Dec 28, 2015

@author: David Zwicker <dzwicker@seas.harvard.edu>
'''

from __future__ import division

import numpy as np

from data_storage.provider.interpolate import Interpolator
from .base import TestBase



class TestFunctionInterpolation(TestBase):
    """ test caches using a simple dictionary as the storage backend """

    _multiprocess_can_split_ = True #< let nose know that tests can run parallel
    
    
    def test_1d_1d(self):
        """ test a simple 1d interpolation """
        
        interp = Interpolator(np.arange(4), np.arange(4))
        
        self.assertEqual(interp(1.5), 1.5)
        self.assertAllClose(interp([1.5, 2.5]), [1.5, 2.5])
    
    
    def test_1d_2d(self):
        """ test a simple 1d-2d interpolation """
        
        interp = Interpolator(np.arange(4), np.arange(8).reshape(4, 2))
        
        self.assertAllClose(interp(1.5), [3, 4])
        self.assertAllClose(interp([1.5, 2.5]), [[3, 4], [5, 6]])
        
    
    def test_2d_1d(self):
        """ test a simple 2d-1d interpolation """

        interp = Interpolator(np.random.randn(10, 2), np.random.randn(10, 1))
        
        self.assertEqual(interp([0.01, 0.01]).shape, (1,))
        self.assertEqual(interp([[0.01, 0.01], [-0.01, -0.01]]).shape, (2, 1))
        
        
    def test_2d_nd(self):
        """ test a simple 2d-nd interpolation """

        interp = Interpolator(np.random.randn(10, 2), np.random.randn(10, 3))
        
        self.assertEqual(interp([0.01, 0.01]).shape, (3,))
        self.assertEqual(interp([[0.01, 0.01], [-0.01, -0.01]]).shape, (2, 3))
              
                
    def test_1d_nmd(self):
        """ test a simple 1d-nmd interpolation """

        interp = Interpolator(np.arange(5), np.random.randn(5, 3, 2))
        
        self.assertEqual(interp(0.01).shape, (3, 2))
        self.assertEqual(interp([0.01, 0.01]).shape, (2, 3, 2))
                