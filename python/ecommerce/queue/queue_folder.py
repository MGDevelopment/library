"""Directory based Queue object for the Queue module

by Jose Luis Campanello
"""

import datetime
import time
import uuid
import dircache
import threading
import shutil
import re
import os
import os.path

import zc.lockfile

import ecommerce.config

from qexceptions import *
from queue       import Queue, QueueItem


#####################################################################
#####################################################################
#
# LOCK EXCEPTION
#

class QueueFolderLockException(QueueException):
    """ecommerce.queue Queue Folder Queue Lock Exception
    """
    pass


#####################################################################
#####################################################################
#
# SYNCHRONIZED SEQUENCER
#

class Sequencer(object):

    def __init__(self, initial = 0):
        self._value = initial
        self._lock = threading.Lock()

    def next(self):
        seq = -1
        with self._lock:
            seq = self._value
            self._value += 1
        return seq


#####################################################################
#####################################################################
#
# QUEUE CLASS
#

class QueueFolder(Queue):
    """Folder Queue Class

    Queue items have file names of the form:

        YYYYMMDDhhmmssuuuuuu-aaaaaaaaaaaa-SSSSSSSS.bin

    where (last 2 fields are in hexa):
        - YYYYMMDDhhmmssuuuuuu is the timestamp (u is microseconds)
        - aaaaaaaaaaaa is the hardware mac address (as returned by uuid.getnode())
        - SSSSSSSS is a sequential number in hexadecimal
    """

    def __init__(self, config, prefix, producer = True):

        # base class init
        Queue.__init__(self, config, prefix, producer)

        # get other attributes
        self._folder     = config.getMulti(prefix, "folder")
        self._ext        = "." + config.getMulti(prefix, "extension", "bin")
        self._period     = config.getMulti(prefix, "rescan", 5)
        self._pid        = config.getMulti(prefix, "lockfile", "queue.pid")
        self._keep       = config.getMulti(prefix, "keep", False)
        self._errFolder  = config.getMulti(prefix, "errFolder",  "err")
        self._newFolder  = config.getMulti(prefix, "newFolder",  "new")
        self._doneFolder = config.getMulti(prefix, "doneFolder", "done")
        self._workFolder = config.getMulti(prefix, "workFolder", "work")
        self._errFolder  = self._folder + os.sep + self._errFolder
        self._newFolder  = self._folder + os.sep + self._newFolder
        self._doneFolder = self._folder + os.sep + self._doneFolder
        self._workFolder = self._folder + os.sep + self._workFolder
        self._pattern    = re.compile("[0-9]{20}-[0-9a-fA-F]{12}-[0-9a-fA-F]{8}" + self._ext)

        # only for consumer queue instances, but define for all
        self._seq      = Sequencer(0)
        self._queue    = [ ]

        # check we have a folder
        if self._folder is None:
            raise QueueConfigurationException("Missing folder path for queue [%s]" % prefix)

        # be sure all folders exist
        self._ensureFolder(self._folder)
        if not self._producer:
            self._ensureFolder(self._errFolder)
            self._ensureFolder(self._newFolder)
            self._ensureFolder(self._doneFolder)
            self._ensureFolder(self._workFolder)

        # if a consumer, lock the queue
        if not self._producer:
            # the pid file
            pidfile = self._folder + os.sep + self._pid

            # try locking
            try:
                self._lockFile = zc.lockfile.LockFile(pidfile)
            except zc.lockfile.LockError:
                raise QueueFolderLockException("Cannot lock queue, pid file [%s]" % pidfile)

        # if there are entries in work, move them to ready
        self._undoWork()

        # if not a producer, scan the queue
        if not self._producer:
            self._rescan()


    def __del__(self):

        # if this is a consumer, unlock the queue
        if not self._producer:
            # release the lock
            if self._lockFile is not None:
                self._lockFile.close()

        # base class del
        Queue.__del__(self)


    def list(self):
        """Returns the list of item files in the queue"""

        self._rescan()
        return self._queue


    def item(self):
        """Creates a new item for the queue"""

        return QueueItem(self)


    def next(self, blocking = False):
        """Returns the next item in the queue"""

        # if a producer => error
        if self._producer:
            raise QueueRuntimeException("Queue is not a consumer")

        # rescan
        self._rescan()

        # if blocking and empty, wait until list is not empty
        while blocking and self.isEmpty():
            # wait half a second and rescan
            time.sleep(0.5)
            self._rescan()

        # get the head
        head = self._head()
        if head is None:
            return None

        # load the item
        item = self._load(head, self._folder)

        # move the item to the work
        self._move(item, self._workFolder, self._folder)

        return item


    def lock(self, blocking = False):
        """Lock queue head and return it

        IMPORTANT: No support for locking here, just do next()
        """
        return self.next(blocking)


    def isEmpty(self):
        """True if the queue is empty"""

        # rescan the queue
        self._rescan()
        return self._isEmpty()


    def unlock(self, item):
        """Unlocks item, leaves it as is

        IMPORTANT: No support for locking here, do nothing
        """

        # if a producer => error
        if self._producer:
            raise QueueRuntimeException("Queue is not a consumer")

        return


    def ready(self, item):
        """Marks queue item as ready (put in queue)"""

        # sanity checks
        if item is None:
            raise QueueRuntimeException("Trying to make ready None item")

        # figure out the item id
        item._id = self._makeId()

        # write the item (goes to ready folder then moved to queue)
        self._write(item)

        # change item status
        item._status = "ready"

        # if not a producer => rescan the queue
        if not self._producer:
            self._rescan()

        return item


    def done(self, item):
        """Marks queue item as done (removes from queue)"""

        # sanity checks
        if item is None:
            raise QueueRuntimeException("Trying to mark None item as done")

        # if a producer => error
        if self._producer:
            raise QueueRuntimeException("Queue is not a consumer")

        # delete or move the item
        if self._keep:
            # move to done folder
            self._move(item, self._doneFolder, self._workFolder)
        else:
            # remove the item
            self._delete(item, self._workFolder)

        # change item status
        item._status = "done"

        return item


    def error(self, item):
        """Marks queue item as in error (removes from queue)"""

        # sanity checks
        if item is None:
            raise QueueRuntimeException("Trying to mark None item in error")

        # if a producer => error
        if self._producer:
            raise QueueRuntimeException("Queue is not a consumer")

        # move to error folder
        self._move(item, self._errFolder, self._workFolder)

        # change item status
        item._status = "error"

        return item


    def _head(self):
        """Returns the head of the queue"""
        return None if len(self._queue) == 0 else self._queue[0]


    def _isEmpty(self):
        """True if the queue is empty"""
        return True if len(self._queue) == 0 else False


    def _makeId(self):
        """Create an id for a queue item

            YYYYMMDDhhmmssuuuuuu-aaaaaaaaaaaa-SSSSSSSS.bin

        where (last 2 fields are in hexa):
            - YYYYMMDDhhmmssuuuuuu is the timestamp (u is microseconds)
            - aaaaaaaaaaaa is the hardware mac address (as returned by uuid.getnode())
            - SSSSSSSS is a sequential number in hexadecimal
        """

        # get some data
        now  = datetime.datetime.now()
        node = uuid.getnode()
        seq  = self._seq.next()

        id = "%s-%012x-%08x" % (now.strftime("%Y%m%d%H%M%S%f"), node, seq)

        return id


    def _rescan(self, forced = False):
        """Rescans the queue directory"""

        # get the queue contents
        l = os.listdir(self._folder)

        # reduce the non-valid entries
        #
        # valid entries are: YYYYMMDDhhmmssuuuuuu-aaaaaaaaaaaa-SSSSSSSS.bin
        # where (last 2 fields are in hexa):
        #
        # - YYYYMMDDhhmmssuuuuuu is the timestamp (u is microseconds)
        # - aaaaaaaaaaaa is the hardware mac address (as returned by uuid.getnode())
        # - SSSSSSSS is a sequential number in hexadecimal
        #
        q = sorted( [ item for item in l if self._pattern.match(item) is not None ] )

        # set the new queue list
        self._queue = q


    def _undoWork(self):
        """Move orphan entries in work back to ready"""

        # get the queue contents
        l = os.listdir(self._workFolder)

        # get the queue files
        q = sorted( [ item for item in l if self._pattern.match(item) is not None ] )

        # move to the ready
        for entry in q:

            # load the item
            item = self._load(entry, self._workFolder)

            # move the item
            self._move(item, self._folder, self._workFolder)


    def _load(self, fname, folder):
        """Load an item from a folder"""

        # build the file name
        filename = folder + os.sep + fname

        # get item attributes
        ext          = self._ext
        id           = fname[:-len(ext)] if fname.endswith(ext) else fname
        creationDate = datetime.datetime.fromtimestamp(os.path.getctime(filename))
        content      = open(filename, "r").read()

        # create the item
        return QueueItem(self, "work", id, creationDate, content)


    def _delete(self, item, folder = None):
        """Delete the item"""

        # item has no id => ignore
        if item is None or item.id is None:
            return

        # if no src => use the queue folder
        if folder is None:
            folder = self._newFolder

        # get the file name
        fname = folder + os.sep + item.id + self._ext

        os.remove(fname)


    def _move(self, item, dst, src = None):
        """Move the item file to a subfolder

        Path manipulation is done manualy because of windows removing the
        first part if the folder contains a disk drive letter
        """

        # item has no id => ignore
        if item.id is None:
            return

        # if no src => use the queue folder
        if src is None:
            src = self._folder

        # item is in the queue folder
        srcPath = src + os.sep + item.id + self._ext
        dstPath = dst + os.sep + item.id + self._ext

        # move the file
        shutil.move(srcPath, dstPath)


    def _write(self, item):
        """Write the item to the queue

        The item is first written into the new folder, then moved
        """

        # item has no id => ignore
        if item.id is None:
            return

        # get the file name
        fname = self._newFolder + os.sep + item.id + self._ext

        # write the item content
        fname = self._newFolder + os.sep + item.id + self._ext
        file = open(fname, "w")
        file.write(item.content)
        file.close()

        # move to the destination folder
        self._move(item, self._folder, self._newFolder)


    def _ensureFolder(self, folder):
        """Be sure folders exist"""

        # if the target folder does not exists, create it
        if not os.path.exists(folder):
            # create the folder
            os.makedirs(folder)


#####################################################################
#####################################################################
#
# CREATOR FUNCTION
#

def create(config, prefix, producer):
    """Create a QueueFolder"""

    return QueueFolder(config, prefix, producer)

