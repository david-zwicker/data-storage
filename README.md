# data-storage
Package that manages data persistently. This package focuses on sets of
numerical data, where each dataset consists of a single numpy array and some
auxiliary, descriptive data. 

The package supports multiple different backends and different data providers.
Data providers can for instance be function caches or interpolators, which
calculate the value of a function based on stored data.

## Initializing storage

The simplest storage container is a python dictionary in memory, which will of 
course not be persistent. It can be created by

    storage = StorageMemory()
    
This can be helpful for creating function caches.

If persistence is necessary, other storage engines can be used. One example is
a database based on hdf5, which requires the `h5py` package. It can be
initialized by

    storage = StorageHDF5(filename)
    
where `filename` points to a file where the database is stored


## Using storage

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


## Storage protocol for serializing objects

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
