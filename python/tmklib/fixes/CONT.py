"""CONT (contributor - autor) fixup functions for TMK Library

by Jose Luis Campanello
"""

import tmklib.support

########################################################

def title(row):
    """Reformats the Contributor title"""

    # sanity check
    if "ContributorName" not in row:
        return row

    # get the title
    title = row["ContributorName"]

    # if title is prefixed with "[MUS] ", remove
    if title.startswith("[MUS] "):
        title = title[6:]

    # capitalize
    title = tmklib.support.capitalize(title)

    # reset the title
    row["ContributorName"] = title

    return row
