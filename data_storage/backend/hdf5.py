'''
Created on Nov 12, 2015

@author: David Zwicker <dzwicker@seas.harvard.edu>
'''

from __future__ import division

import logging
import itertools
import os
import shutil
import tempfile

import numpy as np
import h5py
import json

from .base import StorageBase



class StorageHDF5(StorageBase):
    """ manages a cache that is stored in a hdf5 file """

    def __init__(self, database_file, readonly=False, truncate=False,
                 temporary=False):
        """ initialize the hdf5 database
        
        `database_file` denotes the filename where the database is stored
        `readonly` is a flag determining whether the database is readonly
        `truncate` is a flag determining whether the database will be cleared
            before usage
        `temporary` indicates whether the database file will be deleted when the
            objects is deleted
        """
        super(StorageHDF5, self).__init__()
        
        self.readonly = readonly
        self.filename = database_file
        self.temporary = temporary
                
        if truncate:
            h5py.File(self.filename, 'w').close()
        else:
            h5py.File(self.filename, 'a').close()

        # build the index of the database
        self._index = {}
        self.update_index()
        
        
    def __del__(self):
        """ called before the object is destroyed """
        if self.temporary:
            logging.debug('Delete the database file')
            os.remove(self.filename)
          

    def clear(self, time_max=None, kwargs=None):
        """ clears all items from the storage that have been saved before the
        given time `time_max`. If `time_max` is None, all the data is remove
        """
        if self.readonly:
            raise IOError('Cannot clear readonly database')

        if time_max is None and kwargs is None:
            # the database will be emptied
            h5py.File(self.filename, 'w').close()
            self._index = {}
            
        else:
            # potentially only a part of the database will be affected 
            super(StorageHDF5, self).clear(time_max, kwargs)
        
        
    def repack(self):
        """ rewrite the hdf5 file to make sure deleted data is removed """
        if self.readonly:
            raise IOError('Cannot repack readonly database')
        
        # generate temporary file and associated storage
        file_tmp = tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False)
        storage_tmp = StorageHDF5(file_tmp.name, truncate=True)

        logging.debug('Created temporary database at `%s`', file_tmp.name)
        
        # copy all data to temporary storage
        for value in self.itervalues():
            storage_tmp.store(*value)

        logging.debug('Copied data to temporary database')
            
        # copy temporary file to location of this file
        os.remove(self.filename)
        shutil.move(file_tmp.name, self.filename)
        
        # copy index of temporary storage to current object
        self._index = storage_tmp._index

        logging.debug('Substituted current database by the temporary one')
        
          
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
                if key in self._index:
                    logging.warn('Database contains key `%s` more than once.',
                                 key)
                self._index[key] = name
        logging.debug('Found %d items in the hdf file', len(self))
        
        
    def __len__(self):
        """ return length of the storage """
        return len(self._index)


    def _retrieve_dataset(self, dataset, with_internal=True):
        """ returns the (result, args, kwargs) from a hdf5 dataset """
        
        if dataset.attrs.get('deleted', False):
            raise KeyError('Dataset `%s` has been deleted' % dataset.name)
        
        data_array = dataset[()]
        args = json.loads(dataset.attrs['args'])
        if args is None:
            args = tuple()
        kwargs = json.loads(dataset.attrs['kwargs'])
        if kwargs is None:
            kwargs = {}
        
        if with_internal:
            internal_data = json.loads(dataset.attrs['internal_data'])
            return data_array, args, kwargs, internal_data
        else: 
            return data_array, args, kwargs


    def itervalues(self):
        """ iterates through all values """
        with h5py.File(self.filename, 'r') as db:
            for name in self._index.itervalues():
                yield self._retrieve_dataset(db[name])
               
                
    def iteritems(self):
        """ iterates through all keys and values """
        with h5py.File(self.filename, 'r') as db:
            for key, name in self._index.iteritems():
                yield key, self._retrieve_dataset(db[name])
               
                
    def __getitem__(self, key):
        """ retrieve data with given `key` from hdf5 file """
        name = self._index[key]
        
        with h5py.File(self.filename, 'r') as db:
            result = self._retrieve_dataset(db[name])
            
        logging.debug('Loaded item `%s` from hdf file', name)
        
        return result


    def __setitem__(self, key, data):
        """ store new `data` in the hdf5 file with a given `key` """
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
            raise IOError('Cannot delete from a readonly database')

        name = self._index[key]
        
        with h5py.File(self.filename, 'a') as db:
            db[name].attrs['deleted'] = True

        del self._index[key]

        logging.debug('Deleted item `%s` from hdf file', name)


