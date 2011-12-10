"""CONT (contributor - autor) fixup functions for TMK Library

by Jose Luis Campanello
"""

import tmklib.support

########################################################

def _reverse(title, sep = ",", joiner = " "):
    """Split a string using sep and reverse the parts
    
    Special case: when two separators exist, split by the
                  first only.
    """

    # split the string
    (part1, part2, part3) = title.partition(sep)

    # rebuild
    title = part3.strip() + joiner + part1.strip()

    return title


def title(row):
    """Reformats the Contributor title

    The logic to properly format the name is as follows:

    - If Descripcion2 IS NOT NULL =>
        - strip leading "[MUS] " if present
        - Descripcion2
    - if begins with "[MUS] "
        - if category in (1) and and has a comma =>
            - strip leading "[MUS] "
            - reverse by comma
        - If category in (1) and and has no comma =>
            - strip leading "[MUS] "
        - If category in (3,4,5) and has a comma =>
            - strip leading "[MUS] "
        - If category in (3,4,5) and has no comma =>
            - strip leading "[MUS] "
            - reverse by space
    - If not begins with "[MUS] " =>
        - If like '%,%,%' =>
            - If has a '-' or a '/' =>
                - split by - or /
                - treat as two names, reverse by ,
            - Else (no '-' or '/') =>
                - reverse splitting by first comma
        - If like '%,%' =>
            - reverse by ','
        - Else (not like '%,%') =>
            - as is
    """

    # sanity check
    if "ContributorName" not in row:
        return row

    # get the title
    title  = row["ContributorName"]
    title2 = None
    if "ContributorName2" in row:
        title2 = row["ContributorName2"]
        del row["ContributorName2"]

    # we hace title2 => special case
    #
    #    - If Descripcion2 IS NOT NULL =>
    #    - strip leading "[MUS] " if present
    #    - Descripcion2
    #
    if title2 is not None:
        # strip the leading "[MUS] " (if present)
        if title2.startswith("[MUS] "):
            title2 = title2[6:]

        # reset the title
        row["ContributorName"] = tmklib.support.capitalize(title2)

        return row

    # begins with "[MUS] "
    #
    #    - if begins with "[MUS] "
    #        - strip leading "[MUS] "
    #        - if category in (1) and and has a comma =>
    #            - reverse by comma
    #        - If category in (1) and and has no comma =>
    #            - return as is
    #        - If category in (3,4,5) and has a comma =>
    #            - return as is
    #        - If category in (3,4,5) and has no comma =>
    #            - reverse by space
    #
    if title.startswith("[MUS] "):
        # strip leading "[MUS] "
        title = title[6:]

        # get the section (default to music)
        seccion = row.get("Categoria_Seccion", 4)

        # if books => handle differently
        if seccion == 1:
            # if comma => reverse
            if title.find(",") != -1:
                title = _reverse(title, ",")
        else:
            # seccion 3, 4 or 5
            if title.find(",") == -1:
                title = _reverse(title, " ")

        # set the title
        row["ContributorName"] = tmklib.support.capitalize(title)

        return row

    # not begins with "[MUS] "
    #
    #    - If not begins with "[MUS] " =>
    #        - If like '%,%,%' =>
    #            - If has a '-' or a '/' =>
    #                - split by - or /
    #                - treat as two names, reverse by ,
    #            - Else (no '-' or '/') =>
    #                - reverse splitting by first comma
    #        - If like '%,%' =>
    #            - reverse by ','
    #        - Else (not like '%,%') =>
    #            - as is
    commas = title.count(",")

    # like "%,%,%"
    if commas > 1:
        (split, pos) = ("-", title.find("-"))
        if pos == -1:
            (split, pos) = ("/", title.find("/"))
        if pos != -1:
            parts = title.partition(split)
            title = _reverse(parts[0].strip()) + " " + split + " " + _reverse(parts[2].strip())
        else:
            title = _reverse(title, ",")
    
    # like "%,%"
    if commas == 1:
        title = _reverse(title, ",")

    # no commas (do nothing)

    # set the title
    row["ContributorName"] = tmklib.support.capitalize(title)

    ###### if title is prefixed with "[MUS] ", remove
    #####if title.startswith("[MUS] "):
    #####    title = title[6:]
    #####
    ###### capitalize
    #####title = tmklib.support.capitalize(title)
    #####
    ###### set the title
    #####row["ContributorName"] = title

    return row
