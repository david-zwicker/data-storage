'''
Created on Nov 12, 2015

@author: David Zwicker <dzwicker@seas.harvard.edu>
'''

from __future__ import division

from .base import StorageBase



class StorageMemory(dict, StorageBase):
    """ manages a cache that stores data in a dictionary """
    pass
