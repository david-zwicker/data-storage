'''
Created on Nov 7, 2015

@author: David Zwicker <dzwicker@seas.harvard.edu>
'''

from __future__ import division

import unittest




      
class TestFunctionCache(unittest.TestCase):
    """ unit tests for the continuous library """

    _multiprocess_can_split_ = True #< let nose know that tests can run parallel
    
    def test_simple(self):
        """ setup tests """
        
        @CacheMemory()
        def square(x, y):
            return x**2 + y
        
        a = square(2, 1)
        b = square(2, 1)
        self.assertEqual(a, b)
        
        