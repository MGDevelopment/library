
from unittest         import TestCase
from tempfile         import mkdtemp
from shutil           import rmtree
import sqlite3
import datetime

import ecommerce.config
import ecommerce.db
import ecommerce.db.codetables

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
        loosetypes: true                    # column types are not rigid
    codetables:
        database:   test
        codetable:  CodeTables
        fields:
            tableId:            CodeTableId
            tableDomain:        TableDomain
            tableName:          TableName
            flagGrouped:        FlagGrouped
            dataTableSchema:    DataTableSchema
            dataTableName:      DataTableName
            dataTableId:        CodeTableId
            dataTableCode:      DataTableCodeField
            dataTableDesc:      DataTableNameField
keychain:
    file:           "null"
    dirs:
        - /dev
'''

setup_sentences = [
    ########### the main list
    """
    CREATE TABLE CodeTables (
        CodeTableId        integer NOT NULL,
        TableDomain        varchar(128) NOT NULL,
        TableName          varchar(128) NOT NULL,
        FlagGrouped        boolean NOT NULL,
        DataTableName      varchar(128) NOT NULL,
        DataTableSchema    varchar(128) NULL,
        DataTableCodeField varchar(128) NULL,
        DataTableNameField varchar(128) NULL,
        PRIMARY KEY(CodeTableId)
    )
    """,
    ########### the char 2 table
    """
    CREATE TABLE CodeTablesONIX30Char2 (
        CodeTableId    integer NOT NULL,
        CodeValue      char(2) NOT NULL,
        Name           varchar(128) NOT NULL,
        PRIMARY KEY(CodeTableId, CodeValue)
    )
    """,
    ########### Code Tables Definition
    "INSERT INTO CodeTables(CodeTableId, TableDomain, TableName, FlagGrouped, DataTableName, "
                            "DataTableSchema, DataTableCodeField, DataTableNameField) "
           "VALUES(16, 'ONIX', '13', 1, 'CodeTablesONIX30Char2', NULL, NULL, NULL)",
    "INSERT INTO CodeTables(CodeTableId, TableDomain, TableName, FlagGrouped, DataTableName, "
                            "DataTableSchema, DataTableCodeField, DataTableNameField) "
           "VALUES(3, 'User', 'User', 1, 'CodeTablesONIX30Char2', NULL, NULL, NULL)",
    ########### Table ONIX.13 DATA
    "INSERT INTO CodeTablesONIX30Char2(CodeTableId, CodeValue, Name) VALUES(16, '02', 'ISSN')",
    "INSERT INTO CodeTablesONIX30Char2(CodeTableId, CodeValue, Name) "
           "VALUES(16, '03', 'German National Bibliography series ID')",
    "INSERT INTO CodeTablesONIX30Char2(CodeTableId, CodeValue, Name) "
           "VALUES(16, '04', 'German Books in Print series ID')",
    "INSERT INTO CodeTablesONIX30Char2(CodeTableId, CodeValue, Name) VALUES(16, '05', 'Electre series ID')",
    "INSERT INTO CodeTablesONIX30Char2(CodeTableId, CodeValue, Name) VALUES(16, '06', 'DOI')",
    "INSERT INTO CodeTablesONIX30Char2(CodeTableId, CodeValue, Name) VALUES(16, '22', 'URN')",
    ########### Table User.User DATA
    "INSERT INTO CodeTablesONIX30Char2(CodeTableId, CodeValue, Name) VALUES(3, 'A', 'Aprovado')",
    "INSERT INTO CodeTablesONIX30Char2(CodeTableId, CodeValue, Name) VALUES(3, 'R', 'Rechazado')",
    "INSERT INTO CodeTablesONIX30Char2(CodeTableId, CodeValue, Name) VALUES(3, 'P', 'Pendiente')"
]


translate_1 = {
    "field1" : "ONIX.13",
    "field2" : "User.User",
    "field3" : "Invalid.List"
}


data_1 = [
    ################# ENTRY 1
    {
        'id': 123,
        'field1': '21',
        'field2': 'P',
        'field3': 'abc'
    },
    ################# ENTRY 2
    {
        'id': 456,
        'field1': '02',
        'field2': 'R',
        'field3': 'def'
    }
]


result_1 = [
    ################# ENTRY 1
    {
        'id': 123,
        'field1': '21',
        'field1._desc': '21',
        'field1._list': 'ONIX.13',
        'field2': 'P',
        'field2._desc': 'Pendiente',
        'field2._list': 'User.User',
        'field3': 'abc',
        'field3._desc': 'abc',
        'field3._list': 'Invalid.List'
    },
    ################# ENTRY 2
    {
        'id': 456,
        'field1': '02',
        'field1._desc': 'ISSN',
        'field1._list': 'ONIX.13',
        'field2': 'R',
        'field2._desc': 'Rechazado',
        'field2._list': 'User.User',
        'field3': 'def',
        'field3._desc': 'def',
        'field3._list': 'Invalid.List'
    }
]


class TestSequenceFunctions(TestCase):

    def setUp(self):
        """Create a config object with test configuration"""

        # create a temp dir for the db
        self.tmp_dir    = mkdtemp()

        # create the config and initialize the db module
        self.config = ecommerce.config.getConfigFromString(db_conf.replace("<<DIR>>", self.tmp_dir))
        ecommerce.db.initialize(self.config)

        # connect to the database and set the data
        conn = ecommerce.db.getConnection("test")
        conn.isolation_level = None
        for s in setup_sentences:
            # get a cursor and execute
            cursor = conn.cursor()
            cursor.execute(s)

        # initialize the codetables
        ecommerce.db.codetables.initialize(self.config)


    def tearDown(self):
        """Remove the temporary directory and destroy the config object"""
        rmtree(self.tmp_dir)
        self.config = None


    def test_1(self):
        """Test list translation"""

        result = ecommerce.db.codetables.translate(translate_1, data_1)
        self.assertEqual(result, result_1, "Translation returned different data")


