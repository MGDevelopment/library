from ecommerce.storage  import FilesystemStorage
from unittest           import TestCase
from tempfile           import mkdtemp
from shutil             import rmtree
from os                 import chmod, remove
from os.path            import join as os_path_join


page_name = 'test_page.html'
page_data = '<html><body>Test content</body></html>'
page_type = 'text/html'

class TestStorageModule(TestCase):

    def getStorage(self):
        """Return a config loader for the local folder only"""
        return FilesystemStorage(self.tmp_dir)

    def setUp(self):
        '''Create a temporary directory with sample configuration files'''

        self.tmp_dir    = mkdtemp()
        #self.fileNames  = [ ]

    def tearDown(self):
        '''Remove the temporary directory'''
        rmtree(self.tmp_dir)

    def testOpenStorage(self):
        '''Test opening storage object'''
        s = self.getStorage()
        self.assertIsInstance(s, FilesystemStorage)

    def testWriteStorage(self):
        '''Test opening storage object'''
        s = self.getStorage()
        s.send(page_name, page_data, page_type)
        f = open(self.tmp_dir + '/' + page_name)
        self.assertEqual(page_data, f.read())

