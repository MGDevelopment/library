"""Exceptions for the Queue module

by Jose Luis Campanello
"""

class QueueException(Exception):
    """Generic ecommerce.queue exception
    """
    pass


class QueueConfigurationException(QueueException):
    """ecommerce.queue Configuration Exception
    """
    pass


class QueueRuntimeException(QueueException):
    """ecommerce.queue Runtime Exception
    """
    pass

