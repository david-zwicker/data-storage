'''
Created on Nov 12, 2015

@author: David Zwicker <dzwicker@seas.harvard.edu>
'''

from __future__ import division

import logging

from .base import StorageBase 

h5py = None #< lazy load



class StorageHDF5(StorageBase):
    """ manages the cache """

    def __init__(self, database_file, readonly=False, truncate=False):
        """ initialize the cache """
        self.readonly = readonly
        self.filename = database_file
        
        if h5py is None:
            # this raises an exception if h5py was not found
            import h5py
        
        if truncate:
            h5py.File(self.filename, 'w').close()
        else:
            h5py.File(self.filename, 'a').close()

        # read the index from the database
        self._update_index()
          
          
    def _update_index(self):
        """ update the index from the database """
        logging.debug('Start reading the index from the hdf file')
        with h5py.File(self.filename, 'r') as db:
            #print db.values()[0].attrs
            self.index = {}
            for name, data in db.iteritems():
                attrs = dict(data.attrs)
                attrs['dims'] = tuple(attrs['dims'])
                self.index[hashabledict(attrs)] = name
        logging.debug('Start reading the index from the hdf file')
        
                
    def __get_item__(self, key):
        """ retrieve data from cache """
        name = self._index[key]
        
        with h5py.File(self.filename, 'r') as db:
            data = db[name]
        # parameters = Parameters(dx=data.attrs['dx'], dims=data.attrs['dims'])
        return data
        #return GreensFunction(parameters, data.attrs['alpha'], data.attrs['x0'],
        #                      data[...])
#             

        
    def __setitem__(self, key, value):
        """ store new data in the cache """
        
        data_array, arguments = value
        
        if self.readonly:
            raise IOError('Cannot write to readonly database')
        
        # determine the name of the key 
        name0 = key[:32]
        name = name0
        
        # make sure that the name is unique
        with h5py.File(self.filename, 'a') as db:
            for i in itertools.count():
                if name in db:
                    if hashabledict(db[name].attrs) == key:
                        raise KeyError('Entry for key `%s` already exists' % key)
                    name = '%s_%03d' % (name0, i)
                else:
                    break
                
            # store the result
            data = db.create_dataset(name, data=value)
            data.attrs.update(key)
        
        # add the dataset to the index
        self.index[hashabledict(data.attrs)] = name
        
              