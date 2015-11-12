'''
Created on Nov 7, 2015

@author: David Zwicker <dzwicker@seas.harvard.edu>
'''

from __future__ import division

import unittest


        
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


class TestFunctionCache(unittest.TestCase):
    """ unit tests for the continuous library """

    _multiprocess_can_split_ = True #< let nose know that tests can run parallel
    
    def test_simple(self):
        """ setup tests """
