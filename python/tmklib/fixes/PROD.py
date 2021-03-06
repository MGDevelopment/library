"""PROD (product - articulo) fixup functions for TMK Library

by Jose Luis Campanello
"""

import os.path

import ecommerce.config

import tmklib.support
import tmklib.cache


########################################################

def title(row):
    """Capitalize the title"""

    # keep the original title
    row["_Title"] = row["Title"]

    # capitalize the title
    if "Title" in row:
        row["Title"] = tmklib.support.capitalize(row["Title"])
    else:
        row["Title"] = None

    return row

########################################################

def checkImage(imagelist, base, template, variables):
    """Try to find an image file that responds to macro expansion"""

    # try expanding each variable
    for v in variables:
        template = template.replace("{{" + v + "}}", str(variables[v]))

    # if template is in imagelist => we got it
    return "/" + template if template in imagelist else None


def checkImageFile(base, template, variables):
    """Try to find an image file that responds to macro expansion"""

    # try expanding each variable
    for v in variables:
        template = template.replace("{{" + v + "}}", str(variables[v]))

    # join the file names
    fname = os.path.join(base, template)

    # return the file only if check if the file exists and is not empty
    return ("/" + template) if os.path.isfile(fname) and os.path.getsize(fname) > 0 else None


def calcImages(row, entityIdVar = "EntityId"):
    """Figure out if an Article has images and what the paths are

    Requires attributes:
    EntityId - the Product Id (same as Id_Articulo, PK on Articulos)
    Categoria_Seccion - from Articulos

    Up to four attributes are appended:
    SmallCover - the path to the small cover
    SmallCoverGeneric - a boolean indicating that the SmallCover is a generic
    LargeCover - if exists, the path to the large cover
    """

    # get some config values (be sure to make copies)
    config   = ecommerce.config.getConfig()
    basePath = config.get("paths.resources")
    small    = config.get("paths.cover.small", [ ])[:] # shallow copy
    smallDef = config.get("paths.cover.small-def")
    large    = config.get("paths.cover.large", [ ])[:] # shallow copy

    # figure out the variables we want to pass
    variables = {
        "EntityId"              : row.get(entityIdVar),
        "Categoria_Seccion"     : row.get("Categoria_Seccion")
    }

    # query the cache to find the images
    imagelist = tmklib.cache.findImages(variables["EntityId"])
    if imagelist is None:
        imagelist = [ ]

    # try to find the small image
    row["CoverSmall"] = None
    row["CoverSmallGeneric"] = True
    for i in range(len(small)):
        path = checkImage(imagelist, basePath, small[i], variables)
        if path is not None:
            row["CoverSmall"] = path
            row["CoverSmallGeneric"] = False
            break
    # still no image? => check for a default
    if row["CoverSmall"] is None and smallDef is not None:
        path = checkImageFile(basePath, smallDef, variables)
        if path is not None:
            row["CoverSmall"] = path
            row["CoverSmallGeneric"] = True

    # try to find the large image
    row["CoverLarge"] = None
    for i in range(len(large)):
        path = checkImage(imagelist, basePath, large[i], variables)
        if path is not None:
            row["CoverLarge"] = path
            break

    return row

########################################################

def filterWithoutImage(row):
    """Returns False if the product has a default image.
    
    Use after calcImages in showcases
    """

    # sanity check
    if row is None or "CoverSmallGeneric" not in row:
        return row

    # check the small image is not generic
    return False if row["CoverSmallGeneric"] else row

########################################################

def calcImagesRelated(row):
    """Calculates the images for a related entity"""

    return calcImages(row, "RelatedEntityId")


########################################################

def embedRatings(row):
    """Makes Rating group as direct attributes"""

    # sanity check
    if "Ratings" not in row or row["Ratings"] is None:
        row["Ratings"] = { }

    # get the data item
    ratings = row["Ratings"]

    row["Rating"] = ratings.get("Rating")
    row["CommentCount"] = ratings.get("CommentCount")

    # pass the attributes up (do None for missing attrs)
    for attr in [ "CommentCount", "Rating" ]:
        row[attr] = ratings.get(attr)

    # remove the ratings from the row
    del row["Ratings"]

    return row

########################################################

def content_title(row):
    """Capitalize the content (song) title"""

    # capitalize the title
    if "EffectiveTitle" in row:
        row["EffectiveTitle"] = tmklib.support.capitalize(row["EffectiveTitle"])
    else:
        row["EffectiveTitle"] = None

    return row

########################################################

def tipoArticulo(row):
    """Capitalize the TipoArticulo_desc field"""

    # capitalize the TipoArticulo_desc
    if "TipoArticulo_desc" in row:
        row["TipoArticulo_desc"] = tmklib.support.capitalize(row["TipoArticulo_desc"])
    else:
        row["TipoArticulo_desc"] = None

    return row
