"""SUBJ (subject - categoria) fixup functions for TMK Library

by Jose Luis Campanello
"""

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

