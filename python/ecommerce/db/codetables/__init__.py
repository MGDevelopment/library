"""Codetables module for eCommerce package

This module provides a mechanism to automate "code" to "description" for
data elements. It is common to use "code" fields as a form of enumerated types
and then to store the description associated to each specific code somewhere.

This module handles that conversion by reading the descriptions from the database
(indicated by config value "db.codetables.database") and using a master table of
tables (indicated by config value "db.codetables.codetable"). This master table
of tables contains a list of tables (each table having a domain and a name, for
example: domain "ONIX" list "13", or "ONIX.13" for short).

Each table then has 5 fields that describe where to find the required information.
The fields (indicated by config hashmap "db.codetables.fields") are:

- flagGrouped: if true, the target table schema/name is a single table that
               stores information for multiple tables, so the tableId field is
               part of the primary key
- dataTableSchema/dataTableName: indicate the schema and table name for the
               table
- dataTableCode/dataTableDesc: indicate the code and description fields in the
               target table.

TODO - a flag to indicate that the table has a language translation table.

At initialization, the module reads the list of tables and stores that in a
cache. Then, as each list gets used, the contents of the list are fetched into
cache to speed up future conversions.

The method "translate" of this package performs the translation by receiving
three parameters:

- translation description - a hashmap of "attribute name" -> "list name"
- data - a list of hashmaps o a single hashmap
- language - the target language of the translation. Default None (NOT USED)

The translation (for a given "attribute name", attr for short) creates two
new attributes named after the "attr._list" having the "list name" and
"attr._desc" having the description. If the code (indicated by "attr") does
not have a translation, the same value is repeated in "attr._desc".

If a "list name" is not defined, the translation is performed anyway (by
repeating the list name in the "attr._list" and the "attr" in "attr._desc").

For example, the following input parameters:

- translation description:

    { "field1" : "ONIX.13", "field2" : "eCommerce.status" }

- data:

    [
        { "id" : 123, "field1" : "21", "field2" : "P" },
        { "id" : 456, "field1" : "02", "field2" : "R" }
    ]

Could produce the following result:

    [
        { "id" : 123,
          "field1" : "22", "field1._list" : "ONIX.13", "field1._desc" : "URN",
          "field2" : "P", "field2._list" : "eCommerce.status", "field2._desc" : "Pendiente"
        },
        { "id" : 456,
          "field1" : "02", "field1._list" : "ONIX.13", "field1._desc" : "ISSN",
          "field2" : "R", "field2._list" : "eCommerce.status", "field2._desc" : "Rechazado"
        }
    ]

by Jose Luis Campanello
"""

import types

import ecommerce.config
import ecommerce.db

from exceptions import DBCodetablesConfigurationException, DBCodetablesRuntimeException
import cache
import translator


def translate(desc, data, language = None):
    """Perform translation on data according to desc and language

    Parameters:
    - desc --- hashmap indicating "attribute name" -> "list name"
    - data --- list or hashmap containing data
    - language --- the target language (NOT USED)
    """

    # sanity checks
    if desc is None or data is None:
        return data

    # create a translation configuration
    prepared = translator.prepare(desc, language)

    # perform the translation
    if isinstance(data, types.DictType):
        # translate single entry
        data = translator.translate(prepared, data)
    elif isinstance(data, types.ListType):
        # translate each entry
        for i in range(len(data)):
            data[i] = translator.translate(prepared, data[i])

    # return the translated data
    return data


def list():
    """Get the list of cached code tables"""

    return cache.codeTableList()


def getTranslation(table, language = None):
    """Get the translation data for a table"""

    return cache.codeTableFind(table, language)


def initialize(config = None):
    """Initialize the module with specific or default config"""

    # initialize the cache
    cache.initialize(config)

    # initialize the translator
    translator.initialize(config)


# initialize
initialize()


# public methods
__all__ = [ "translate", "initialize", "list", "getTranslation" ]

