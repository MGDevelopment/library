"""Cache query handling for the Cache module for TMK (current site)

This module just creates an sqlite3 database and imports
the contents of some directories on different tables.

It also has methods to query the contents of the tables and
a method to re-create the cache. This method can be called
by the content generator every now and then to keep the cache
up to date

by Jose Luis Campanello
"""

import types
import math

import ecommerce.db

import cacheconf

####################################################

def ensureInt(id):

    # if an int => just that
    if isinstance(id, types.IntType):
        return id

    # if a float => math.trunc
    if isinstance(id, types.FloatType):
        return math.trunc(id)

    # go to string and to int
    try:
        return int(str(id))
    except:
        return -1

####################################################

def queryDB(tableName, fieldName, id):
    """Do the actual query"""

    # do the query
    cursor = cacheconf._connection.cursor()
    cursor.execute(
            "SELECT %s, FSFileName FROM %s WHERE %s = ?" % (fieldName, tableName, fieldName),
            (id, ) )
    result = cursor.fetchall()
    cursor.close()

    # change empty list to None
    if result is not None and len(result) == 0:
        result = None

    return result

####################################################

def findBiography(id):
    """Figure out if an Id_Autor has a biography and the file name"""

    # ensure the id is an int
    id = ensureInt(id)

    # query the database
    result = queryDB(cacheconf._database["table.biography"], "Id_Autor", id)

    # return None or a file name
    return None if result is None else result[0][1]


####################################################

def findFirstChapter(id):
    """Figure out if an Id_Articulo has a first chapter and the file name"""

    # ensure the id is an int
    id = ensureInt(id)

    # query the database
    result = queryDB(cacheconf._database["table.firstChapter"], "Id_Articulo", id)

    # return None or a file name
    return None if result is None else result[0][1]

####################################################

def findInterview(id):
    """Figure out if an Id_Articulo has an interview and the file name"""

    # ensure the id is an int
    id = ensureInt(id)

    # query the database
    result = queryDB(cacheconf._database["table.interview"], "Id_Articulo", id)

    # return None or a file name
    return None if result is None else result[0][1]

####################################################

def findImages(id):
    """Figure out if an Id_Articulo has images and return the list"""

    # ensure the id is an int
    id = ensureInt(id)

    # query the database
    result = queryDB(cacheconf._database["table.image"], "Id_Articulo", id)

    # return None or a file name
    return None if result is None else [ image[1] for image in result ]
