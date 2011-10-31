"""Dataset module for eCommerce package

This module declares the exceptions used by the package.

by Jose Luis Campanello
"""

class DBDatasetException(Exception):
    """Generic ecommerce.db.dataset exception"""
    pass

class DBDatasetConfigurationException(DBDatasetException):
    """ecommerce.db.dataset Configuration Exception"""
    pass

class DBDatasetRuntimeException(DBDatasetException):
    """ecommerce.db.dataset Runtime Exception"""
    pass

