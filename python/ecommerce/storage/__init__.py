#!/usr/bin/env python
'''S3 Content uploader module for ILHSA SA by Alejo Sanchez
'''
from os.path       import dirname, exists, join as os_path_join
from os            import remove, makedirs, sep
from boto          import connect_s3
from boto.s3.key   import Key
from gzip          import GzipFile
import types
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO  import StringIO

import ecommerce.config

content_gzippable = ('text/html', 'text/css', 'application/javascript',
                     'text/plain', 'text/xml')

###############################################################
###############################################################
#
# BaseStorage class
#
class BaseStorage(object):
    """Abstract base storage"""

    def __init__(self):
        self.sep = sep

    def send(self, name, src, headers = None):
        return self.put(name, src, headers)

    def put(self, name, src, headers = None):
        raise NotImplementedError("BaseStorage.put method not implemented")

    def copy(self, dst_name, src_name):
        raise NotImplementedError("BaseStorage.copy method not implemented")

    def get(self, name):
        raise NotImplementedError("BaseStorage.get method not implemented")

    def delete(self, name):
        raise NotImplementedError("BaseStorage.delete method not implemented")


###############################################################
###############################################################
#
# FilesystemStorage class
#
class FilesystemStorage(BaseStorage):
    '''Filesystem content uploader

    Do not use os.path.join as it does weird things on windows (always
    has to be noticed). Use manual string joins, using self.sep (initialized
    to os.sep).

    params:
        directory:             destination directory (key prefix)
    '''
    def __init__(self, directory):

        BaseStorage.__init__(self)

        if  not isinstance(directory, types.StringTypes) or \
            directory == '' or directory is None:
            raise IOError('directory path required')

        # JLUIS - if path is relative, let it be relative
        #if directory[0] is not '/':
        #    directory  = '/' + directory # prepend

        # test if directory is OK
        if not exists(directory):
            raise IOError('invalid storage directory')

        self._directory  = directory


    def put(self, name, src, headers = None):
        '''Store an object on the filesystem
            params
                name:    name for the destination object
                src:     generator of object data
                headers: (ignored)
        '''

        if name[0] == self.sep:
            name = name[len(self.sep):] # Strip leading slash
        tname = self._directory + self.sep + name
        tdir = dirname(tname)
        if not exists(tdir):
            makedirs(tdir)
        f = open(tname, 'w')
        f.write(src)
        f.close()

        open(self._directory + self.sep + name, 'w').write(src)

    def copy(self, dst_name, src_name):
        '''Copy S3 object to this storage

        params:
            dst_name:   new name (without base directory)
            src_name:   source object (base directory added for this store)
        '''

        dst_name = self._directory + self.sep + dst_name
        src_name = self._directory + self.sep + src_name

        f = open(dst_name, 'w').write(open(src_name, 'r').read())
        f.close()


    def get(self, name):
        '''Read an object from Storage

        params
            name:    name for the object to read
        '''
        return open(self._directory + self.sep + name, "r").read()


    def delete(self, name):
        '''Remove an object from Storage

        params
            name:    name for the object to delete
        '''

        os.remove(self._directory + self.sep + name)



###############################################################
###############################################################
#
# S3Storage class
#
class S3Storage(BaseStorage):
    '''S3 content uploader
    
       params:
           bucket_name:           name of the bucket to upload
           directory:             destination directory (key prefix)
           gzip:                  should uploader gzip content (True)
           cache_type:            Cache-Control header (public,max=age3600)
           AWS_ACCESS_KEY_ID:     AWS key id
           AWS_SECRET_ACCESS_KEY: AWS secret key
    '''
    def __init__(self, bucket_name, directory = None, gzip = True,
           cache_type = 'public,max-age=3600',
           AWS_ACCESS_KEY_ID = None, AWS_SECRET_ACCESS_KEY = None):

        BaseStorage.__init__(self)

        # overide operating system (this is the web)
        self.sep         = "/"

        self._conn       = connect_s3(AWS_ACCESS_KEY_ID,
                                      AWS_SECRET_ACCESS_KEY)
        self._bucket     = self._conn.get_bucket(bucket_name)
        self._gzip       = gzip
        self._cache_type = cache_type
        if directory:
            if directory[0] is self.sep:
                directory = directory[1:] # Remove leading slash for S3
            if directory[-1] is self.sep:
                directory = directory[:-1] # Remove trailing slash for S3
        self._directory  = directory

    def send(self, name, src, headers):
        '''Upload an object to S3
           params
           name:    name for the destination object
           src:     generator of object data
           headers: Content-Type, Content-Encoding, Cache-Control'''

        # Create key
        key     = Key(self._bucket)
        if self._directory:
            key.key = (self.sep).join((self._directory, name))
        else:
            key.key = name

        # Headers
        for header_name, header_value in headers.items():
            key.set_metadata(header_name, header_value)

        # Note: S3 already sets Etag

        fbuf = StringIO()  # Temporary in-memory virtual file
        if headers.get('Content-Encoding', None) == 'gzip' and self._gzip:
            # Compressed
            zf = GzipFile(name, 'wb', 9, fbuf)
            zf.write(src)
            zf.close()
        else:
            # Plain
            fbuf.write(src)

        # Upload
        key.set_contents_from_file(fbuf, policy = 'public-read',
                reduced_redundancy = True)

    def copy(self, dst_name, src_name, src_bucket_name = None):
        '''Copy S3 object to this storage
           dst_name:   new name (without base directory)
           src_name:   source object (base directory added for this store)
           src_bucket: name of source bucket (default this store)
         '''
        if not src_bucket_name:
            src_bucket_name = self._bucket.name
        if self._directory:
            dst_name = (self.sep).join((self._directory, dst_name))
            if src_bucket_name == self._bucket.name:
                src_name = (self.sep).join((self._directory, src_name))
        self._bucket.copy_key(dst_name, src_bucket_name, src_name)

    def get(self, name):
        key = self._bucket.get_key(name)
        ret = key.get_contents_as_string()

        if key.content_encoding == 'gzip':
            fbuf = StringIO(ret)  # Temporary in-memory virtual file
            zf = GzipFile(mode = 'rb', fileobj = fbuf)
            ret = zf.read()
            zf.close()

        return ret


###############################################################
###############################################################
#
# handy functions
#

def _createFilesystemStorage(config, prefix):

    # fetch attributes and create
    dir = config.getMulti(prefix, "path")
    return FilesystemStorage(dir)


def _createS3Storage(config, prefix, name):

    # fetch attributes and create
    bucket     = config.getMulti(prefix, "bucket")
    dir        = config.getMulti(prefix, "dir")
    gzip       = config.getMulti(prefix, "gzip", True)
    cache      = config.getMulti(prefix, "cache", "public,max-age=3600")
    accessKey  = config.getMulti(prefix, "access-key")
    secretKey  = config.getMulti(prefix, "secret-key")

    return S3Storage(bucket, dir, gzip, cache, accessKey, secretKey)


_types = {
    "folder" : _createFilesystemStorage,
    "fsys"   : _createFilesystemStorage,
    "file"   : _createFilesystemStorage,
    "s3"     : _createS3Storage,
    "aws"    : _createS3Storage,
    "amazon" : _createS3Storage
}


def getStorage(config, prefix, name):
    """Get a storage as indicated by configuration"""

    # sanity checks
    if config is None or prefix is None or name is None:
        raise ValueError("ecommerce.storage.getStorage called with None parameter(s)")

    # try to get the type (default is "folder")
    type = config.getMulti(prefix + "." + name, "type", "folder")

    # check is a type we know
    if type not in _types:
        raise ValueError("Storage type [%s] now known" % type)

    # create the storage
    return _types[type](config, prefix + "." + name)


def getStorages(config, prefix):
    """Returns a dictionary of storages"""

    # sanity checks
    if config is None or prefix is None:
        raise ValueError("ecommerce.storage.getStorages called with None parameter(s)")

    # get the list of storages to create
    names = config.get(prefix, { }).keys()

    # prepare the result
    storages = { }
    for name in names:
        storages[name] = getStorage(config, prefix, name)

    return storages

