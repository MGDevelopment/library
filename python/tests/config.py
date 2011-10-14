import unittest
from ecommerce.config import Config

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def test_config_load(self):
        c = Config(paths=('./tests/files',))  # Just load configuration
        print c
