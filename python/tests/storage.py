from ecommerce.storage  import FilesystemStorage, S3Storage
from unittest           import TestCase
from tempfile           import mkdtemp
from shutil             import rmtree
from os                 import chmod, remove
from os.path            import join as os_path_join


bucket_name = 'tmk-a'
page_name   = 'test_page.html'
page_data   = '<html><body>Test content</body></html>'
headers  = {
    'Content-Type':    'text/html',
    'Content-Encoding': 'gzip',
    'Cache-Control': 'max-age=3600, must-revalidate'
}

class TestStorageModule(TestCase):

    def getFilesystemStorage(self):
        """Return a config loader for the local folder only"""
        return FilesystemStorage(self.tmp_dir)

    def getS3Storage(self):
        """Return a config loader for the local folder only"""
        return S3Storage(bucket_name)

    def setUp(self):
        '''Create a temporary directory with sample configuration files'''

        self.tmp_dir    = mkdtemp()
        #self.fileNames  = [ ]

    def tearDown(self):
        '''Remove the temporary directory'''
        rmtree(self.tmp_dir)

    def testOpenFilesystemStorage(self):
        '''Test opening storage object'''
        s = self.getFilesystemStorage()
        self.assertIsInstance(s, FilesystemStorage)

    def testWriteFilesystemStorage(self):
        '''Test opening storage object'''
        s = self.getFilesystemStorage()
        s.send(page_name, page_data, headers)
        #f = open(self.tmp_dir + '/' + page_name)
        self.assertEqual(page_data, s.get(page_name))

    # Disabled S3 test
    def _testOpenS3Storage(self):
        '''Test opening storage object'''
        s = self.getS3Storage()
        self.assertIsInstance(s, S3Storage)

    # Disabled S3 test
    def _testWriteS3Storage(self):
        '''Test opening storage object'''
        s = self.getS3Storage()
        s.send(page_name, page_data, headers)
        self.assertEqual(page_data, s.get(page_name))

