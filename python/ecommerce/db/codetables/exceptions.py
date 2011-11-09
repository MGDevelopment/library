"""Codetables module for eCommerce package

This module declares the exceptions used by the package.

by Jose Luis Campanello
"""

class DBCodetablesException(Exception):
    """Generic ecommerce.db.codetables exception"""
    pass

class DBCodetablesConfigurationException(DBCodetablesException):
    """ecommerce.db.codetables Configuration Exception"""
    pass

class DBCodetablesRuntimeException(DBCodetablesException):
    """ecommerce.db.codetables Runtime Exception"""
    pass

