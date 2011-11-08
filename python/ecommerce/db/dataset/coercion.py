"""Dataset module for eCommerce package

This file implements the type coercion for the module.

Coercion works in two modes: 1) bulk by type and 2) by column.

Bulk mode indicates the type as an attribute name and then a list
of columns to coerce. Bulk coercion is just best effort. If it fails,
the original value is returned instead. For example:

      boolean: [ "boolColumn1", "boolColumn2" ]
      datetime: [ "datetimeColumn1", "datetimeColumn2" ]

Column mode indicates a column name and, with attributes, the target
type and a coercion submode:

- "best" effort (if the type cannot be coerced, the original value is
  returned). This is the DEFAULT mode
- "ok-or-none" (if the type cannot be coerced, None is returned)
- "ok-or-fail" (if the type cannot be coerced, and exception is raised)

For example:

     boolColumn1:
         type:      boolean
         mode:      ok-or-fail  # ok-or-none or best
     dateColumn1:
         type:      date

The supported data types are:

- bool (1/true/yes goes to True, 0/false/no goes to False)
- boolean (same as bool)
- int
- integer (same as int)
- long
- float
- double (same as float)
- string
- str (same as string)
- date
- datetime (no timezone support)
- time

Reserved column names (derived from bulk mode) are the same as type
names (bool, boolean, int, integer, long, float, double, string, str,
date, datetime, time).

by Jose Luis Campanello
"""

import types
from datetime import date, datetime, time

import ecommerce.config

from exceptions import DBDatasetConfigurationException, DBDatasetRuntimeException
from iso8601 import parseDatetime, parseTime


def _handleMode(value, type, mode):
    """Handle a type conversion error according to mode."""

    if mode == "ok-or-fail":
        raise DBDatasetRuntimeException(
             "Cannot coerce value [%s] to type [%s]" % (value, type))
    if mode == "ok-or-none" or mode == "ok-or-null":
        return None

    # assume best mode
    return value


def coerceBoolean(value, mode = "best"):
    """Coerce value to boolean according to mode."""

    # convert true values
    if value in [ 1, "true", u"true", "yes", u"yes" ]:
        return True

    # convert false values
    if value in [ 0, "false", u"false", "no", u"no" ]:
        return False

    return _handleMode(value, "boolean", mode)


def coerceInt(value, mode = "best"):
    """Coerce value to int according to mode."""

    # try to convert to int
    try:
        i = int(value)
    except ValueError:
        i = _handleMode(value, "int", mode)

    return i


def coerceLong(value, mode = "best"):
    """Coerce value to long according to mode."""

    # try to convert to long
    try:
        i = long(value)
    except ValueError:
        i = _handleMode(value, "long", mode)

    return i


def coerceFloat(value, mode = "best"):
    """Coerce value to float according to mode."""

    # try to convert to float
    try:
        i = float(value)
    except ValueError:
        i = _handleMode(value, "float", mode)

    return i


def coerceString(value, mode = "best"):
    """Coerce value to string according to mode."""

    return str(value)


def coerceDate(value, mode = "best"):
    """Coerce value to date according to mode."""

    # try parsing the date
    parts = parseDatetime(str(value))
    if parts is None:
        return _handleMode(value, "date", mode)

    # build a date object
    return date(parts.get("year"), parts.get("month"), parts.get("day"))


def coerceDatetime(value, mode = "best"):
    """Coerce value to datetime according to mode."""

    # try parsing the datetime
    parts = parseDatetime(str(value))

    if parts is None:
        return _handleMode(value, "datetime", mode)

    # build a date object
    return datetime(parts["year"], parts["month"], parts["day"],
                    parts["hour"], parts["minute"], parts["second"],
                    parts["fraction"]) #### parts["timezone"]


def coerceTime(value, mode = "best"):
    """Coerce value to time according to mode."""

    # try parsing the time
    parts = parseTime(str(value))
    if parts is None:
        return _handleMode(value, "time", mode)

    # build a date object
    return time(parts["hour"], parts["minute"], parts["second"],
                parts["fraction"]) #### parts["timezone"]


_bulkKeys = {
    "bool"        : coerceBoolean,
    "boolean"     : coerceBoolean,
    "int"         : coerceInt,
    "integer"     : coerceInt,
    "long"        : coerceLong,
    "float"       : coerceFloat,
    "double"      : coerceFloat,
    "string"      : coerceString,
    "str"         : coerceString,
    "date"        : coerceDate,
    "datetime"    : coerceDatetime,
    "time"        : coerceTime
}


def performCoercion(row, coerce):
    """Performs type coercion on a row (dictionary)"""

    # some sanity checks
    if row is None or coerce is None:
        return row

    # iterate each key in coerce param
    for key in coerce:

        # figure out if the key is for bulk mode
        if key in _bulkKeys:

            # force it to be a list
            keys = coerce[key]
            if not isinstance(coerce[key], types.ListType):
                keys = list(coerce[key])

            # iterate the columns
            for col in keys:
                if col in row and row[col] is not None:
                    row[col] = _bulkKeys[key](row[col], "best")
        else:
            # solve for the column
            if key in row and row[key] is not None:
                type = coerce[key].get("type", "string")
                if type not in _bulkKeys: 
                    raise DBDatasetConfigurationException(
                          "Type [%s] is unknown, don't know how to coerce" % type)
                mode = coerce[key].get("mode", "best")
                row[key] = _bulkKeys[type](row[key], mode)

    return row

