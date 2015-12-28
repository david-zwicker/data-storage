'''
Created on Dec 28, 2015

@author: David Zwicker <dzwicker@seas.harvard.edu>
'''

from __future__ import division

import unittest
from itertools import izip_longest

import numpy as np



def arrays_close(arr1, arr2, rtol=1e-05, atol=1e-08, equal_nan=False):
    """ compares two arrays using a relative and an absolute tolerance """
    arr1 = np.atleast_1d(arr1)
    arr2 = np.atleast_1d(arr2)
    
    if arr1.shape != arr2.shape:
        # arrays with different shape are always unequal
        return False
        
    if equal_nan:
        # skip entries where both arrays are nan
        idx = ~(np.isnan(arr1) & np.isnan(arr2))
        if idx.sum() == 0:
            # occurs when both arrays are full of NaNs
            return True

        arr1 = arr1[idx]
        arr2 = arr2[idx]
    
    # get the scale of the first array
    scale = np.linalg.norm(arr1.flat, np.inf)
    
    # try to compare the arrays
    with np.errstate(invalid='raise'):
        try:
            is_close = np.any(np.abs(arr1 - arr2) <= (atol + rtol * scale))
        except FloatingPointError:
            is_close = False
        
    return is_close



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
    
    @classmethod
    def create_from_interpolated(cls, data_array, args, extra_args):
        """ create object from interpolated data """
        return cls(data_array, extra_args)
    
    def __eq__(self, other): 
        """ compare objects using their attributes """
        return self.__dict__ == other.__dict__    



class TestBase(unittest.TestCase):
    """ extends the basic TestCase class with some convenience functions """ 
      
    def assertAllClose(self, arr1, arr2, rtol=1e-05, atol=1e-08, msg=None):
        """ compares all the entries of the arrays a and b """
        try:
            # try to convert to numpy arrays
            arr1 = np.asanyarray(arr1)
            arr2 = np.asanyarray(arr2)
            
        except ValueError:
            # try iterating explicitly
            try:
                for v1, v2 in izip_longest(arr1, arr2):
                    self.assertAllClose(v1, v2, rtol, atol, msg)
            except TypeError:
                if msg is None:
                    msg = ""
                else:
                    msg += "; "
                raise TypeError(msg + "Don't know how to compare %s and %s"
                                % (arr1, arr2))
                
        else:
            if msg is None:
                msg = 'Values are not equal'
            msg += '\n%s !=\n%s)' % (arr1, arr2)
            is_close = arrays_close(arr1, arr2, rtol, atol, equal_nan=True)
            self.assertTrue(is_close, msg)
