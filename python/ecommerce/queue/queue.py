"""Abstract Queue object for the Queue module

by Jose Luis Campanello
"""

import datetime

class Queue(object):
    """Abstract Queue Class
    """

    def __init__(self, config, prefix, producer = True):

        self._config   = config
        self._prefix   = prefix
        self._producer = producer


    def __del__(self):
        pass


    def item(self):
        """Creates a new item for the queue"""
        raise NotImplementedError("item method not implemented")


    def next(self, blocking = False):
        """Returns the next item in the queue"""
        raise NotImplementedError("next method not implemented")


    def lock(self, blocking = False):
        """Lock queue head and return it"""
        raise NotImplementedError("lock method not implemented")


    def isEmpty(self):
        """True if the queue is empty"""
        raise NotImplementedError("isEmpty method not implemented")


    def unlock(self, item):
        """Unlocks item, leaves it as is"""
        raise NotImplementedError("unlock method not implemented")


    def done(self, item):
        """Marks queue item as done (removes from queue)"""
        raise NotImplementedError("done method not implemented")


    def ready(self, item):
        """Marks queue item as ready (put in queue)"""
        raise NotImplementedError("ready method not implemented")


    def error(self, item):
        """Marks queue item as in error (removes from queue)"""
        raise NotImplementedError("error method not implemented")


class QueueItem:
    """Abstract Queue Item Class
    """

    def __init__(self, queue, status = "unknown", id = None, creationDate = None, content = None):

        self._queue        = queue
        self._status       = status
        self._id           = id
        self._creationDate = creationDate
        self._content      = content
        self._locked       = False


    def _getContent(self):
        """Gets the item content"""
        return self._content


    def _setContent(self, content):
        """Sets the item content"""
        self._content = content


    def _getSize(self):
        """Gets the item content size"""
        return 0 if self._content is None else len(self._content)


    def _getLocked(self):
        """True if the item is locked"""
        return self._locked


    def _getId(self):
        """Returns the Id of the item"""
        return self._id


    def _getStatus(self):
        """Returns the Status of the item"""
        return self._status


    def _getCreationDate(self):
        """Returns the Creation Date of the item"""
        return self._creationDate


    id           = property(_getId)
    status       = property(_getStatus)
    creationDate = property(_getCreationDate)
    locked       = property(_getLocked)

    # need overide
    size         = property(_getSize)
    content      = property(_getContent, _setContent)


