# data-storage

Package that manages data persistently. This package focuses on sets of
numerical data, where each dataset consists of a single numpy array and some
auxiliary, descriptive data. 

The package supports multiple different backends and different data providers.
Data providers can for instance be function caches or interpolators, which
calculate the value of a function based on stored data.


## Simple Usage


### Initializing storage

The simplest storage container is a python dictionary in memory, which will of 
course not be persistent. It can be created by

    storage = StorageMemory()
    
This can be helpful for creating function caches.

If persistence is necessary, other storage engines can be used. One example is
a database based on hdf5, which requires the `h5py` package. It can be
initialized by

    storage = StorageHDF5(filename)
    
where `filename` points to a file where the database is stored


### Use storage

The simplest way to use storage is in a function cache. We provide a decorator
`cached`, which can be used as follows

    @cached(storage)
    def function(*args, **kwargs):
        ...
        
Here, the result of the function will be cached in the provided `storage`. If
a persistent storage is used, the function values will be available immediately
even after the python interpreter was restarted. Note that not all function
can be cached. In particular, the function arguments must be JSON-serializable.
Additionally, the return type of the function should be numeric, i.e. a simple
number or a numpy array. If the function returns an object, this object must
implement the storage protocol described in the next section.



## Advanced Usage

This section covers some advanced topics.


### Interpolating caching decorator

Despite the caching decorator, we also supply a special decorator which
interpolates between already calculated results. It can be used in a very
similar fashion to the cached decorator, but it will not calculate the function
for data points that are close to already calculated ones, but instead use these
data to (linearly) interpolate the result. A simple result reads


    @interpolated(StorageMemory(), max_distance=0.6)
    def func(x):
        return x**2
    
For instance, if `func(1)` and `func(2)` were called, a subsequent call to
`func(1.5)` will not evoke the calculation, but instead interpolate between the
previous two results and return 2.5 instead of 2.25.
Note that we only interpolate the result when it is closer than `max_distance` 
to a previously calculated result.


### Storage protocol for serializing objects

To support more flexible result types, we also support arbitrary python objects
as long as they support the storage protocol, which implements the serialization
of the object. An example for such an object is the following 

    class SimpleResult(object):
        """ simple object implementing the storage protocol """
         
        def __init__(self, data, arg=None):
            """ create the simple object """
            self.data = data
            self.arg = arg
            
        def storage_prepare(self):
            """ prepare object for storage """
            return self.data, {'arg': self.arg}
        
        @classmethod
        def storage_retrieve(cls, data_array, extra_data):
            """ create object from retrieved data """
            return cls(data_array, extra_data['arg'])

Here, the method `storage_prepare` serializes the object and returns a numpy
array and a structure that can be serialized using JSON. The class method
`storage_retrieve` then receives these two objects and reconstructs the object.
Instance of `SimpleResult` can now be returned by any function and will be
cached correctly.

If such custom objects should also be used with interpolated results, an extra
method has to be defined to support the construction of objects from 
interpolated data. Extending the example above, this could read

    class SimpleResultInterpolated(SimpleResult):
        """ simple object implementing the storage protocol with support for
        interpolation """
            
        @classmethod
        def create_from_interpolated(cls, data_array, args, extra_args):
            """ create object from interpolated data """
            return cls(data_array, extra_args)

Here, `data_array` contains the interpolated data and `args` is a list of 
arguments that were used for interpolation, i.e. the points at which the
interpolated results were calculated. The additional argument `extra_args`
contains the second item returned by a call to `storage_prepare` of one example
of the object from which we interpolate. This data can be helpful to fully
reconstruct the interpolated object.


