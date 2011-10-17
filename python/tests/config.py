from ecommerce.config import Config, getConfig, defaultFolders, defaultFragmentList, ConfigLoaderFileSystem
from unittest         import TestCase
from tempfile         import mkdtemp
from shutil           import rmtree
from os               import chmod, remove
from os.path          import join as os_path_join
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
keychain:
  file:     keychain.yaml
  dirs:
    - <<DIR>>
    - ./config
    - /etc/ecommerce
'''

local_conf = '''
top:
  <<: *top_global
  inner_two:   two
  inner_three: three
'''

keychain_conf = """
#
# keychain file
#
master-key:
    # some hexa value
    value:      44335522661177
    algorithm:  master-key
master-db:
    value:      somekey
    algorithm:
some-other-key:
    # some hexa value
    value:      44335522661177
    algorithm:  3DES-cbc
    key:        master-key
"""

testConfig = { "global" : global_conf, "local" : local_conf }

class TestSequenceFunctions(TestCase):

    def getLoader(self):
        """Return a config loader for the local folder only"""
        return ConfigLoaderFileSystem(self.tmp_dir)


    def getLocalConfig(self):
        """Return a configuration with local folder only"""
        return Config(self.getLoader())


    def load_config(self, loaders):
        '''Helper function loads a configuration'''
        Config(loaders)


    def setUp(self):
        '''Create a temporary directory with sample configuration files'''

        self.tmp_dir    = mkdtemp()
        self.fileNames  = [ ]
        for k in testConfig.keys():
            # create the file name
            fileName = os_path_join(self.tmp_dir, k + ".yaml")

            # append to the list
            self.fileNames.append(fileName)

            # write to the file
            f = open(fileName, 'w')
            f.write(testConfig[k].replace("<<DIR>>", self.tmp_dir))
            f.close()

        # write the keychain
        keychainFile = os_path_join(self.tmp_dir, "keychain.yaml")
        f = open(keychainFile, 'w')
        f.write(keychain_conf)
        f.close()


    def tearDown(self):
        '''Remove the temporary directory'''
        rmtree(self.tmp_dir)


    def test_config_load(self):
        '''Test loading configuration files'''
        c = Config(self.getLoader())
        self.assertTrue(c.len() > 0, 'empty configuration')


    def test_config_bad_perms(self):
        # Change to execute only
        chmod(self.fileNames[0], 0111)
        # execute and check
        self.assertRaises(IOError, self.load_config, self.getLoader())


    def test_config_missing(self):
        # remove the config
        remove(self.fileNames[1])
        self.assertRaises(IOError, self.load_config, self.getLoader())


    def test_get_top(self):
        """Test access to top level entry"""
        self.assertEqual(self.getLocalConfig().get("top").get("inner_one"), "one",
                         "get('top') didn't get 'inner_one'")


    def test_get_top_somemap(self):
        """Test access to sub-entry"""
        self.assertEqual(self.getLocalConfig().get("top.some-map").get("entry1"), "scalar",
                         "get('top.some-map') didn't get 'scalar'")


    def test_get_top_somemap_entry2(self):
        """Test access to sub-sub-entry"""
        self.assertIsInstance(self.getLocalConfig().get("top.some-map.entry2"), types.ListType,
                              "get('top.some-map.entry2') is not a list")


    def test_get_top_somemap_entry2E1(self):
        """Test access to sub-sub-entry list item"""
        self.assertEqual(self.getLocalConfig().get("top.some-map.entry2[1]"), "test2",
                         "get('top.some-map.entry2[1]') didn't get 'test2'")


    def test_get_top_somemap_entry2E1_accessor(self):
        """Test access with brackets"""
        self.assertEqual(self.getLocalConfig()["top.some-map.entry2[1]"], "test2",
                         "config['top.some-map.entry2[1]'] didn't get 'test2'")


    def test_keychain_nonkey(self):
        """Test fetch for a non-key syntax (keychain:{{keyname}})"""
        self.assertEqual(self.getLocalConfig().keychain.fetch("testkey"), "testkey",
                         "failed fetch with non-conformant key")

    def test_keychain_key(self):
        """Test fetch for a key syntax (keychain:{{keyname}})"""
        self.assertEqual(self.getLocalConfig().keychain.fetch("keychain:master-db"), "somekey",
                         "failed fetch with conformant key")

    def test_keychain_keyinvalid(self):
        """Test fetch for a key syntax (keychain:{{keyname}}) that does not exist"""
        self.assertRaises(KeyError, self.getLocalConfig().keychain.fetch, "keychain:dumb-db")

