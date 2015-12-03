'''
Created on Nov 8, 2015

@author: David Zwicker <dzwicker@seas.harvard.edu>
'''

from __future__ import division

import logging
import functools

import numpy as np
from scipy import interpolate, spatial

from ..backend.memory import StorageMemory



class Interpolator(object):
    """ helper class that does the interpolation """
    
    def __init__(self, points, values):
        """ initialize the interpolator with support points and associated 
        values """
        # make sure that the data is in the right shape
        self._points = np.asarray(points)
        if self._points.ndim == 1:
            self._points = self._points[:, None]

        self._values = np.asarray(values)
        if self._values.ndim == 1:
            self._values = self._values[:, None]

        assert self._points.shape[0] == self._values.shape[0]

        logging.debug('Construct interpolator for function from R^%d to R^%d '
                      'from %d points', self._points.shape[1],
                      self._values.shape[1], self._points.shape[0])

        self._interpolator = None

    
    def get_distance(self, point):
        """ get minimal distance of a given point to the support points """
        if self._points.size == 0:
            return np.inf
        return spatial.distance.cdist(np.atleast_2d(self._points),
                                      np.atleast_2d(point)).min()
    
    
    def interpolate(self, point):
        """ interpolate values at given point """
        if self._interpolator is None:
            if self._points.shape[1] == 1:
                # one-dimensional interpolation
                self._interpolator = interpolate.interp1d(
                          self._points.flat, self._values, axis=0, copy=False)
                
            else:
                # n-dimensional interpolation
                self._interpolator = interpolate.LinearNDInterpolator(
                                                    self._points, self._values)
        
        return self._interpolator(point)



class interpolated(object):
    """ function that caches the result of the decorated function in the
    supplied storage provider. If a requested data point is close enough to
    already calculated data points the result is calculated by interpolating
    between previous results instead. Here, the interpolation is done on all
    the values that are supplied by as positional arguments.    
    """
    
    def __init__(self, storage=None, max_distance=1, ignore_kwargs=None):
        """ initialize the decorator with a storage class and a cutoff distance
        determining the minimal distance to the closest support point """
        if storage is None:
            self.storage = StorageMemory()
        else:
            self.storage = storage
        self.max_distance = max_distance
        self.ignore_kwargs = ignore_kwargs
        
        self._interpolator = None
        self._interpolator_kwargs = None
    
    
    def get_interpolator(self, kwargs):
        """ get the interpolator for the given kwargs """
        if self._interpolator is None or self._interpolator_kwargs != kwargs:
        
            logging.debug('Construct interpolator for kwargs: %s', kwargs)
        
            points = []
            values = []
            
            for c_result, c_args, _ in self.storage.iterdata(kwargs):
                points.append(np.array(c_args))
                values.append(c_result)
                    
            self._interpolator = Interpolator(points, values)
            
        return self._interpolator
    
    
    def __call__(self, func):
        """ decorate the given function """
        
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            if self.ignore_kwargs:
                kwargs_cache = {k: v
                                for k, v in kwargs.iteritems()
                                if k not in self.ignore_kwargs}
            else:
                kwargs_cache = kwargs

            # try to interpolate
            interpolator = self.get_interpolator(kwargs_cache)
            if interpolator.get_distance(args) <= self.max_distance:
                return interpolator.interpolate(args)
            else:
                result = func(*args, **kwargs)
                self.storage.store(result, args=args, kwargs=kwargs_cache)
                self._interpolator = None #< devalidate interpolator
                return result
            
        return func_wrapper
    
    
    