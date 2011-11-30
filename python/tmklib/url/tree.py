"""Support functions for subject tree

by Jose Luis Campanello
"""

import ecommerce.config
import ecommerce.db

import tmklib.support

_tree  = None
_nodes = None

########################################################

def findNode(seccion, grupo = -1, familia = -1, subfamilia = -1):
    """Find a node and return the information"""

    # load nodes (if needed)
    _loadNodes()

    # build the key
    key = (seccion, grupo, familia, subfamilia)

    # return the node (none if not present)
    return _nodes.get(key)

########################################################

def _loadNodes():
    """Load the tree nodes"""

    global _nodes

    # only if not already loaded
    if _nodes is not None:
        return

    # prepare the dictionary
    nodes = { }
    try:

        # categ_secciones
        nodes = _processQuery(nodes, 0, """
                SELECT          C.Categoria_Seccion             AS Categoria_Seccion,
                                -1                              AS Categoria_Grupo,
                                -1                              AS Categoria_Familia,
                                -1                              AS Categoria_SubFamilia,
                                CASE C.Categoria_Seccion
                                    WHEN 1 THEN         'Libros'
                                    WHEN 3 THEN         'Pasatiempos'
                                    WHEN 4 THEN         'Música'
                                    WHEN 5 THEN         'Películas'
                                END                             AS Nombre,
                                C.Descripcion                   AS Descripcion
                    FROM        Categ_Secciones C
                    WHERE       C.Categoria_Seccion IN (1, 3, 4, 5)
                    ORDER BY    C.Categoria_Seccion
                """)

        # categ_grupos
        nodes = _processQuery(nodes, 1, """
                SELECT          C.Categoria_Seccion             AS Categoria_Seccion,
                                C.Categoria_Grupo               AS Categoria_Grupo,
                                -1                              AS Categoria_Familia,
                                -1                              AS Categoria_Subfamilia,
                                C.Descripcion                   AS Nombre,
                                C.Descripcion                   AS Descripcion
                    FROM        Categ_Grupos C
                    WHERE       C.Categoria_Seccion IN (1, 3, 4, 5)
                    ORDER BY    C.Categoria_Seccion, C.Categoria_Grupo
                """)

        # categ_familias
        nodes = _processQuery(nodes, 2, """
                SELECT          C.Categoria_Seccion             AS Categoria_Seccion,
                                C.Categoria_Grupo               AS Categoria_Grupo,
                                C.Categoria_Familia             AS Categoria_Familia,
                                -1                              AS Categoria_Subfamilia,
                                C.Descripcion                   AS Nombre,
                                C.Descripcion                   AS Descripcion
                    FROM        Categ_Familias C
                    WHERE       C.Categoria_Seccion IN (1, 3, 4, 5)
                    ORDER BY    C.Categoria_Seccion, C.Categoria_Grupo,
                                C.Categoria_Familia
                """)

        # categ_subfamilias
        nodes = _processQuery(nodes, 3, """
                SELECT          C.Categoria_Seccion             AS Categoria_Seccion,
                                C.Categoria_Grupo               AS Categoria_Grupo,
                                C.Categoria_Familia             AS Categoria_Familia,
                                C.Categoria_Subfamilia          AS Categoria_Subfamilia,
                                C.Descripcion                   AS Nombre,
                                C.Descripcion                   AS Descripcion
                    FROM        Categ_Subfamilias C
                    WHERE       C.Categoria_Seccion IN (1, 3, 4, 5)
                    ORDER BY    C.Categoria_Seccion, C.Categoria_Grupo,
                                C.Categoria_Familia, C.Categoria_Subfamilia
                """)
    except:
        raise

    # everything ok => set the nodes
    _nodes = nodes

########################################################

def _processQuery(nodes, id, query):
    """Process a query and populate nodes dictionary (keys are tuples)"""

    # get connection, execute query and fetch entries
    conn     = ecommerce.db.getConnection()
    encoding = ecommerce.db.hasEncoding()
    cursor   = conn.cursor()
    cursor.execute(query)

    # process entries
    for row in cursor:
        # build the key
        key = (row[0], row[1], row[2], row[3])

        # build the data
        data = {
            "id"                        : key[id],
            "Categoria_Seccion"         : row[0],
            "Categoria_Grupo"           : row[1],
            "Categoria_Familia"         : row[2],
            "Categoria_Subfamilia"      : row[3],
            "Nombre"                    : tmklib.support.decode(tmklib.support.capitalize(row[4]), encoding),
            "Descripcion"               : tmklib.support.decode(row[5], encoding)
        }

        # add to the node list
        nodes[key] = data

    return nodes

