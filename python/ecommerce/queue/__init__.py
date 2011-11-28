"""Queue module for eCommerce package

This module implements a generic queue that isolates the application from knowing
how the queue is implemented.

The first implementation is a directory queue. Later, other implementations can be
created (for example: using Amazon AWS Queue Services).

The queue is expected to handle jobs that are IDEMPOTENT (meaning that if they are
executed multiple times, no harm is done).

The API is very simple:

- to create a queue, you import this module (import ecommerce.queue) and then invoke
  "ecommerce.queue.queue(config, prefix)", where prefix is the base of the configuration
  options for the queue (for example: prefix can be "content.queue")

- the returned Queue object has many methods to manipulate the queue, for example:

  - item()      - returns a new item (not in the queue)
  - next()      - returns the next item in the queue
  - lock()      - returns the next item in the queue and locks it (if locking is supported)
  - isEmpty()   - True if the queue is empty
  - done(item)  - marks the item as done (removes from the queue)
  - ready(item) - marks the item as ready (puts the item in the queue)
  - error(item) - marks the item as in error (moves the item to the error list)

- the item object supports a few methods:

  - content      - setable property for the item content (set to None for clearing)
  - size         - gets the size of the content for the item
  - locked       - read only property, True if the item is locked (if locking is supported)
  - id           - read only property with the item id
  - creationDate - read only property with the creation date

- the generic configuration options are as follows:

  {{prefix}}.type       - the queue type (possible values: "folder")

- the folder queue specific configuration options are as follows:

  {{prefix}}.folder     - the queue path
  {{prefix}}.rescan     - the number in seconds between rescans (default 5)
  {{prefix}}.keep       - if True, done entries are kept in a separate directory (default False)
  {{prefix}}.errFolder  - the error folder (default "error")
  {{prefix}}.newFolder  - the new item folder (default "new")
  {{prefix}}.doneFolder - the done item folder (default "done")


by Jose Luis Campanello
"""

from qexceptions import *

_queueTypes = { }


def queue(config, prefix, producer = True):
    """Returns a Queue object of the appropriate type"""

    global _queueTypes

    # sanity checks
    if config is None or prefix is None:
        raise QueueRuntimeException("Missing config or prefix attributes")

    # get the queue type
    type = config.getMulti(prefix, "type")
    if type is None:
        raise QueueRuntimeException("No queue type specified")

    # get the module (or import, if necessary)
    if type not in _queueTypes:
        try:
            _queueTypes[type] = __import__("queue_" + type)
        except:
            pass
    if type not in _queueTypes:
        raise QueueRuntimeException("Unknown queue type [%s]" % type)

    # get the module and the create function
    module  = _queueTypes[type]
    try:
        creator = getattr(module, "create", None)
    except:
        raise QueueRuntimeException("Module for Queue type [%s] has no 'create' function" % type)

    # return a new queue object
    return creator(config, prefix, producer)

