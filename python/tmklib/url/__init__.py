"""URL functions for TMK library

by Jose Luis Campanello
"""

import urllib

import tmklib.support

from SUBJ import SUBJ
import tree
import cannonical

########################################################
#
# SUBJects - categorias
#

def SUBJ(row, rowBack = True):

    # sanity check
    if row is None:
        return None

    node = tree.findNode(row.get("Categoria_Seccion",    -1),
                         row.get("Categoria_Grupo",      -1),
                         row.get("Categoria_Familia",    -1),
                         row.get("Categoria_Subfamilia", -1))
    linkBase = ""
    if node is not None:
        linkBase = node["LinkBase"]
    else:
        path = [ row.get("Categoria_Seccion",    -1),
                 row.get("Categoria_Grupo",      -1),
                 row.get("Categoria_Familia",    -1),
                 row.get("Categoria_Subfamilia", -1) ]
        path = [ str(p) for p in path if p != -1 ]
        if len(path) == 0:
            path = [ -1 ]
        linkBase = ".".join(path)
    row["LinkBase"] = linkBase

    return row if rowBack else row["LinkBase"]


########################################################
#
# PRODucts - categorias
#

def PROD(row, rowBack = True, entityIdVar = "EntityId"):

    # find the nodes
    seccion    = tree.findNode(row["Categoria_Seccion"], -1,
                               -1, -1)
    grupo      = tree.findNode(row["Categoria_Seccion"], row["Categoria_Grupo"],
                               -1, -1)
    familia    = tree.findNode(row["Categoria_Seccion"], row["Categoria_Grupo"],
                               row["Categoria_Familia"], -1)
    subfamilia = tree.findNode(row["Categoria_Seccion"], row["Categoria_Grupo"],
                               row["Categoria_Familia"], row["Categoria_Subfamilia"])

    # FIRST PART - seccion
    url = "/"
    if seccion["id"] == 1:
        url += "libros/"
    elif seccion["id"] == 3:
        url += "pasatiempos/"
    elif seccion["id"] == 4:
        url += "cds/"
    elif seccion["id"] == 5:
        url += "dvds/"
    else:
        url += tmklib.support.noDiacritics(seccion["Nombre"]) + "/"

    # SECOND PART - grupo (if any)
    if grupo is not None and grupo["id"] != 0:
        url += tmklib.support.alphaOnly(
                    tmklib.support.noDiacritics(
                        tmklib.support.capitalize(
                            grupo["Nombre"]))).strip("_").lower() + \
               "--" + str(grupo["id"]) + "/"

    # THIRD PART - familia (if any)
    if familia is not None and familia["id"] != 0:
        url += tmklib.support.alphaOnly(
                    tmklib.support.noDiacritics(
                        tmklib.support.capitalize(
                            familia["Nombre"]))).strip("_").lower() + \
               "--" + str(familia["id"]) + "/"

    # FOURTH PART - subfamilia (if any)
    if subfamilia is not None and subfamilia["id"] != 0:
        url += tmklib.support.alphaOnly(
                    tmklib.support.noDiacritics(
                        tmklib.support.capitalize(
                            subfamilia["Nombre"]))).strip("_").lower() + \
               "--" + str(subfamilia["id"]) + "/"

    # FIFTH PART - title
    _title = row.get("_Title")
    if not _title:
        _title = row.get("Title")
    url += tmklib.support.smartStrip(
                tmklib.support.alphaOnly(
                    tmklib.support.noDiacritics(
                        tmklib.support.capitalize(
                            _title, False)), True)).lower()

    # check length. NO MORE THAN 230 chars
    #
    # not exact science. Name can have multiple \\ or multiple //
    # depending on what's configured. Give some room for different
    # conditions
    if len(url) > 200:
        url = url[:200]

    # SIXTH PART - the "--<product id>"
    #
    # this is appended later, after we know for sure
    # file name length is not larger than 230 chars
    #
    url += "--" + str(row[entityIdVar])

    # set the url
    row["LinkBase"] = url

    return row if rowBack else url


########################################################
#
# PRODucts related - categorias
#

def PRODRelated(row, rowBack = True):

    return PROD(row, rowBack, "RelatedEntityId")


########################################################
#
# IMPRints - editoriales
#

def IMPR(row, rowBack = True):
    """Creates the URL for the Imprint page"""

    # get some data
    seccionId   = str(row.get("Categoria_Seccion", 1))
    imprintId   = str(row.get("ImprintId", 0))
    imprintName = row.get("ImprintName", "")
    
    optSeleccionada = "Editorial"
    seccionDeBusqueda = "En Libros"
    if seccionId == 1 :
        optSeleccionada = "Editorial"
        seccionDeBusqueda = "En Libros"
    elif seccionId == 4 :
        optSeleccionada = "Sello Discogr%E1fico"
        seccionDeBusqueda = "En Musica"
    elif seccionId == 5 :
        optSeleccionada = "Productora"
        seccionDeBusqueda = "En Peliculas"
    elif seccionId == 3 :
        optSeleccionada = "Editorial"
        seccionDeBusqueda = "En Pasatiempos"
    

    # encode the url params
    params = urllib.urlencode( {
        "seccion"           : seccionId,
        "idSeccion"         : seccionId,
        "criterioDeOrden"   : 2,
        "claveDeBusqueda"   : "porEditorial",
        "texto"             : imprintName,
        "idAutor"           : imprintId,
        "txtencoded"        : imprintName,
        "optSeleccionada"   : optSeleccionada,
        "seccionDeBusqueda" : seccionDeBusqueda,
        "idSeccionPropia"   : seccionId
    } )

    # build the url
    #linkBase = "/buscador/productos.jsp?" + params
    linkBase = "/buscar.do?" + params

    # set the URL
    row["ImprintURL"] = linkBase

    return row if rowBack else linkBase


########################################################
#
# CONTributors - autores
#

def CONT(row, rowBack = True):
    """Creates the URL for the Contributor page"""

    # get some data
    seccionId       = str(row.get("Categoria_Seccion", 1))
    contributorId   = str(row.get("ContributorId", 0))
    contributorName = row.get("ContributorName", "")
    
    optSeleccionada = "Autor"
    seccionDeBusqueda = "En Libros"
    if seccionId == 1 :
        optSeleccionada = "Autor"
        seccionDeBusqueda = "En Libros"
    elif seccionId == 4 :
        optSeleccionada = "Grupo/Int%E9rprete"
        seccionDeBusqueda = "En Musica"
    elif seccionId == 5 :
        optSeleccionada = "Director/Actor"
        seccionDeBusqueda = "En Peliculas"
    elif seccionId == 3 :
        optSeleccionada = "Autor"
        seccionDeBusqueda = "En Pasatiempos"
    

    # encode the url params
    params = urllib.urlencode( {
        "seccion"           : seccionId,
        "idSeccion"         : seccionId,
        "criterioDeOrden"   : 2,
        "claveDeBusqueda"   : "porAutor",
        "texto"             : contributorName,
        "idAutor"           : contributorId,
        "txtencoded"        : contributorName,
        "optSeleccionada"   : optSeleccionada,
        "seccionDeBusqueda" : seccionDeBusqueda,
        "idSeccionPropia"   : seccionId
    } )

    # build the url
    #linkBase = "/buscador/productos.jsp?" + params
    linkBase = "/buscar.do?" + params

    # set the URL
    row["ContributorURL"] = linkBase

    return row if rowBack else linkBase


########################################################
#
# PAGEs - home page
#

def PAGE(row, rowBack = True):
    """Creates the URL for the Home page"""

    linkBase = "/"

    # set the URL
    row["LinkBase"] = linkBase

    return row if rowBack else linkBase


########################################################
#
# treeBranch
#

def treeBranch(seccion):
    """Return a tree given the seccion"""

    return tree.baseTree(seccion)


########################################################
#
# treePath
#

def treePath(seccion, grupo = -1, familia = -1, subfamilia = -1):
    """Return the path of the tree"""

    return tree.basePath(seccion, grupo, familia, subfamilia)


########################################################
#
# cannonicals
#

def cannonicals(entities):
    """Given a list of entities, returns the cannonical URLs.
    
    The entities are passed as 2-uples (or lists) consisting of
    EntityType and EntityId. The function is smart enough to
    calculate by EntityType. This is important because the
    calculation requires going to the DB and fetching data. The
    function does that in an optimal way (just one query by
    EntityType).
    
    The result is a match (by position) on the input.
    """

    # scan the list and separate by entity type
    generator = {
        "SUBJ" : SUBJ,
        "PROD" : PROD,
        "IMPR" : IMPR,
        "CONT" : CONT,
        "PAGE" : PAGE
    }
    partials = {
        "SUBJ" : { },
        "PROD" : { },
        "IMPR" : { },
        "CONT" : { },
        "PAGE" : { }
    }
    for e in range(len(entities)):
        EntityType, EntityId = entities[e][0], entities[e][1]
        if EntityType not in partials:
            # create some bougs entry
            partials[EntityType] = { }
        partials[EntityType][EntityId] = None

    # fetch data (from DB) for each type
    for p in partials:
        if len(partials[p]) > 0:
            partials[p] = cannonical.fetch(p, partials[p])

    # generate all URLs
    for p in partials:
        # if we know how to generate, do so,
        if p in generator:
            gen = generator[p]
            urls = { id : gen(partials[p][id], False) for id in partials[p] }
            partials[p] = urls
        else:
            partials[p] = { id : None for id in partials[p] }

    # build and return the result
    return [ partials[entities[i][0]][entities[i][1]] for i in range(len(entities)) ]

########################################################

__all__ = [ "SUBJ", "PROD", "CONT", "IMPR", "PAGE", "cannonicals",
            "treePath", "treeBranch" ]

tree._initialize()
