"""Codetables module for eCommerce package

This file implements the code table cache.

Upon initialization, the full code table list is loaded.
Then, as translations are required, tables are read.

TODO - support translation languages.

by Jose Luis Campanello
"""

import types

import ecommerce.config
import ecommerce.db

from exceptions import DBCodetablesConfigurationException, DBCodetablesRuntimeException

# the cache
_cache  = None
_config = { }


def codeTableList():
    """List all the cached code tables"""

    # be sure cache is initialized
    _initializeCache()

    return _cache.keys()


def _codeTableLoad(table):
    """Load the set of codes for a code table

    WE EXPECT THE ENTRY FOR table TO EXISTS IN _cache
    """

    # prepare a result
    result = { }

    # get the data
    try:

        # get the data
        data = _cache[table]

        # get some data
        (name, schema)     = (data["tableName"], data["tableSchema"])
        (colCode, colDesc) = (data["tableColumnCode"], data["tableColumnDesc"])
        (colId, id)        = (data["tableColumnId"], data["id"])
        qName              = (schema + "." + name if schema is not None else name)

        # escape the if if needed
        if isinstance(id, types.StringTypes):
            id = "'" + id + "'"

        # build the query
        query = "SELECT %s, %s FROM %s WHERE %s = %s" % (colCode, colDesc, qName, colId, id) \
                if data["grouped"] else                                                      \
                "SELECT %s, %s FROM %s" % (colCode, colDesc, qName)

        # get the data from the database
        conn = ecommerce.db.getConnection(_config["dbName"])
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        while row is not None:

            # add the code -> desc info to the result
            result[row[0]] = row[1]

            # get the next row
            row = cursor.fetchone()
    except:
        raise
        pass     # ignore exceptions, NEVER FAIL!!!

    # we never fail...
    return result


def codeTableFind(table, language = None):
    """Find the entry for a code table"""

    global _cache

    # be sure cache is initialized
    _initializeCache()

    # sanity checks
    if table is None:
        raise DBCodetablesRuntimeException("Trying to find [None] table")

    # check if the table is in the cache
    if table not in _cache:

        # get the domain and name
        parts = table.rsplit(".", 1)
        domain = ""
        name   = parts[0]
        if len(parts) > 1:
            domain = parts[0]
            name   = parts[1]

        # create a synthetic entry
        _cache[table] = {
            "id"              : -1,
            "domain"          : domain,
            "name"            : name,
            "fullname"        : table,
            "grouped"         : False,
            "tableSchema"     : "",
            "tableName"       : "",
            "tableColumnId"   : "",
            "tableColumnCode" : "",
            "tableColumnDesc" : "",
            "defined"         : False,     # True= from database, False= synthetic
            "data"            : { }        # None= not loaded, else loaded
        }

    # if the table is not loaded ("data" is None) => load it
    if _cache[table]["data"] is None:
        _cache[table]["data"] = _codeTableLoad(table)

    # return the translation
    return _cache[table]["data"]


def _loadConfig(config = None):
    """Try to get a viable configuration (use defaults wherever appropriate)"""

    # prepare the results (assume defaults)
    _config = {
        "dbName" :          None,
        "codeTable" :       "CodeTables",
        "tableId" :         "CodeTableId",
        "tableDomain" :     "TableDomain",
        "tableName" :       "TableName ",
        "flagGrouped" :     "FlagGrouped",
        "dataTableSchema" : "DataTableSchema",
        "dataTableName" :   "DataTableName ",
        "dataTableId" :     "CodeTableId",
        "dataTableCode" :   "DataTableCodeField",
        "dataTableDesc" :   "DataTableNameField"
    }

    # if we can find a config, try to get config
    if config is None:
        config = ecommerce.config.getConfig()
    if config is not None:
        # get the config values (using defaults)
        _config["dbName"]          = config.get("codetables.database",
                                                _config["dbName"])
        _config["codeTable"]       = config.get("codetables.codetable",
                                                _config["codeTable"])
        _config["tableId"]         = config.get("codetables.fields.tableId",
                                                _config["tableId"])
        _config["tableDomain"]     = config.get("codetables.fields.tableDomain",
                                                _config["tableDomain"])
        _config["tableName"]       = config.get("codetables.fields.tableName",
                                                _config["tableName"])
        _config["flagGrouped"]     = config.get("codetables.fields.flagGrouped",
                                                _config["flagGrouped"])
        _config["dataTableSchema"] = config.get("codetables.fields.dataTableSchema",
                                                _config["dataTableSchema"])
        _config["dataTableName"]   = config.get("codetables.fields.dataTableName",
                                                _config["dataTableName"])
        _config["dataTableId"]     = config.get("codetables.fields.dataTableId",
                                                _config["dataTableId"])
        _config["dataTableCode"]   = config.get("codetables.fields.dataTableCode",
                                                _config["dataTableCode"])
        _config["dataTableDesc"]   = config.get("codetables.fields.dataTableDesc",
                                                _config["dataTableDesc"])

    # return the configured elements
    return _config


def _loadCache(_config):
    """Try to initialize a cache with the known lists"""

    # prepare an empty cache
    _cache = { }

    # try getting the lists from the database
    cursor = None
    try:
        conn = ecommerce.db.getConnection(_config["dbName"])
        cursor = conn.cursor()
    except:
        pass
    if cursor is None:
        return _cache
    cursor.execute("SELECT    %s, %s, %s, %s, %s, %s, %s, %s FROM %s" %
                   (_config["tableId"],             # 0
                    _config["tableDomain"],         # 1
                    _config["tableName"],           # 2
                    _config["flagGrouped"],         # 3
                    _config["dataTableSchema"],     # 4
                    _config["dataTableName"],       # 5
                    _config["dataTableCode"],       # 7
                    _config["dataTableDesc"],       # 8
                    _config["codeTable"]) )
    row = cursor.fetchone()
    while row is not None:

        # prepare the data
        data = {
            "id"              : row[0],
            "domain"          : row[1],
            "name"            : row[2],
            "fullname"        : "",
            "grouped"         : False,
            "tableSchema"     : row[4],
            "tableName"       : row[5],
            "tableColumnId"   : _config["dataTableId"],
            "tableColumnCode" : row[6],
            "tableColumnDesc" : row[7],
            "defined"         : True,     # True= from database, False= synthetic
            "data"            : None      # None= not loaded, else loaded
        }
        if row[3] == 1 or row[3] == "true" or row[3] == u"true" or  \
                          row[3] == "yes"  or row[3] == u"yes":
            data["grouped"] = True
        if data["domain"] is None:
            data["domain"] = ""
            data["fullname"] = data["name"]
        else:
            data["fullname"] = data["domain"] + "." + data["name"]

        # autocomplete some fields
        if data["grouped"]:
            if data["tableColumnId"] is None:
                data["tableColumnId"]   = "CodeTableId"
            if data["tableColumnCode"] is None:
                data["tableColumnCode"] = "CodeValue"
            if data["tableColumnDesc"] is None:
                data["tableColumnDesc"] = "Name"

        # add to the cache
        _cache[data["fullname"]] = data

        # fetch next row
        row = cursor.fetchone()

    # return the prepared cache
    return _cache


def _initializeCache():
    """If not already done, try loading the list of tables"""

    global _cache

    # try loading if not defined
    if _cache is None:
        _cache = _loadCache(_config)


def load(config):
    """Load the list of code tables"""

    # get some config
    _config = _loadConfig(config)

    # try initializing the cache
    _cache  = None

    return (_config, _cache)


def initialize(config = None):
    """Initialize the component"""

    global _cache
    global _config

    # try to initialize
    (_config, _cache) = load(config)

