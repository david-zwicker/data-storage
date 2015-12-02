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

        # build the index of the database
        self._index = {}
        self.update_index()
          
          
    def delete_file(self):
        """ deletes the hdf5 file and thus clears the cache completely """
        if self.readonly:
            raise IOError('Cannot delete readonly database')

        os.remove(self.filename)
        self._index = {}
        
        
    def repack(self):
        """ rewrite the hdf5 file to make sure deleted data is removed """
        raise NotImplementedError 
                  
          
    def update_index(self):
        """ update the index from the database """
        logging.debug('Start reading the index from the hdf file')
        with h5py.File(self.filename, 'r') as db:
            self._index = {}
            for name, dataset in db.iteritems():
                if dataset.attrs.get('deleted', False):
                    continue
                args = json.loads(dataset.attrs['args'])
                kwargs = json.loads(dataset.attrs['kwargs'])
                key = self.get_key(args, kwargs)
                self._index[key] = name
        logging.debug('Found %d items in the hdf file', len(self))
        
        
    def __len__(self):
        """ return length of the storage """
        return len(self._index)


    def _retrieve_dataset(self, dataset, with_internal=True):
        """ returns the (result, args, kwargs) from a hdf5 dataset """
        
        if dataset.attrs.get('deleted', False):
            raise KeyError('Dataset has been deleted')
        
        data_array = dataset[()]
        args = json.loads(dataset.attrs['args'])
        kwargs = json.loads(dataset.attrs['kwargs'])
        
        if with_internal:
            internal_data = json.loads(dataset.attrs['internal_data'])
            return data_array, args, kwargs, internal_data
        else: 
            return data_array, args, kwargs


    def itervalues(self):
        """ iterates through all values """
        with h5py.File(self.filename, 'r') as db:
            for _, dataset in db.iteritems():
                yield self._retrieve_dataset(dataset)
               
                
    def iteritems(self):
        """ iterates through all values """
        with h5py.File(self.filename, 'r') as db:
            for key, name in self._index.iteritems():
                yield key, self._retrieve_dataset(db[name])
               
                
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
        
        data_array, args, kwargs, internal_data = data
        
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
            dataset.attrs['internal_data'] = json.dumps(internal_data)
        
        # add the dataset to the index
        self._index[key] = name
        
        logging.debug('Stored item `%s` to hdf file', name)


    def __delitem__(self, key):
        """ delete item with given key """ 
        if self.readonly:
            raise IOError('Cannot modify a readonly database')

        name = self._index[key]
        
        with h5py.File(self.filename, 'a') as db:
            db[name].attrs['deleted'] = True

        del self._index[key]

        logging.debug('Deleted item `%s` from hdf file', name)


