"""Cache module for TMK (current site)

This module just creates an sqlite3 database and imports
the contents of some directories on different tables.

It also has methods to query the contents of the tables and
a method to re-create the cache. This method can be called
by the content generator every now and then to keep the cache
up to date

by Jose Luis Campanello
"""

import ecommerce.config
import ecommerce.db

import cacheconf
from reload import reload
from queries import findBiography, findFirstChapter, findInterview, findImages
import queries


def initialize(config = None):
    """Initialize the cache"""

    # be sure to get a config object
    if config is None:
        config = ecommerce.config.getConfig()

    cacheconf._initialize(config)


initialize()

__all__ = [ "CONT", "IMPR", "PAGE", "PROD", "SUBJ" ]
