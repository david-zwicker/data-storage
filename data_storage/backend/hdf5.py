'''
Created on Nov 12, 2015

@author: David Zwicker <dzwicker@seas.harvard.edu>
'''

from __future__ import division

import logging
import itertools
import os

import numpy as np
import h5py
import json

from .base import StorageBase



class StorageHDF5(StorageBase):
    """ manages a cache that is stored in a hdf5 file """

    def __init__(self, database_file, readonly=False, truncate=False):
        """ initialize the cache """
        super(StorageHDF5, self).__init__()
        
        self.readonly = readonly
        self.filename = database_file
                
        if truncate:
            h5py.File(self.filename, 'w').close()
        else:
            h5py.File(self.filename, 'a').close()

        # read the index from the database
        self._index = {}
        self._update_index()
          
          
    def delete_file(self):
        """ deletes the hdf5 file and thus clears the cache completely """
        os.remove(self.filename)
        self._index = {}
                  
          
    def _update_index(self):
        """ update the index from the database """
        logging.debug('Start reading the index from the hdf file')
        with h5py.File(self.filename, 'r') as db:
            self._index = {}
            for name, dataset in db.iteritems():
                args = json.loads(dataset.attrs['args'])
                kwargs = json.loads(dataset.attrs['kwargs'])
                key = self.get_key(args, kwargs)
                self._index[key] = name
        logging.debug('Found %d items in the hdf file', len(self))
        
        
    def __len__(self):
        """ return length of the storage """
        return len(self._index)


    def _retrieve_dataset(self, dataset):
        """ returns the (result, args, kwargs) from a hdf5 dataset """
        data_array = dataset[()]
        args = json.loads(dataset.attrs['args'])
        kwargs = json.loads(dataset.attrs['kwargs'])
        return data_array, args, kwargs


    def itervalues(self):
        """ iterates through all values """
        with h5py.File(self.filename, 'r') as db:
            for _, dataset in db.iteritems():
                yield self._retrieve_dataset(dataset)
               
                
    def __getitem__(self, key):
        """ retrieve data from hdf5 file """
        name = self._index[key]
        
        with h5py.File(self.filename, 'r') as db:
            result = self._retrieve_dataset(db[name])

        logging.debug('Loaded item `%s` from hdf file', name)
        
        return result


    def __setitem__(self, key, data):
        """ store new data in the hdf5 file """
        
        if self.readonly:
            raise IOError('Cannot write to readonly database')
        
        data_array, args, kwargs = data
        
        # determine the name of the key 
        name0 = str(hash(key))
        name = name0

        # make sure that the name is unique
        with h5py.File(self.filename, 'a') as db:
            for i in itertools.count():
                if name in db:
                    name = '%s_%03d' % (name0, i)
                else:
                    break
                
            # store the result
            dataset = db.create_dataset(name, data=np.asarray(data_array))
            dataset.attrs['args'] = json.dumps(args)
            dataset.attrs['kwargs'] = json.dumps(kwargs)
        
        # add the dataset to the index
        self._index[key] = name
        
        logging.debug('Stored item `%s` to hdf file', name)

