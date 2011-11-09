"""Dataset module for eCommerce package

This file implements the solve function for the module.

The solve function receives the parsed dataset and the list of ids and
does what is needed to retrieve the information from the database.

by Jose Luis Campanello
"""

import os
import os.path
import platform
import importlib
import yaml
import types

import ecommerce.config
import ecommerce.db

from exceptions import DBDatasetConfigurationException, DBDatasetRuntimeException
from coercion import performCoercion


# default database
_defaultDB = None

# imported code libraries
_code = { }


def solve(dataset, entityType, datasetName, idList):
    """Solve the dataset for the list of entities

    The received dataset (a dictionary) is used to fetch information
    for each entry in idList (just a single id is supported now).
    The result is a list with a 4-uple of the form < EntityType,
    EntityId, Boolean for exception (true), data or exception >. The
    list is returned in the same order indicated by idList.
    """

    # figure out the type of result
    single = dataset.get("single", False)

    # set an empty result
    result = None

    # execute the query or code (if any)
    result = solveMain(dataset, entityType, datasetName, idList)

    # do augmentation ONLY if single
    if single:

        # get the augment result (if any)
        partial = solveAugment(dataset, entityType, datasetName, idList)

        # import the augment result into the result
        if partial is not None:
            # be sure we have a dictionary
            if result is None:
                result = { }
            for p in partial:
                result[p] = partial[p]

        # return the same for each input entity
        result = { id: result for id in idList }

    return result


def solveMain(dataset, entityType, datasetName, idList):
    """Generic solve that decides if sql or code must be executed

    This returns a dictionary where each entry of idList is a key and
    the value is the data.
    """

    # no result
    result = None

    # figure out if solving for query or code (if any at all)
    #
    # NOTE: check for query first because is the most used
    #
    if dataset.get("query.sql") is not None:
        # execute the query and import the result
        result = solveQuery(dataset, entityType, datasetName, idList)
    else:
        if dataset.get("code.name") is not None:
            # execute the named function
            result = solveCode(dataset, entityType, datasetName, idList)

    return result


def solveAugment(dataset, entityType, datasetName, idList, attributeName = "augment"):
    """Solve the augment set and return a dictionary with the results"""

    # this always returns a dictionary
    result = { }

    # process augmented columns (if any and result is single!)
    augment = dataset.get(attributeName, None)
    if augment is not None:

        # iterate each augment entry
        for a in augment:

            # solve the query or code
            result[a] = solveMain(augment[a], entityType, datasetName, idList)

    return result


def solveQuery(dataset, entityType, datasetName, idList):
    """Solve the query, possibly doing a manual join of augments

    This returns a dictionary where each key is an id from idList and
    the value is the data associated to that key.
    """

    # if we have augment, solve them
    augmenting = False
    augment = { }
    if dataset.get("query.augment") is not None:
        augmenting = True
        augment = solveAugment(dataset, entityType, datasetName, idList, "query.augment")

    # build the query
    query = solveQuerySQL(dataset, entityType, datasetName, idList)

    # get the column list and the pk list
    columns = dataset.get("query.columns")
    if columns is None:
        raise DBDatasetConfigurationException(
                  "query.columns not present in [%s/%s]" %
                  (entityType, datasetName) )

    # get the output format
    format = dataset.get("query.output")

    # figure out if query is static
    isStatic = dataset.get("query.static", False)

    # get the group columns list
    group = dataset.get("query.group", [ ])
    group = [ columns.index(key) if key in columns else -1 for key in group ]
    if -1 in group:
        raise DBDatasetConfigurationException(
                  "query.group columns not present in query.columns for [%s/%s]" %
                  (entityType, datasetName) )
    grouping = True if len(group) > 0 else False
    groupSingle = True if len(group) == 1 else False

    # get the key columns list
    keys  = dataset.get("query.key", [ ])
    keys  = [ columns.index(key) if key in columns else -1 for key in keys ]
    if -1 in keys:
        raise DBDatasetConfigurationException(
                  "query.key columns not present in query.columns for [%s/%s]" %
                  (entityType, datasetName) )
    keySingle = True if len(keys) == 1 else False
    keying = True if len(keys) > 0 else False

    # if grouping, group columns must be prefix of key columns
    if grouping and keying:

        # remove the first matching group elements from the key list
        for g in range(len(group)):
            if group[g] == keys[0]:
                keys.pop(0)
                if len(keys) == 0:
                    break
            else:
                break

        # redecide if keySingle
        keySingle = True if len(keys) == 1 else False
        keying = True if len(keys) > 0 else False

    # get the db name and loose type mark
    dbname = dataset.get("database")
    loose  = ecommerce.db.hasLooseTypes(dbname)
    coerce = None if not loose else dataset.get("query.coerce")

    # get a db connection
    conn   = ecommerce.db.getConnection(dbname)
    cursor = conn.cursor()

    # execute the query
    cursor.execute(query)

    # check the result has at least as many columns as we are expecting
    if len(cursor.description) < len(columns):
        raise DBDatasetConfigurationException(
                  "query returned fewer columns than query.columns states for [%s/%s]" %
                  (entityType, datasetName) )

    # start fetching
    result = [ ] if format == "list" else { }
    tRow = cursor.fetchone()
    rowNumber = 0
    while tRow is not None:

        # build the row dictionary
        row = { columns[i] : tRow[i] for i in range(len(columns)) }

        # if loose types and have something to coerce, do so
        if loose and (coerce is not None):
            row = performCoercion(row, coerce)

        # build the keys (key and grouping)
        kKey = None
        gKey = None
        if keying:
            kKey = tRow[keys[0]] if keySingle else tuple( [ tRow[keys[i]] for i in range(len(keys)) ] )
        if grouping:
            gKey = tRow[group[0]] if groupSingle else tuple( [ tRow[group[i]] for i in range(len(group)) ] )

        # if there is some augment, do it
        if augmenting:

            # add each attribute
            for a in augment:
                augmentData = None
                if grouping:
                    augmentData = augment[a][gKey] if gKey in augment[a] else None
                    if augmentData is None and augment[a]["__all__"] is not None:
                        augmentData = augment[a]["__all__"]
                if keying:
                    augmentData = augment[a][kKey] if kKey in augment[a] else None
                    if augmentData is None and augment[a]["__all__"] is not None:
                        augmentData = augment[a]["__all__"]
                row[a] = augmentData

        # add the row to the result
        if format is not None:
            result.append(row)
        else:
            if grouping:
                if gKey not in result:
                    result[gKey] = [ row ] if not keying else { kKey : row }
                else:
                    if not keying:
                        result[gKey].append(row)
                    else:
                        result[gKey][kKey] = row
            else:
                if keying:
                    result[kKey] = row         # set by key
                else:
                    result[rowNumber] = row    # set by row number (an array)

        # fetch next row
        tRow = cursor.fetchone()
        rowNumber += 1

    # close cursor and connection
    cursor.close()
    conn.close()

    # if query is static, return element 0 as "__all__" 
    if isStatic:
       result = { "__all__" : result[0] }

    return result


def solveQuerySQL(dataset, entityType, datasetName, idList):
    """Return a valid SQL sentence

    TODO - support a complex idList (a tuple) and the condition
           for where statements
    """

    # get the sql
    sql = dataset.get("query.sql")

    # get table prefix
    prefix = dataset.get("query.prefix", None)
    prefix = (prefix + ".") if prefix is not None else ""

    # prepare the list of PKs
    queryIds = dataset.get("query.id", [ ])
    pks = { id : " " + prefix + id + " IN (" + \
                     (", ".join([ str(idList[i]) for i in range(len(idList))] ) ) + \
                 ") " for id in queryIds }
    pks["ID:EntityType"] = (" " + prefix + "EntityType = '" + entityType + "' ")

    # build the list of local vars
    vars = dataset.get("query.var", { } )

    # replace macros of the form "{{VARGROUP:VAR}}", # supported groups are:
    #
    # - ID (pks)
    # - VAR (vars)
    # - CONFIG (ecommerce.config)
    #
    (macroBegin, macroEnd) = ("{{", "}}")
    start = sql.find(macroBegin)
    while start != -1:

        # find the termination
        end = sql.find(macroEnd, start)
        if end == -1:       # malformed, but let the sql return an error
            break

        # get the name and separate into group and var
        name = sql[start + 2:end]
        names = name.split(':', 1)
        (group, var) = (names[0], names[1])

        # get the value
        value = ""
        if group == "ID":
            value = pks.get(var, "")
        if group == "VAR":
            value = vars.get(var, "")
        if group == "CONFIG":
            try:
                value = str(ecommerce.config.getConfig().get(var))
            except:
                value = ""

        # do the replacement
        sql = sql.replace( (macroBegin + name + macroEnd), value)

        # find the next
        start = sql.find(macroBegin)

    return sql


def solveCode(dataset, entityType, datasetName, idList):
    """Solve the code definition

    This returns a dictionary where each key is an id from idList and
    the value is the data associated to that key.
    """

    global _code

    # get the code entry
    qualified = dataset.get("code.name")   # cannot be none because we are here!
    parts = qualified.rsplit(".", 1)
    if len(parts) != 2:
        raise DBDatasetRuntimeException(
              "Invalid qualified function name [%s]" % qualified)

    # get the parts
    (module, function) = (parts[0], parts[1])

    # if module is not in the cache, import it
    if module not in _code:

        # initialize the cache entry
        _code[module] = { "module" : None, "functions" : { } }

        # try the import (ignore exceptions)
        try:
            _code[module]["module"] = importlib.import_module(module)
        except:
            pass
    if _code[module]["module"] is None:
        raise DBDatasetRuntimeException(
              "Module [%s] cannot be imported" % module)

    # if function not in cache, get it
    if function not in _code[module]["functions"]:

        # initialize the entry
        _code[module]["functions"][function] = None

        # try to get the object (ignore exceptions)
        try:
            _code[module]["functions"][function] = getattr(_code[module]["module"], function)
        except:
            pass
    if _code[module]["functions"][function] is None:
        raise DBDatasetRuntimeException(
              "Module [%s] does not have a function [%s]" % (module, function))

    # now, invoke the function
    result = _code[module]["functions"][function](dataset, entityType, datasetName, idList)

    # return the result
    return result


def solverInitialize(config = None):
    """Initialize the solver mechanism

    Accesses the configuration and figures out the global database
    """

    global _defaultDB
    global _code

    # instantiate the appropriate loader
    if config is None:
        config = ecommerce.config.getConfig()

    _defaultDB = config.get("db.dataset.database", ecommerce.db.getDefaultDB())

    # reset the imported library cache
    _code = { }
