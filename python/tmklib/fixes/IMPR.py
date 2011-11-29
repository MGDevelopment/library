"""IMPR (imprint - editorial) fixup functions for TMK Library

by Jose Luis Campanello
"""


import tmklib.support

########################################################

def title(row):
    """Reformats the Imprint title"""

    # sanity check
    if "ImprintName" not in row:
        return row

    # get the title
    title = row["ImprintName"]

    # if title is prefixed with "[MUS] ", remove
    if title.startswith("[MUS] "):
        title = title[6:]

    # capitalize
    title = tmklib.support.capitalize(title)

    # reset the title
    row["ImprintName"] = title

    return row
