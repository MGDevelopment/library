"""Config handling for the Cache module for TMK (current site)

This module just creates an sqlite3 database and imports
the contents of some directories on different tables.

It also has methods to query the contents of the tables and
a method to re-create the cache. This method can be called
by the content generator every now and then to keep the cache
up to date

by Jose Luis Campanello
"""

import ecommerce.db

_connection = None
_database = {
    "name"                  : "fscache",
    "prefix.image.small"    : "tapas/chicas/",
    "prefix.image.large"    : "tapas/grandes/",
    "prefix.image.sitio"    : "tapas/sitio/",
    "table.image"           : "tbl_images",
    "table.interview"       : "tbl_interview",
    "table.firstChapter"    : "tbl_firstChapter",
    "table.biography"       : "tbl_biography"
}

_paths      = {
    "image.small"       : {
        "path"          : None,
        "pattern"       : "^(\d+).jpg$"
    }, 
    "image.large"       : {
        "path"          : None,
        "pattern"       : "^l(\d+).jpg$"
    }, 
    "image.site"        : {
        "path"          : None,
        "pattern"       : "^(\d+)[cg]0.jpg$"
    }, 
    "interviews"        : {
        "path"          : None,
        "pattern"       : "^(\d+).txt$"
    }, 
    "firstChapter"      : {
        "path"          : None,
        "pattern"       : "^(\d+).txt$"
    }, 
    "biography"         : {
        "path"          : None,
        "pattern"       : "^(\d+).txt$"
    }
}

def _initialize(config = None):
    """Query the config object and initialize internal data"""

    global _database
    global _paths
    global _connection

    # set some defaults
    _database           = {
        "name"                  : "fscache",
        "prefix.image.small"    : "tapas/chicas/",
        "prefix.image.large"    : "tapas/grandes/",
        "prefix.image.sitio"    : "tapas/sitio/",
        "table.image"           : "tbl_images",
        "table.interview"       : "tbl_interview",
        "table.firstChapter"    : "tbl_firstChapter",
        "table.biography"       : "tbl_biography"
    }

    # sanity check
    if config is None:
        return

    # get db related config
    database = config.get("paths.cache", _database).copy()

    # be sure to have every option with a value
    if "name" not in database:
        database["name"] = "fscache"
    if "prefix.image.small" not in database:
        database["prefix.image.small"] = "tapas/chicas/"
    if "prefix.image.large" not in database:
        database["prefix.image.large"] = "tapas/grandes/"
    if "prefix.image.sitio" not in database:
        database["prefix.image.sitio"] = "tapas/sitio/"
    if "table.image" not in database:
        database["table.image"] = "tbl_images"
    if "table.interview" not in database:
        database["table.interview"] = "tbl_interview"
    if "table.firstChapter" not in database:
        database["table.firstChapter"] = "tbl_firstChapter"
    if "table.biography" not in database:
        database["table.biography"] = "tbl_biography"

    # set the new config
    _database = database

    # get the paths
    _paths["image.small"]["path"]   = config.get("paths.covers-small")
    _paths["image.large"]["path"]   = config.get("paths.covers-large")
    _paths["image.site"]["path"]    = config.get("paths.covers-site")
    _paths["interviews"]["path"]    = config.get("paths.interviews")
    _paths["firstChapter"]["path"]  = config.get("paths.firstChapter")
    _paths["biography"]["path"]     = config.get("paths.biography")

    # get a connection to the database
    _connection = ecommerce.db.getConnection(_database["name"])
