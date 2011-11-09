
from unittest         import TestCase
from tempfile         import mkdtemp
from shutil           import rmtree
import sqlite3
import datetime

import ecommerce.config
import ecommerce.db
import ecommerce.db.dataset

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
    dataset:                                # base definition for dataset module
        loader:     folder                  # folder loading
        database:   test                    # the default database
        paths:      [ "./tests/dataset" ]   # directory where datasets are stored
keychain:
    file:           "null"
    dirs:
        - /dev
'''

setup_sentences = [
    ########### the main product table
    """
    create table Products(
        ProductId        INT NOT NULL,
        Title            VARCHAR(256) NOT NULL,
        Status           CHAR(2) NOT NULL,
        CoerceBool       BOOLEAN NOT NULL,
        CoerceDatetime   TIMESTAMP NOT NULL,
        CoerceFloat      FLOAT NULL,
        List1            CHAR(2) NOT NULL,
        List2            CHAR(2) NULL,
        List3            CHAR(2) NOT NULL,
        PRIMARY KEY (ProductId)
    )
    """,
    ########### the identifiers table
    """
    create table ProductIdentifiers(
        ProductId     INT NOT NULL,
        IDValue       VARCHAR(255) NOT NULL,
        PRIMARY KEY (ProductId, IDValue)
    )
    """,
    ########### the texts table
    """
    create table ProductTexts(
        ProductId     INT NOT NULL,
        TextRole      CHAR(2) NOT NULL,
        TextContent   VARCHAR(255) NOT NULL,
        PRIMARY KEY (ProductId, TextRole)
    )
    """,
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
    "INSERT INTO CodeTablesONIX30Char2(CodeTableId, CodeValue, Name) VALUES(3, 'P', 'Pendiente')",
    ########### Products Data
    "INSERT INTO Products(ProductId, Title, Status, CoerceBool, CoerceDatetime, CoerceFloat, List1, List2, List3) "
           "VALUES(1, 'Title 1', 'OK', 1,       '2011-12-02T16:34:45.453Z', NULL,       '02', 'P',  'abc')",
    "INSERT INTO Products(ProductId, Title, Status, CoerceBool, CoerceDatetime, CoerceFloat, List1, List2, List3) "
           "VALUES(2, 'Title 2', 'ER', 'false', 'sometime',                 9.15,       '01', NULL, 'def')",
    "INSERT INTO Products(ProductId, Title, Status, CoerceBool, CoerceDatetime, CoerceFloat, List1, List2, List3) "
           "VALUES(3, 'Title 3', 'OK', 6.65,    93,                         '-9324.10', '22', NULL, 'ghi')",
    "INSERT INTO Products(ProductId, Title, Status, CoerceBool, CoerceDatetime, CoerceFloat, List1, List2, List3) "
           "VALUES(4, 'Title 4', 'ER', 'false', 'sometime',                 'abc',      '02', 'P',  'jkl')",
    ########### ProductIdentifiers Data
    "INSERT INTO ProductIdentifiers(ProductId, IDValue) VALUES(1, '8050443322')",
    "INSERT INTO ProductIdentifiers(ProductId, IDValue) VALUES(1, '97880504433221')",
    "INSERT INTO ProductIdentifiers(ProductId, IDValue) VALUES(2, '9090443343')",
    "INSERT INTO ProductIdentifiers(ProductId, IDValue) VALUES(3, '97832989052232')",
    ########### ProductTexts Data
    "INSERT INTO ProductTexts(ProductId, TextRole, TextContent) VALUES(1, '01', 'text for 1/01')",
    "INSERT INTO ProductTexts(ProductId, TextRole, TextContent) VALUES(1, '18', 'text for 1/18')",
    "INSERT INTO ProductTexts(ProductId, TextRole, TextContent) VALUES(1, '26', 'text for 1/26')",
    "INSERT INTO ProductTexts(ProductId, TextRole, TextContent) VALUES(2, '01', 'text for 2/01')",
    "INSERT INTO ProductTexts(ProductId, TextRole, TextContent) VALUES(2, '18', 'text for 2/18')",
    "INSERT INTO ProductTexts(ProductId, TextRole, TextContent) VALUES(3, '01', 'text for 3/01')"
]

result_1 = [
    ############# Product 1
    ('PROD', 1, False, {
        'Identifiers': [
            { 'IDValue': u'8050443322',     'ProductId': 1 },
            { 'IDValue': u'97880504433221', 'ProductId': 1 }
        ],
        'ProductId': 1,
        'Status': u'OK',
        'TextsHash': {
            u'01': { 'ProductId': 1, 'TextContent': u'text for 1/01', 'TextRole': u'01' },
            u'18': { 'ProductId': 1, 'TextContent': u'text for 1/18', 'TextRole': u'18' },
            u'26': { 'ProductId': 1, 'TextContent': u'text for 1/26', 'TextRole': u'26' }
        },
        'TextsList': [
            { 'ProductId': 1, 'TextContent': u'text for 1/01', 'TextRole': u'01' },
            { 'ProductId': 1, 'TextContent': u'text for 1/18', 'TextRole': u'18' },
            { 'ProductId': 1, 'TextContent': u'text for 1/26', 'TextRole': u'26' }
        ],
        'Title': u'Title 1'
    } ),
    ############# Product 2
    ('PROD', 2, False, {
        'Identifiers': [
            {'IDValue': u'9090443343', 'ProductId': 2 }
         ],
        'ProductId': 2,
        'Status': u'ER',
        'TextsHash': {
            u'01': { 'ProductId': 2, 'TextContent': u'text for 2/01', 'TextRole': u'01' },
            u'18': { 'ProductId': 2, 'TextContent': u'text for 2/18', 'TextRole': u'18' }
        },
        'TextsList': [
            { 'ProductId': 2, 'TextContent': u'text for 2/01', 'TextRole': u'01' },
            { 'ProductId': 2, 'TextContent': u'text for 2/18', 'TextRole': u'18' }
        ],
        'Title': u'Title 2'
    } ),
    ############# Product 3
    ('PROD', 3, False, {
        'Identifiers': [
            { 'IDValue': u'97832989052232', 'ProductId': 3 }
        ],
        'ProductId': 3,
        'Status': u'OK',
        'TextsHash': {
            u'01': { 'ProductId': 3, 'TextContent': u'text for 3/01', 'TextRole': u'01' }
        },
        'TextsList': [
            {'ProductId': 3, 'TextContent': u'text for 3/01', 'TextRole': u'01' }
        ],
        'Title': u'Title 3'
    } )
]

result_2 = [
    ############# Page 1
    ( 'PAGE', 1, False, {
        'Set1': [
            { 'ProductId': 1,
              'Status': u'OK',
              'Texts': [
                  { 'ProductId': 1, 'TextContent': u'text for 1/01', 'TextRole': u'01' },
                  { 'ProductId': 1, 'TextContent': u'text for 1/18', 'TextRole': u'18' },
                  { 'ProductId': 1, 'TextContent': u'text for 1/26', 'TextRole': u'26' }
              ],
              'Title': u'Title 1'},
            { 'ProductId': 2,
              'Status': u'ER',
              'Texts': None,
              'Texts': [
                  { 'ProductId': 2, 'TextContent': u'text for 2/01', 'TextRole': u'01' },
                  { 'ProductId': 2, 'TextContent': u'text for 2/18', 'TextRole': u'18' }
              ],
              'Title': u'Title 2'}
        ],
        'Set2': [
            { 'ProductId': 2,
              'Status': u'ER',
              'Texts': [
                  { 'ProductId': 2, 'TextContent': u'text for 2/01', 'TextRole': u'01' },
                  { 'ProductId': 2, 'TextContent': u'text for 2/18', 'TextRole': u'18' }
              ],
              'Title': u'Title 2'
            },
            { 'ProductId': 3,
              'Status': u'OK',
              'Texts': [
                  { 'ProductId': 3, 'TextContent': u'text for 3/01', 'TextRole': u'01' }
              ],
              'Title': u'Title 3'
            }
        ]
    } )
]

result_coerce = [
    ############# Product 1
    ( 'PROD', 1, False, {
        'CoerceBool': True,
        'CoerceDatetime': datetime.datetime(2011, 12, 2, 16, 34, 45, 453000),
        'CoerceFloat': None,
        'ProductId': 1,
        'Status': u'OK',
        'Title': u'Title 1'
    } ),
    ############# Product 2
    ( 'PROD', 2, False, {
        'CoerceBool': False,
        'CoerceDatetime': None,
        'CoerceFloat': 9.15,
        'ProductId': 2,
        'Status': u'ER',
        'Title': u'Title 2'
    } ),
    ############# Product 3
    ( 'PROD', 3, False, {
        'CoerceBool': 6.65,
        'CoerceDatetime': None,
        'CoerceFloat': -9324.1,
        'ProductId': 3,
        'Status': u'OK',
        'Title': u'Title 3'
    } ),
    ############# Product 3
    ( 'PROD', 4, False, {
        'CoerceBool': False,
        'CoerceDatetime': None,
        'CoerceFloat': None,
        'ProductId': 4,
        'Status': u'ER',
        'Title': u'Title 4'
    } )
]

result_static = [
    ############# Product 1
    ( 'PROD', 1, False, {
        'ProductId': 1,
        'Status': u'OK',
        'Title': u'Title 1',
        'TotalCount': {
            'Max': 4, 'Min': 1, 'Total': 4
        }
    } ),
    ############# Product 2
    ( 'PROD', 2, False, {
        'ProductId': 2,
        'Status': u'ER',
        'Title': u'Title 2',
        'TotalCount': {
            'Max': 4, 'Min': 1, 'Total': 4
        }
    } ),
    ############# Product 3
    ( 'PROD', 3, False, {
        'ProductId': 3,
        'Status': u'OK',
        'Title': u'Title 3',
        'TotalCount': {
            'Max': 4, 'Min': 1, 'Total': 4
        }
    } ),
    ############# Product 4
    ( 'PROD', 4, False, {
        'ProductId': 4,
        'Status': u'ER',
        'Title': u'Title 4',
        'TotalCount': {
            'Max': 4, 'Min': 1, 'Total': 4
        }
    } )
]


result_code = [
    ############# Product 1
    ( 'PROD', 1, False, {
        'HashValue': 'c4ca4238a0b923820dcc509a6f75849b',
        'ProductId': 1,
        'Status': u'OK',
        'Title': u'Title 1',
        'TotalCount': {
            'Max': 4, 'Min': 1, 'Total': 4
        }
    } ),
    ############# Product 2
    ( 'PROD', 2, False, {
        'HashValue': 'c81e728d9d4c2f636f067f89cc14862c',
        'ProductId': 2,
        'Status': u'ER',
        'Title': u'Title 2',
        'TotalCount': {
            'Max': 4, 'Min': 1, 'Total': 4
        }
    } ),
    ############# Product 3
    ( 'PROD', 3, False, {
        'HashValue': 'eccbc87e4b5ce2fe28308fd9f2a7baf3',
        'ProductId': 3,
        'Status': u'OK',
        'Title': u'Title 3',
        'TotalCount': {
            'Max': 4, 'Min': 1, 'Total': 4
        }
    } ),
    ############# Product 4
    ( 'PROD', 4, False, {
        'HashValue': 'a87ff679a2f3e71d9181a67b7542122c',
        'ProductId': 4,
        'Status': u'ER',
        'Title': u'Title 4',
        'TotalCount': {
            'Max': 4, 'Min': 1, 'Total': 4
        }
    } )
]


result_translate = [
    ############# Product 1
    ( 'PROD', 1, False, {
        'ProductId': 1,
        'Status': u'OK',
        'Title': u'Title 1',
        'List1': u'02',
        'List1._desc': u'ISSN',
        'List1._list': 'ONIX.13',
        'List2': u'P',
        'List2._desc': u'Pendiente',
        'List2._list': 'User.User',
        'List3': u'abc',
        'List3._desc': u'abc',
        'List3._list': 'Invalid.List'
    } ),
    ############# Product 2
    ( 'PROD', 2, False, {
        'ProductId': 2,
        'Status': u'ER',
        'Title': u'Title 2',
        'List1': u'01',
        'List1._desc': u'01',
        'List1._list': 'ONIX.13',
        'List2': None,
        'List2._desc': None,
        'List2._list': 'User.User',
        'List3': u'def',
        'List3._desc': u'def',
        'List3._list': 'Invalid.List'
    } ),
    ############# Product 3
    ( 'PROD', 3, False, {
        'ProductId': 3,
        'Status': u'OK',
        'Title': u'Title 3',
        'List1': u'22',
        'List1._desc': u'URN',
        'List1._list': 'ONIX.13',
        'List2': None,
        'List2._desc': None,
        'List2._list': 'User.User',
        'List3': u'ghi',
        'List3._desc': u'ghi',
        'List3._list': 'Invalid.List'
    } ),
    ############# Product 4
    ( 'PROD', 4, False, {
        'ProductId': 4,
        'Status': u'ER',
        'Title': u'Title 4',
        'List1': u'02',
        'List1._desc': u'ISSN',
        'List1._list': 'ONIX.13',
        'List2': u'P',
        'List2._desc': u'Pendiente',
        'List2._list': 'User.User',
        'List3': u'jkl',
        'List3._desc': u'jkl',
        'List3._list': 'Invalid.List'
    } )
]


class TestSequenceFunctions(TestCase):

    def setUp(self):
        """Create a config object with test configuration"""

        # create a temp dir for the db
        self.tmp_dir    = mkdtemp()

        # create the config and initialize the db module
        self.config = ecommerce.config.getConfigFromString(db_conf.replace("<<DIR>>", self.tmp_dir))
        ecommerce.db.initialize(self.config)
        ecommerce.db.dataset.initialize(self.config)

        # connect to the database and set the data
        conn = ecommerce.db.getConnection("test")
        conn.isolation_level = None
        for s in setup_sentences:
            # get a cursor and execute
            cursor = conn.cursor()
            cursor.execute(s)


    def tearDown(self):
        """Remove the temporary directory and destroy the config object"""
        rmtree(self.tmp_dir)
        self.config = None


    def test_1(self):
        """Test a query with augment"""

        entities = [
            ("PROD", 1, "texts"),
            ("PROD", 2, "texts"),
            ("PROD", 3, "texts")
        ]
        result = ecommerce.db.dataset.fetch(entities)
        self.assertEqual(result, result_1, "Dataset returned different data")


    def test_2(self):
        """Test a dataset with augments only"""

        import pprint
        entities = [
            ("PAGE", 1, "augments")
        ]
        result = ecommerce.db.dataset.fetch(entities)
        self.assertEqual(result, result_2, "Dataset returned different data")

        pass


    def test_coerce(self):
        """Test a query with type coercion"""

        entities = [
            ("PROD", 1, "coerce"),
            ("PROD", 2, "coerce"),
            ("PROD", 3, "coerce"),
            ("PROD", 4, "coerce")
        ]
        result = ecommerce.db.dataset.fetch(entities)
        self.assertEqual(result, result_coerce, "Dataset returned different data")


    def test_static(self):
        """Test a query with static augment"""

        entities = [
            ("PROD", 1, "static"),
            ("PROD", 2, "static"),
            ("PROD", 3, "static"),
            ("PROD", 4, "static")
        ]
        result = ecommerce.db.dataset.fetch(entities)
        self.assertEqual(result, result_static, "Dataset returned different data")


    def test_code(self):
        """Test a query with code augment"""

        entities = [
            ("PROD", 1, "code"),
            ("PROD", 2, "code"),
            ("PROD", 3, "code"),
            ("PROD", 4, "code")
        ]
        result = ecommerce.db.dataset.fetch(entities)
        self.assertEqual(result, result_code, "Dataset returned different data")


    def test_list(self):
        """Test a query with list translation"""

        entities = [
            ("PROD", 1, "list"),
            ("PROD", 2, "list"),
            ("PROD", 3, "list"),
            ("PROD", 4, "list")
        ]
        result = ecommerce.db.dataset.fetch(entities)
        self.assertEqual(result, result_translate, "Dataset returned different data")

