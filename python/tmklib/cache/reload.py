"""Cache reload handling for the Cache module for TMK (current site)

This module just creates an sqlite3 database and imports
the contents of some directories on different tables.

It also has methods to query the contents of the tables and
a method to re-create the cache. This method can be called
by the content generator every now and then to keep the cache
up to date

by Jose Luis Campanello
"""

import os
import os.path
import re

import ecommerce.db

import cacheconf

####################################################

def _genericReload(tableName, fieldNames, tableDDL, dirname, _pattern, prefix = ""):
    """Generic reload of a cache table"""

    # sanity checks
    if dirname is None:
        raise Exception("No directory to populate biography cache")
    if tableName is None:
        raise Exception("No table to populate")

    # handy connection
    conn = cacheconf._connection

    # recreate the table (if ddl passed)
    if tableDDL is not None:

        # first drop the table (if exists)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS %s" % tableName)
        conn.commit()
        cursor.close()

        # create the table
        cursor = conn.cursor()
        cursor.execute(tableDDL % tableName)
        conn.commit()
        cursor.close()

    # get the directory and pattern
    pattern = re.compile(_pattern)

    # get the directory contents
    files = os.listdir(dirname)
    data = [ ]
    for file in files:
        # file must match the pattern
        m = pattern.search(file)
        if m is None:
            continue

        # get the id
        id = int(m.group(1))

        # add the data
        data.append( (id, prefix + file) )

        # if more than 10000 entries => insert
        if len(data) == 10000:
            # populate the cache
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO %s(%s) VALUES(?, ?)" % (tableName, fieldNames),
                data)
            conn.commit()
            cursor.close()

            # clean data
            data = [ ]

    # if some data remains => insert into cache
    if len(data) > 0:
        # populate the cache
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT INTO %s(%s) VALUES(?, ?)" % (tableName, fieldNames),
            data)
        conn.commit()
        cursor.close()


####################################################

def reloadBiography():
    """Reload the biography cache. Destroys and creates the table"""

    # get some data
    tableName  = cacheconf._database["table.biography"]
    fieldNames = "Id_Autor, FSFileName"
    tableDDL   = """
CREATE TABLE %s (
    Id_Autor            INTEGER NOT NULL,
    FSFileName          VARCHAR(255) NOT NULL,
    PRIMARY KEY (Id_Autor)
)
"""
    dirname = cacheconf._paths["biography"]["path"]
    pattern = re.compile(cacheconf._paths["biography"]["pattern"])

    # do the magic
    _genericReload(tableName, fieldNames, tableDDL, dirname, pattern)


####################################################

def reloadFirstChapter():
    """Reload the first chapter cache. Destroys and creates the table"""

    # get some data
    tableName  = cacheconf._database["table.firstChapter"]
    fieldNames = "Id_Articulo, FSFileName"
    tableDDL   = """
CREATE TABLE %s (
    Id_Articulo         INTEGER NOT NULL,
    FSFileName          VARCHAR(255) NOT NULL,
    PRIMARY KEY (Id_Articulo)
)
"""
    dirname = cacheconf._paths["firstChapter"]["path"]
    pattern = re.compile(cacheconf._paths["firstChapter"]["pattern"])

    # do the magic
    _genericReload(tableName, fieldNames, tableDDL, dirname, pattern)


####################################################

def reloadInterview():
    """Reload the interview cache. Destroys and creates the table"""

    # get some data
    tableName  = cacheconf._database["table.interview"]
    fieldNames = "Id_Articulo, FSFileName"
    tableDDL   = """
CREATE TABLE %s (
    Id_Articulo         INTEGER NOT NULL,
    FSFileName          VARCHAR(255) NOT NULL,
    PRIMARY KEY (Id_Articulo)
)
"""
    dirname = cacheconf._paths["interviews"]["path"]
    pattern = re.compile(cacheconf._paths["interviews"]["pattern"])

    # do the magic
    _genericReload(tableName, fieldNames, tableDDL, dirname, pattern)


####################################################

def reloadImageSmall():
    """Reload the small image cache. Destroys and creates the table"""

    # get some data
    tableName  = cacheconf._database["table.image"]
    fieldNames = "Id_Articulo, FSFileName"
    tableDDL   = """
CREATE TABLE %s (
    Id_Articulo         INTEGER NOT NULL,
    FSFileName          VARCHAR(255) NOT NULL,
    PRIMARY KEY (Id_Articulo, FSFileName)
)
"""
    dirname = cacheconf._paths["image.small"]["path"]
    pattern = re.compile(cacheconf._paths["image.small"]["pattern"])
    prefix  = cacheconf._database["prefix.image.small"]

    # do the magic
    _genericReload(tableName, fieldNames, tableDDL, dirname, pattern, prefix)


####################################################

def reloadImageLarge():
    """Reload the small image cache. Uses an already created table"""

    # get some data
    tableName  = cacheconf._database["table.image"]
    fieldNames = "Id_Articulo, FSFileName"
    dirname = cacheconf._paths["image.large"]["path"]
    pattern = re.compile(cacheconf._paths["image.large"]["pattern"])
    prefix  = cacheconf._database["prefix.image.large"]

    # do the magic
    _genericReload(tableName, fieldNames, None, dirname, pattern, prefix)


####################################################

def reloadImageSite():
    """Reload the site image cache. Uses an already created table"""

    # get some data
    tableName  = cacheconf._database["table.image"]
    fieldNames = "Id_Articulo, FSFileName"
    dirname = cacheconf._paths["image.site"]["path"]
    pattern = re.compile(cacheconf._paths["image.site"]["pattern"])
    prefix  = cacheconf._database["prefix.image.sitio"]

    # do the magic
    _genericReload(tableName, fieldNames, None, dirname, pattern, prefix)


####################################################

def reload():
    """Re-create the cache (destroy tables and create them)"""

    # reload biography
    reloadBiography()

    # reload first chapter
    reloadFirstChapter()

    # reload interview
    reloadInterview()

    # reload images (small, large and site)
    reloadImageSmall()      # must be first!!!!
    reloadImageLarge()
    reloadImageSite()

