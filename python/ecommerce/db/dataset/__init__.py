"""Dataset module for eCommerce package

This module provides a mechanism to fetch related information for a database
entity. Each entity (EntityType, EntityId) can have multiple datasets defined.
When retrieved, each dataset can span multiple tables. The information is
retrieved and stored in a dictionary, keeping the same names as the database
schema. Each dataset is stored in a YAML file in a subdirectory with the name
of the EntityType (ex: dataset texts for PROD is stored as PROD/texts.yaml).
The only exception is that if the same exact dataset is configured for more than
one EntityType, it can be placed in directory __all__ (ex: __all__/texts.yaml).

An application can use the default config (that is fetched from db.dataset) or
it can use it's own. To do so, the application must call configApplication
passing in the name of the application and the place in the configuration where
the config is. Later, when trying to solve data, the application must pass the
same name as second parameter to fetch.

by Jose Luis Campanello
"""

import time
import traceback

import ecommerce.config
import ecommerce.db

from exceptions import DBDatasetConfigurationException, DBDatasetRuntimeException
from loader     import getLoader, loaderInitialize
from solver     import solve, solverInitialize

# the pre-process function
_preProcess = None


def setPreProcess(preProcess = None):
    """Sets the fetch list pre-process funcion

    This function receives the same parameters than the fetch function and
    can alter the entities. This is useful if some entity type can actually
    built represent many types of database entities that require different
    datasets. This function could change the dataset name according to some
    rules. For example, if <SUBJ, 1> is a category and <SUBJ, 2> is a
    subcategory, when the dataset subjectComments is passed in, it could be
    changed to subjectCommentsCategory and subjectCommentsSubcategory to
    accomodate differences in the database model.
    """

    global _preProcess

    # get the current
    current = _preProcess

    # set the new
    _preProcess = preProcess

    # always return the old pre-process function
    return current


def fetch(entities, application = None):
    """Returns datasets for each entity (EntityType, EntityId, DatasetName) passed

    The list of entities does not need to be homogeneous, meaning that the
    caller can pass in a Product (EntityType PROD) and a Contributor
    (EntityType CONT) or any other combination of things. The Dataset neither
    needs to be homogeneous. The output is in the same order as the input, except
    each entry is a 4-uple matching (EntityType, EntityId, Error, Data/Exception).

    Arguments:
    entities -- a list of 3-uples, each being < EntityType, EntityId, DatasetName >
    """

    #
    # give a chance to pre-process the fetch list and change it
    #
    if _preProcess is not None:
        entities = _preProcess(entities, application)

    #
    # a first pass thru the list is made to:
    #
    # 1- create a sublist of < EntityType, DatasetName > so SQL execution is optimal
    # 2- get a list of where each EntityType.EntityId.DatasetName goes on output list
    #
    dataOrder = { }
    fetchSets = { }
    for i in range(len(entities)):

        # handy data
        (entityType, entityId, datasetName) = entities[i]
        fetchSet = (entityType, datasetName)

        # build the fetch sets
        if fetchSet not in fetchSets:
            # build the entry
            fetchSets[fetchSet] = {
                "EntityType" : entityType,
                "Dataset"    : datasetName,
                "idList"     : [ ],
                "result"     : { }
            }
        # solve only once
        if entityId not in fetchSets[fetchSet]["idList"]:
            fetchSets[fetchSet]["idList"].append(entityId)

    # prepare the result (same length as input, filled with None)
    result = [ None ] * len(entities)

    #
    # solve each fetchSet and put the result in place
    #
    for f in fetchSets:

        # handy data
        entityType  = fetchSets[f]["EntityType"]
        datasetName = fetchSets[f]["Dataset"]
        idList      = fetchSets[f]["idList"]     # list of ids to resolve
        dataList    = None                       # expected list of results
                                                 # the position matches the id
        exception   = None                       # the exception (if any)

        # load the dataset and solve
        dataset = None
        try:
            dataset = getLoader(application).get(entityType, datasetName)
        except Exception as ex:
            # be sure to have a valid exception
            if not isinstance(ex, KeyError) and not isinstance(ex, DBDatasetRuntimeException):
                # something else
                err = traceback.format_exc()
                ex = DBDatasetRuntimeException(
                         "Generic Exception: type [%s] msg [%s], stack trace follows:\n%s" %
                         (ex.__class__.__name__, ex, err))
            exception = ex      # keep the exception

        # if we have a dataset, solve the set
        tStart = time.time()
        connSet = { }
        if dataset is not None:
            try:
                dataList = solve(dataset, entityType, datasetName, idList, connSet)
                dataList = { id : (False, dataList[id]) for id in dataList }
            except Exception as ex:
                # generate error
                err = traceback.format_exc()
                exception = DBDatasetRuntimeException(
                         "Generic Exception: type [%s] msg [%s], stack trace follows:\n%s" %
                         (ex.__class__.__name__, ex, err))
        tEnd = time.time()
        print "solving for %s/%s -- took %.3f seconds" % (entityType, datasetName, tEnd - tStart)

        # if no datalist, build it from the exceptions
        if dataList is None:
            dataList = { id : (True, exception) for id in idList }

        # set the result
        fetchSets[f]["result"] = dataList

    # build the result
    if False:
        result = { "entities" : entities, "fetchSets" : fetchSets }
    else:
        result = [ (entity[0],
                    entity[1],
                    fetchSets[ (entity[0], entity[2]) ]["result"].get(entity[1], ( True, "Missing key %s" % entity[1] ) )[0],
                    fetchSets[ (entity[0], entity[2]) ]["result"].get(entity[1], ( True, "Missing key %s" % entity[1] ) )[1])
                   for entity in entities ]

    return result


def configApplication(application, config = None):
    """Configures an application and sets the folder where the datasets are"""

    # tell the loader
    loader.createLoader(application, config)


def initialize(config = None):
    """Initialize the module with specific or default config"""

    # initialize the loader
    loaderInitialize(config)

    # initialize the solver
    solverInitialize(config)


# initialize
initialize()

# public methods
__all__ = [ "fetch", "initialize", "configApplication", "setPreProcess" ]

if __name__ == "__main__":
    print "Exports: ", __all__
