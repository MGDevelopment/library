"""Dataset module for eCommerce package

This file implements iso8601 date/datetime and time parsing. The methods
exported return None if the passed in string is not a valid ISO8601 date
or a hashmap with the following attributes:

    year, month, day, 
    separator, 
    hour, minute, second, fraction, 
    timezone

by Jose Luis Campanello
"""

import re

_iso8601Date_re = r"^"                                                        \
                  r"(?P<year>[0-9]{4})"                                       \
                      r"(-?(?P<month>[0-9]{1,2})"                             \
                          r"(-?(?P<day>[0-9]{1,2})"                           \
                              r"((?P<separator>T| )?"                         \
                                  r"(?P<hour>[0-9]{2})"                       \
                                      r"(:?(?P<minute>[0-9]{2})"              \
                                          r"(:?(?P<second>[0-9]{2})"          \
                                              r"(\.(?P<fraction>[0-9]+))?"    \
                                          r")?"                               \
                                      r")?"                                   \
                                      r"(?P<timezone>"                        \
                                         r"Z|(([-+])([0-9]{2})(:?[0-9]{2})?)" \
                                      r")?"                                   \
                              r")?"                                           \
                          r")?"                                               \
                      r")?"                                                   \
                  r"$"
_iso8601Time_re = r"^"                                        \
                  r"(?P<hour>[0-9]{2})"                       \
                      r"(:?(?P<minute>[0-9]{2})"              \
                          r"(:?(?P<second>[0-9]{2})"          \
                              r"(\.(?P<fraction>[0-9]+))?"    \
                          r")?"                               \
                      r")?"                                   \
                      r"(?P<timezone>"                        \
                         r"Z|(([-+])([0-9]{2})(:?[0-9]{2})?)" \
                      r")?"                                   \
                  r"$"

_iso8601Date = re.compile(_iso8601Date_re)
_iso8601Time = re.compile(_iso8601Time_re)


def _fixDateFields(attrs):
    """Convert date fields to integer values"""

    if "year" in attrs:
        attrs["year"] = int(attrs["year"])
    else:
        attrs["year"] = None
    if "month" in attrs:
        attrs["month"] = int(attrs["month"])
    else:
        attrs["month"] = None
    if "day" in attrs:
        attrs["day"] = int(attrs["day"])
    else:
        attrs["day"] = None
    if "hour" in attrs:
        attrs["hour"] = int(attrs["hour"])
    else:
        attrs["hour"] = None
    if "minute" in attrs:
        attrs["minute"] = int(attrs["minute"])
    else:
        attrs["minute"] = None
    if "second" in attrs:
        attrs["second"] = int(attrs["second"])
    else:
        attrs["second"] = None
    if "fraction" in attrs:
        attrs["fraction"] = int( (attrs["fraction"] + "000000")[:6] )
    else:
        attrs["fraction"] = None
    if "timezone" not in attrs:
        attrs["timezone"] = None
    if "separator" not in attrs:
        attrs["separator"] = None

    return attrs


def _fixTimeFields(attrs):
    """Convert time fields to integer values"""

    if "hour" in attrs:
        attrs["hour"] = int(attrs["hour"])
    else:
        attrs["hour"] = None
    if "minute" in attrs:
        attrs["minute"] = int(attrs["minute"])
    else:
        attrs["minute"] = None
    if "second" in attrs:
        attrs["second"] = int(attrs["second"])
    else:
        attrs["second"] = None
    if "fraction" in attrs:
        attrs["fraction"] = int( (attrs["fraction"] + "000000")[:6] )
    else:
        attrs["fraction"] = None
    if "timezone" not in attrs:
        attrs["timezone"] = None

    return attrs


def parseDatetime(value):
    """Try parsing an ISO 8601 date or datetime string"""

    m = _iso8601Date.match(value)
    return None if m is None else _fixDateFields(m.groupdict())


def parseTime(value):
    """Try parsing an ISO 8601 time string"""

    m = _iso8601Time.match(value)
    return None if m is None else _fixTimeFields(m.groupdict())

