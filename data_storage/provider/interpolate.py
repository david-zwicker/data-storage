'''
Created on Nov 8, 2015

@author: David Zwicker <dzwicker@seas.harvard.edu>
'''

from __future__ import division

import logging
import functools

import numpy as np
from scipy import interpolate, spatial

from ..backend.base import import_module
from ..backend.memory import StorageMemory



class Interpolator(object):
    """ helper class that does the interpolation """
    
    def __init__(self, points, values):
        """ initialize the interpolator with support points and associated 
        values """
        # make sure that the data is in the right shape
        self._points = np.asarray(points)

        if self._points.ndim < 2:
            # input space is one dimensional
            self._points = self._points[:, None]
            self.points_ndim = 1
        elif self._points.ndim > 2:
            # input space 
            raise ValueError('Input data must have at most two dimensions.')
        else:
            # input space is  
            self.points_ndim = 2

        self._values = np.asarray(values)
        if self._values.ndim == 1:
            self._values = self._values[:, None]
            self.values_shape = tuple()
        else:
            self.values_shape = self._values.shape[1:]


        assert self._points.shape[0] == self._values.shape[0]

        logging.info('Construct interpolator for function from R^%d to R^%d '
                     'from %d points', self._points.shape[1],
                     self._values.shape[1], self._points.shape[0])

        self._interpolator = None

    
    def get_distance(self, point):
        """ get minimal distance of a given point to the support points """
        if self._points.size == 0:
            return np.inf
        
        return spatial.distance.cdist(np.atleast_2d(self._points),
                                      np.atleast_2d(point)).min()
    
    
    def __call__(self, point):
        """ interpolate values at given point """
        point = np.asarray(point)
        
        if self._interpolator is None:
            if self.points_ndim == 1 or self._points.shape[1] == 1:
                # one-dimensional interpolation
                self._interpolator = interpolate.interp1d(
                          self._points.flat, self._values, axis=0, copy=False)
                
            else:
                # n-dimensional interpolation
                self._interpolator = interpolate.LinearNDInterpolator(
                                                    self._points, self._values)
        
        # determine the shape of the input points (without the interpolation
        # dimension)
        if self.points_ndim == 1:
            input_shape = point.shape
        else:
            input_shape = point.shape[:-1] 

        # reshape the output to produce correct dimensions
        result_shape = input_shape + self.values_shape
        return self._interpolator(point).reshape(result_shape)
        


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
        self._obj_extra_data = None
    
    
    def get_interpolator(self, kwargs):
        """ get the interpolator for the given kwargs """
        if self._interpolator is None or self._interpolator_kwargs != kwargs:
        
            logging.debug('Construct interpolator for kwargs: %s', kwargs)
        
            points = []
            values = []
            
            iterator = self.storage.iterdata(kwargs, ret_extra_data=True)
            for c_result, c_args, c_extra_data in iterator:
                points.append(np.array(c_args))
                values.append(c_result)
                self._obj_extra_data = c_extra_data #< store example extra data
                
            logging.debug('Found %d data points', len(values))
                    
            self._interpolator = Interpolator(points, values)
            
        return self._interpolator
    
    
    def __call__(self, func):
        """ decorate the given function """
        
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            # get the kwargs that go into the cache key
            if self.ignore_kwargs:
                kwargs_cache = {k: v
                                for k, v in kwargs.iteritems()
                                if k not in self.ignore_kwargs}
            else:
                kwargs_cache = kwargs

            # try to interpolate
            interpolator = self.get_interpolator(kwargs_cache)
            if interpolator.get_distance(args) <= self.max_distance:
                # use the interpolator to get the result
                result = interpolator(args)
                if self._obj_extra_data.has_key('obj_class'):
                    # result is an object and not just a numpy array
                    extra_data = self._obj_extra_data
                    module =  import_module(extra_data['obj_module'])
                    cls = getattr(module, extra_data['obj_class'])
                    result = cls.create_from_interpolated(
                                          result, args, extra_data['obj_props'])
                    
            else:
                # recalculate the result since support points are too far
                result = func(*args, **kwargs)
                self.storage.store(result, args=args, kwargs=kwargs_cache)
                self._interpolator = None #< devalidate interpolator
                
            return result
            
        return func_wrapper
    
    
    