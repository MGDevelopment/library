"""DB module for eCommerce package

This module isolates the application from knowing what DB API 2.0 implementation
is being used. Also, the application requests connections to a named "database"
and ignores the details of the connection and the lower level implementation.

Basic module usage is:

    import ecommerce.db

    conn = ecommerce.db.getConnection()        # get default db
    conn = ecommerce.db.getConnection("name")  # get "name" db

Defined modules:

- dataset --- module to fetch sets of related information from the database

TODO:
- implement connection pooling (to avoid tcp/ip reconnect latency)

by Jose Luis Campanello
"""

import ecommerce.config

# imported modules
_modules = { }
_defaultDB = None
_databases = { }

class DBException(Exception):
    """Generic ecommerce.db exception"""
    pass

class DBConfigurationException(DBException):
    """ecommerce.db Configuration Exception"""
    pass

class DBRuntimeException(DBException):
    """ecommerce.db Runtime Exception

    Typicaly when trying to access a db that is not known or
    the module or connect function for that db cannot be imported.
    """
    pass

def getConnection(dbname = None):
    """Return a connection to the named database."""

    # use default db if none passed
    if dbname is None:
        dbname = _defaultDB

    # get the db definition
    if dbname not in _databases:
        raise DBRuntimeException("Unknown database [%s]" % dbname)
    dbDef = _databases[dbname]

    # get the module name and check we know about it
    module = dbDef["module"]
    if module not in _modules:
        raise DBRuntimeException("Unknown module [%s] for database [%s]" % (module, dbname))

    # import the module if needed
    if _modules[module]["module"] is None or _modules[module]["connect"] is None:
        try:
            # import
            _modules[module]["module"] = __import__(module)
            if _modules[module]["module"] is not None:
                # get the "connect" method
                _modules[module]["connect"] = getattr(_modules[module]["module"], "connect")
        except:
            pass    # ignore exceptions
    if _modules[module]["connect"] is None:
        raise DBRuntimeException("Unable to import module [%s] or connect method" % module)

    return _modules[module]["connect"](**dbDef["params"])

def _init(config = None):
    """Initialize the module

    Steps executed:
    1: get the default database
    2: process each module in "db.modules"
    3: process each database in "db.databases" (set default if none)
    """

    # get the configuration
    if config is None:
        config = ecommerce.config.getConfig()

    # 1: get the default database
    defaultDB = config.get("db.default")

    # 2: process each module in "db.modules"
    modules = { }
    try:
        mDef = config.get("db.python")
    except:
        raise DBConfigurationException("Cannot find 'db.python' configuration entry")
    for m in mDef:
        modules[m] = {
            "params"  : mDef[m],
            "module"  : None,
            "connect" : None
        }

    # 3: process each database in "db.databases" (set default if none)
    databases = { }
    try:
        dblist = config.get("db.databases")
    except:
        raise DBConfigurationException("Cannot find 'db.databases' configuration entry")
    for db in dblist:

        # ignore errors
        try:
            # get db conf
            dbconf = config.getMulti("db", db)
            if dbconf is None:     # ignore if not present
                continue

            # get the module
            module = dbconf["python"]

            # prepare the params according to the module
            params = { }
            mDef = modules[module]["params"]
            for key in mDef:
                if key in dbconf:
                    if key == 'password':
                        params[key] = config.keychain.fetch(dbconf[key])
                    else:
                        params[key] = dbconf[key]

            # create the db entry
            databases[db] = {
                "def"      : dbconf,
                "module"   : module,
                "params"   : params
            }

            # if no default, use this one
            if defaultDB is None:
                defaultDB = db
        except:
            raise DBConfigurationException("Configuration error processing 'db.%s'" % db)

    # return the config
    return ( defaultDB, databases, modules )

def initialize(config = None):
    """Initialize the module

    Can use the default configuration or a specified one
    """
    global _defaultDB, _databases, _modules

    # call init
    ( _defaultDB, _databases, _modules ) = _init(config)

# initialize
####initialize()

# public methods
__all__ = [ "getConnection", "dataset" ]
