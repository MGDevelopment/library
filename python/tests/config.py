import unittest
from ecommerce.config import Config

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def test_config_load(self):
        c = Config(paths=('.',))  # Just load configuration
        print c

if __name__ == '__main__':
    unittest.main()
