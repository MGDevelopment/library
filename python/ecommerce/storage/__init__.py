#!/usr/bin/env python
'''S3 Content uploader module for ILHSA SA by Alejo Sanchez
'''
from os.path       import join as os_path_join
from boto          import connect_s3
from boto.s3.key   import Key
from gzip          import GzipFile
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO  import StringIO

content_gzippable = ('text/html', 'text/css', 'application/javascript',
                     'text/plain', 'text/xml')

class FilesystemStorage(object):
    '''Filesystem content uploader
    
       params:
           directory:             destination directory (key prefix)
    '''
    def __init__(self, directory):
        if directory[0] is '/':
            self._directory  = directory
        else:
            self._directory  = '/' + directory

    def send(self, name, src, type = None):
        '''Store an object on the filesystem
           params
           name:   name for the destination object
           src:    generator of object data
           type:   Content-Type (ignored)'''

        f = open(os_path_join(self._directory, name), 'w')
        f.write(src)

    def copy(self, dst_name, src_name):
        '''Copy S3 object to this storage
           dst_name:   new name (without base directory)
           src_name:   source object (base directory added for this store)
           src_bucket: name of source bucket (default this store)
         '''

        if self._directory:
            dst_name = '/'.join((self._directory, dst_name))
            src_name = '/'.join((self._directory, src_name))

        open(dst_name, 'w').write(open(src_name, 'r').read())


class S3Storage(object):
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
        self._conn       = connect_s3(AWS_ACCESS_KEY_ID,
                                      AWS_SECRET_ACCESS_KEY)
        self._bucket     = self._conn.get_bucket(bucket_name)
        self._gzip       = gzip
        self._cache_type = cache_type
        self._directory  = directory

    def send(self, name, src, type):
        '''Upload an object to S3
           params
           name:   name for the destination object
           src:    generator of object data
           type:   Content-Type'''

        # Create key
        key     = Key(self._bucket)
        if self._directory:
            key.key = '/'.join((self._directory, name))
        else:
            key.key = name

        # Headers
        key.set_metadata('Content-Type', type)
        if self._cache_type:
            key.set_metadata('Cache-Control', self._cache_type)
        # Note: S3 already sets Etag

        fbuf = StringIO()  # Temporary in-memory virtual file
        if self._gzip and type in content_gzippable:
            # Compressed
            zf = GzipFile(name, 'wb', 9, fbuf)
            zf.write(src)
            zf.close()
            key.set_metadata('Content-Encoding', 'gzip')
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
            dst_name = '/'.join((self._directory, dst_name))
            if src_bucket_name == self._bucket.name:
                src_name = '/'.join((self._directory, src_name))
        self._bucket.copy_key(dst_name, src_bucket_name, src_name)

