from ecommerce.config import Config
import unittest

class TestSequenceFunctions(unittest.TestCase):

    def load_config(self, paths):
        '''Helper function loads a configuration'''
        Config(paths)

    def setUp(self):
        pass

    def test_config_load(self):
        c = Config(paths=('./tests/files',))  # Just load configuration
        self.assertTrue(c.len() > 0, 'empty configuration')

    def test_config_bad_load(self):
        self.assertRaises(IOError, self.load_config, ('/nonexistent',))
