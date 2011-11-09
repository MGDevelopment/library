"""Codetables module for eCommerce package

This file implements the translator methods.

TODO - support translation languages.

by Jose Luis Campanello
"""

import cache


def prepare(desc, language = None):
    """Prepare to perform translation

    TODO - support language
    """

    # create the result
    prepared = { }

    # iterate on the description
    for k in desc:
        # get the translation
        trans =  cache.codeTableFind(desc[k], language)

        # build the prepared
        prepared[k] = { "name" : desc[k], "trans" : trans }

    # return the prepared translation
    return prepared


def translate(prepared, data):
    """Perform a PREPARED translation on a single record"""

    # iterate the prepared cols
    for k in prepared:

        # if not present in the data => ignore
        if k not in data:
            continue

        # get some handy data
        name  = prepared[k]["name"]
        trans = prepared[k]["trans"]
        value = data[k]

        # get the value and translate it
        data[k + "._list"] = name
        data[k + "._desc"] = value if value not in trans else trans[value]

    return data


def initialize(config = None):
    """Initialize the component"""

