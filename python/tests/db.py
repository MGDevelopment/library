import ecommerce.config
import ecommerce.db
import sqlite3
from unittest         import TestCase
from tempfile         import mkdtemp
from shutil           import rmtree

#
# Test configuration files
#
db_conf = '''
---
db:
    python:
        sqlite3:    [ "database" ]
    default:        test
    databases:      [ "test" ]
    test:
        module:     sqlite
        python:     sqlite3
        database:   <<DIR>>/testdb
keychain:
    file:           "null"
    dirs:
        - /dev
'''

class TestSequenceFunctions(TestCase):

    def setUp(self):
        """Create a config object with test configuration"""

        # create a temp dir for the db
        self.tmp_dir    = mkdtemp()

        # create the config and initialize the db module
        self.config = ecommerce.config.getConfigFromString(db_conf.replace("<<DIR>>", self.tmp_dir))
        ecommerce.db.initialize(self.config)


    def tearDown(self):
        """Remove the temporary directory and destroy the config object"""
        rmtree(self.tmp_dir)
        self.config = None


    def test_connect_testdb(self):
        """Test get connection to test db"""
        self.assertIsInstance(ecommerce.db.getConnection("test"), sqlite3.Connection,
                              "ecommerce.db.getConnection('test') is not a list")


    def test_connect_defaultdb(self):
        """Test get connection to default db"""
        self.assertIsInstance(ecommerce.db.getConnection(), sqlite3.Connection,
                              "ecommerce.db.getConnection() is not a list")


    def test_connect_unknown(self):
        """Test get connection to unknown db (should raise)"""
        self.assertRaises(ecommerce.db.DBRuntimeException, ecommerce.db.getConnection, "unknown-db")

