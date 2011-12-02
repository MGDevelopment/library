"""SUBJ (subject - categoria) fixup functions for TMK Library

by Jose Luis Campanello
"""

import tmklib.url
import tmklib.support

########################################################

def title(row):
    """Capitalize the title"""

    # capitalize the title
    if "Title" in row:
        row["Title"] = tmklib.support.capitalize(row["Title"])
    else:
        row["Title"] = None

    return row

########################################################

def tree(row):
    """Append the Path and Tree entries"""

    # the tree
    row["Tree"] = tmklib.url.treeBranch(row.get("Categoria_Seccion", -1))

    # the path
    row["Path"] = tmklib.url.treePath(row.get("Categoria_Seccion", -1),
                                      row.get("Categoria_Grupo", -1),
                                      row.get("Categoria_Familia", -1),
                                      row.get("Categoria_Subfamilia", -1))

    return row
