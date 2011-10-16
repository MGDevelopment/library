from ecommerce.config import Config, getConfig, global_name, local_name
from unittest         import TestCase
from tempfile         import mkdtemp
from shutil           import rmtree
from os               import chmod, remove
from os.path          import join as pjoin
import types

#
# Test configuration files
#
global_conf = '''
---
top_global:  &top_global
  inner_one:   one
  inner_two:   bad
  some-map:
    entry1:    scalar
    entry2:    # list
      - test1
      - test2
'''

local_conf = '''
top:
  <<: *top_global
  inner_two:   two
  inner_three: three
'''

class TestSequenceFunctions(TestCase):

    def load_config(self, paths):
        '''Helper function loads a configuration'''
        Config(paths)

    def setUp(self):
        '''
        Create a temporary directory with sample configuration files
        <tmp_dir>/<global_name>
        <tmp_dir>/<local_name>
        '''
        self.tmp_dir    = mkdtemp()
        self.tmp_global = pjoin(self.tmp_dir, global_name)
        self.tmp_local  = pjoin(self.tmp_dir, local_name)
        open(self.tmp_global, 'w').write(global_conf)
        open(self.tmp_local,  'w').write(local_conf)

    def tearDown(self):
        '''Remove the temporary directory'''
        rmtree(self.tmp_dir)

    def test_config_load(self):
        '''Test loading configuration files'''
        c = Config(paths=(self.tmp_dir,))
        self.assertTrue(c.len() > 0, 'empty configuration')

    def test_config_bad_perms(self):
        chmod(self.tmp_global, 0111) # Change to execute only
        self.assertRaises(IOError, self.load_config, (self.tmp_dir,))

    def test_config_missing(self):
        remove(self.tmp_global)
        self.assertRaises(IOError, self.load_config, (self.tmp_dir,))

    def test_get_top(self):
        """Test access to top level entry"""
        self.assertEqual(getConfig().get("top").get("inner_one"), "one",
                         "get('top') didn't get 'inner_one'")

    def test_get_top_somemap(self):
        """Test access to sub-entry"""
        self.assertEqual(getConfig().get("top.some-map").get("entry1"), "scalar",
                         "get('top.some-map') didn't get 'scalar'")

    def test_get_top_somemap_entry2(self):
        """Test access to sub-sub-entry"""
        self.assertIsInstance(getConfig().get("top.some-map.entry2"), types.ListType,
                              "get('top.some-map.entry2') is not a list")

    def test_get_top_somemap_entry2E1(self):
        """Test access to sub-entry"""
        self.assertEqual(getConfig().get("top.some-map.entry2[1]"), "test2",
                         "get('top.some-map.entry2[1]') didn't get 'test2'")

    def test_get_top_somemap_entry2E1_accessor(self):
        """Test access to sub-entry"""
        self.assertEqual(getConfig()["top.some-map.entry2[1]"], "test2",
                         "config['top.some-map.entry2[1]'] didn't get 'test2'")

