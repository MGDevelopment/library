"""Support functions for subject tree

by Jose Luis Campanello
"""

import ecommerce.config
import ecommerce.db

import tmklib.support

import SUBJ

_tree  = None
_nodes = None

########################################################

def baseTree(seccion):
    """Find the base tree"""

    # return the node (none if not present)
    return _tree.get(seccion, { })

########################################################

def _clone(node):
    """Clone a node without the Children attribute"""

    return {
        "id"                        : node["id"],
        "path"                      : node["path"],
        "Categoria_Seccion"         : node["Categoria_Seccion"],
        "Categoria_Grupo"           : node["Categoria_Grupo"],
        "Categoria_Familia"         : node["Categoria_Familia"],
        "Categoria_Subfamilia"      : node["Categoria_Subfamilia"],
        "Nombre"                    : node["Nombre"],
        "Descripcion"               : node["Descripcion"],
        "level"                     : node["level"],
        "Subtype"                   : node["Subtype"],
        "LinkBase"                  : node["LinkBase"]    
    }


def basePath(seccion, grupo = -1, familia = -1, subfamilia = -1):
    """Return an array with the path from root to passed in node"""

    # prepare the path
    path = [ ]
    path.append(_clone(findNode(seccion)))
    if grupo != -1:
        path.append(_clone(findNode(seccion, grupo)))
        if familia != -1:
            path.append(_clone(findNode(seccion, grupo, familia)))
            if subfamilia != -1:
                path.append(_clone(findNode(seccion, grupo, familia, subfamilia)))

    # return the path
    return path

########################################################

def findNode(seccion, grupo = -1, familia = -1, subfamilia = -1):
    """Find a node and return the information"""

    # build the key
    key = (seccion, grupo, familia, subfamilia)

    # return the node (none if not present)
    return _nodes.get(key)

########################################################

def _loadNodes():
    """Load the tree nodes"""

    global _nodes

    # prepare the dictionary
    nodes = { }
    try:

        # categ_secciones
        nodes = _processQuery(nodes, 0, 0, """
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
                                C.Descripcion                   AS Descripcion,
                                'Seccion'                       AS Subtype
                    FROM        Categ_Secciones C
                    WHERE       C.Categoria_Seccion IN (1, 3, 4, 5)
                    ORDER BY    C.Categoria_Seccion
                """)

        # categ_grupos
        nodes = _processQuery(nodes, 1, 1, """
                SELECT          C.Categoria_Seccion             AS Categoria_Seccion,
                                C.Categoria_Grupo               AS Categoria_Grupo,
                                -1                              AS Categoria_Familia,
                                -1                              AS Categoria_Subfamilia,
                                C.Descripcion                   AS Nombre,
                                C.Descripcion                   AS Descripcion,
                                'Grupo'                         AS Subtype
                    FROM        Categ_Grupos C
                    WHERE       C.Categoria_Seccion IN (1, 3, 4, 5)
                    ORDER BY    C.Categoria_Seccion, C.Categoria_Grupo
                """)

        # categ_familias
        nodes = _processQuery(nodes, 2, 2, """
                SELECT          C.Categoria_Seccion             AS Categoria_Seccion,
                                C.Categoria_Grupo               AS Categoria_Grupo,
                                C.Categoria_Familia             AS Categoria_Familia,
                                -1                              AS Categoria_Subfamilia,
                                C.Descripcion                   AS Nombre,
                                C.Descripcion                   AS Descripcion,
                                'Familia'                       AS Subtype
                    FROM        Categ_Familias C
                    WHERE       C.Categoria_Seccion IN (1, 3, 4, 5)
                    ORDER BY    C.Categoria_Seccion, C.Categoria_Grupo,
                                C.Categoria_Familia
                """)

        # categ_subfamilias
        nodes = _processQuery(nodes, 3, 3, """
                SELECT          C.Categoria_Seccion             AS Categoria_Seccion,
                                C.Categoria_Grupo               AS Categoria_Grupo,
                                C.Categoria_Familia             AS Categoria_Familia,
                                C.Categoria_Subfamilia          AS Categoria_Subfamilia,
                                C.Descripcion                   AS Nombre,
                                C.Descripcion                   AS Descripcion,
                                'Subfamilia'                    AS Subtype
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

def _processQuery(nodes, id, level, query):
    """Process a query and populate nodes dictionary (keys are tuples)"""

    # get connection, execute query and fetch entries
    conn     = ecommerce.db.getConnection()
    encoding = ecommerce.db.hasEncoding()
    cursor   = conn.cursor()
    cursor.execute(query)

    # process entries
    for row in cursor:
        # build the key
        key = (int(row[0]), int(row[1]), int(row[2]), int(row[3]))

        path = ".".join( [ str(key[k]) for k in range(level + 1) ])

        # build the data
        data = {
            "id"                        : int(key[id]),
            "path"                      : path,
            "Categoria_Seccion"         : int(row[0]),
            "Categoria_Grupo"           : int(row[1]),
            "Categoria_Familia"         : int(row[2]),
            "Categoria_Subfamilia"      : int(row[3]),
            "Nombre"                    : tmklib.support.decode(tmklib.support.capitalize(row[4]), encoding),
            "Descripcion"               : tmklib.support.decode(row[5], encoding),
            "level"                     : level,
            "Subtype"                   : row[6],
            "Children"                  : [ ]       # used when building the tree
        }

        # add to the node list
        nodes[key] = data

    return nodes

########################################################

def _buildTree():
    """Given the list of nodes, build the tree of nodes"""

    global _tree

    # get the keys of nodes, sorted
    keys = sorted(_nodes.keys())

    # prepare the tree
    stack   = [ ]
    level   = 0
    root    = { "level" : 0, "id" : -1, "Descripcion" : "fake root node", "Children" : [ ] }
    parent  = root
    current = root["Children"]
    for k in range(len(keys)):

        # get the node
        node = _nodes[keys[k]]

        # if level bigger than previous
        if node["level"] > level:

            # parent to the stack
            stack.append(parent)
            level += 1

            # new parent is last node of current
            parent  = current[len(current) - 1]
            current = parent["Children"]

            # append current node to parent's list
            current.append(node)
            continue

        # if level same than previous
        if node["level"] == level:
            # append to the current
            current.append(node)
            continue

        # if level less than previous (remove from stack)
        if node["level"] < level:

            # keep poping until at the same level
            while len(stack) > 0 and node["level"] < level:

                # current is parent's current
                parent  = stack.pop()
                level   -= 1

            # get the current
            current = parent["Children"]

            # append node to current
            current.append(node)
            continue

        raise RuntimeError("reached code that should be unreachable in tmklib.url.tree._buildTree")
    #
    # the root node contains all the children trees
    #

    # create the final tree
    tree = { root["Children"][i]["id"] : root["Children"][i] for i in range(len(root["Children"])) }

    _tree = tree

########################################################

def _buildURLs():
    """Pass thru every node and build the LinkBase for it"""

    global _nodes

    # calculate the linkbase for each node
    for k in _nodes:
        _nodes[k] = SUBJ.SUBJ(_nodes[k])


def _initialize():
    """Initialize the component"""

    # load nodes (if needed)
    _loadNodes()

    # build urls
    _buildURLs()

    # build tree
    _buildTree()

