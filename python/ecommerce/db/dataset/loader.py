"""Dataset module for eCommerce package

This file implements the loader classes for the module.

A loader class is responsible for accessing a repository to
retrieve the dataset definition file for a given
< EntityType, DatasetName >.

Besides the base class, only a file system loader is provided.

Future implementations could include database access or AWS S3
acccess.

by Jose Luis Campanello
"""

import os
import os.path
import platform
import yaml

import ecommerce.config

from exceptions import DBDatasetConfigurationException, DBDatasetRuntimeException

#
# default config folders (as usual, windows is "special")
#
defaultFolders = [ './dataset', '{{module}}/dataset' ]
if platform.system() == "Windows":
    defaultFolders = [ '.\\dataset', '{{module}}\\dataset' ]
if "ECOMMERCE_DATASET_DIR" in os.environ:
    defaultFolders = os.environ["ECOMMERCE_DATASET_DIR"].split(":")

#
# dataset loaders
#
class DatasetLoader(object):
    """Base dataset loader class

    It has a cache of loaded datasets (entity type / dataset) and uses
    an abstract method (loadDataset) to load a dataset that is not
    already in the cache.
    """

    def __init__(self, config = None, prefix = None):
        # set internal vars
        self._prefix = prefix   # the config prefix
        self._entities = { }    # the cache


    def get(self, entity, dataset):
        """Return the requested dataset or exception if not found"""

        # check the cache first
        if entity not in self._entities:
            self._entities[entity] = { }
        if dataset not in self._entities[entity]:
            dcontents = self.loadDataset(entity, dataset)
            if dcontents is not None:
                # parse the file (if error raise)
                try:
                    self._entities[entity][dataset] = yaml.safe_load(dcontents)
                except:
                    raise DBDatasetRuntimeException(
                            "Syntax error in dataset file for [%s/%s]" %
                            (entity, dataset))

        # raise if not exists
        if dataset not in self._entities[entity]:
            raise KeyError("Dataset for [%s/%s] not found" % (entity, dataset))

        return self._entities[entity][dataset]


    def loadDataset(self, entity, dataset):
        """Tries to load the named entity/dataset"""
        raise NotImplementedError("loadDataset method not implemented")


class DatasetLoaderFileSystem(DatasetLoader):
    """File system dataset loader

    This class supports loading datasets from the file system. Gets information
    from a Config object or uses defaults.
    """

    def __init__(self, config = None, prefix = None):

        # base class init
        DatasetLoader.__init__(self, config, prefix)

        # prepare internal variables
        self._folders = defaultFolders
        if config is not None:
            self._folders = config.getMulti(prefix, "paths", defaultFolders)
        if self._folders is None:
            raise DBDatasetConfigurationException(
                    "Dataset Folder loader folders not defined")

        # find the folder
        self._folder = None
        for f in self._folders:
            self._folder = self._findFolder(f)
            if self._folder is not None:
                break

        # we better have a folder now or else... raise!
        if self._folder is None:
            raise DBDatasetConfigurationException(
                    "Dataset Folder loader cannot find a suitable folder from list %s" %
                    self._folders)


    def _findFolder(self, folder):
        """Return the folder name if it exists"""

        # if the path has a {{module}} try resolving for it
        if folder.find("{{module}}") > -1:
            # figure out this module absolute __file__ value
            try:
                modPath = os.path.abspath(os.path.dirname(__file__))
            except:
                modPath = ""     # empty replace (will not be found)
            folder = folder.replace("{{module}}", modPath)

        # return the folder if it exists, else None (will try the next)
        return folder if os.path.exists(folder) else None


    def loadDataset(self, entity, dataset):
        """Tries to load the named entity/dataset

        Returns one of:
        - An object if the dataset was located, loaded and parsed
        - An exception if there was a syntax error in the dataset contents
        - None if the dataset cannot be found

        The dataset can be specific (entity passed in) or generic (entity "__all__").
        Tries four files in order:
        - specific with extension ".yaml"
        - specific with extension ".json"
        - generic with extension ".yaml"
        - generic with extension ".json"

        It returns the first file that can be opened. If there is a syntax error in
        that file, then an exception is raised.
        """

        # check for entity/dataset
        specific = os.path.join(self._folder, entity,    dataset)
        generic  = os.path.join(self._folder, "__all__", dataset)
        paths = [ specific + ".yaml", specific + ".json", generic + ".yaml", generic + ".json" ]
        for path in paths:
            if os.path.exists(path):
                # open the file, read it, close it
                f = open(path, "r")
                dataset = f.read()
                f.close()

                return dataset

        # not found
        return None


# defined loaders  --- JUST ONE FOR NOW
_loaderDef = {
    "folder" : DatasetLoaderFileSystem
}

# global loader
_applicationLoaders = { }


def getLoader(application = "default"):
    """Return a Dataset Loader"""

    # sanity check
    if application is None:
        application = "default"

    if application not in _applicationLoaders:
        raise DBDatasetRuntimeException(
                  "Dataset Loader for Application [%s] not configured" %
                  application)

    return _applicationLoaders[application]


def createLoader(application = "default", config = None):
    """Create a Dataset Loader as specified by params"""

    global _applicationLoaders

    # sanity check
    if application is None:
        application = "default"

    # be sure we have a config
    if config is None:
        config = ecommerce.config.getConfig()
    if config is None:
        raise DBDatasetRuntimeException("Cannot initialize ecommerce.db.dataset: missing config")

    # figure out the prefix
    prefix = ("db" if application == "default" else application) + ".dataset"

    # get the loader
    lname = config.getMulti(prefix, "loader", "folder")
    if lname not in _loaderDef:
        raise DBDatasetConfigurationException("Dataset loader [%s] does not exists" % lname)

    # instantiate the appropriate loader
    _applicationLoaders[application] = _loaderDef[lname](config, prefix)

    # return the created loader
    return _applicationLoaders[application]


def loaderInitialize(config = None):
    """Initialize the loader mechanism"""

    # reset the loader list
    _applicationLoaders = { }

    # create default loader
    createLoader("default", config)

