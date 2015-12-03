# data-storage
Package that manages data persistently. This package focuses on sets of
numerical data, where each dataset consists of a single numpy array and some
auxiliary, descriptive data. 

The package supports multiple different backends and different data providers.
Data providers can for instance be function caches or interpolators, which
calculate the value of a function based on stored data.
