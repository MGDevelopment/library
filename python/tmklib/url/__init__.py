"""URL functions for TMK library

by Jose Luis Campanello
"""

import urllib

import tmklib.support

import tree
import cannonical

########################################################
#
# SUBJects - categorias
#
#
# THE URL SCHEME IS NON-OBVIOUS
#
# Libros:
#
#    home:       /libros/
#    tree:       /catalogo/libros/...
#    product:    /libros/...
#
# Games:
#
#    home:       /juguetes/
#    tree:       /catalogo/pasatiempos/...
#    product:    /pasatiempos/...
#
# Music:
#
#    home:       /musica/
#    tree:       /catalogo/cds/...
#    product:    /cds/...
#
# Movies:
#
#    home:       /peliculas/
#    tree:       /catalogo/dvds/...
#    product:    /dvds/...

_urlBases = {
    "Seccion"    : { 1: "libros/",          3: "juguetes/",
                     4: "musica/",          5: "peliculas/" },
    "Grupo"      : { 1: "catalogo/libros/", 3: "catalogo/pasatiempos/",
                     4: "catalogo/cds/",    5: "catalogo/dvds/" },
    "Familia"    : { 1: "catalogo/libros/", 3: "catalogo/pasatiempos/",
                     4: "catalogo/cds/",    5: "catalogo/dvds/" },
    "Subfamilia" : { 1: "catalogo/libros/", 3: "catalogo/pasatiempos/",
                     4: "catalogo/cds/",    5: "catalogo/dvds/" }
}

def SUBJ(row, rowBack = True):

    # find the nodes
    subtype    = row["Subtype"]
    seccion    = tree.findNode(row["Categoria_Seccion"], -1,
                               -1, -1)
    grupo      = tree.findNode(row["Categoria_Seccion"], row["Categoria_Grupo"],
                               -1, -1)
    familia    = tree.findNode(row["Categoria_Seccion"], row["Categoria_Grupo"],
                               row["Categoria_Familia"], -1)
    subfamilia = tree.findNode(row["Categoria_Seccion"], row["Categoria_Grupo"],
                               row["Categoria_Familia"], row["Categoria_Subfamilia"])

    # prepare an empty URL
    url = "/"

    # FIRST PART - seccion or /catalogo/seccion - all cases
    if subtype in [ "Seccion", "Grupo", "Familia", "Subfamilia" ]:
        if subtype in _urlBases and seccion["id"] in _urlBases[subtype]:
            url += _urlBases[subtype][seccion["id"]]
        else:
            if subtype == "Seccion":
                url += tmklib.support.noDiacritics(seccion["Nombre"]) + "/"
            else:
                url += "catalogo/" + tmklib.support.noDiacritics(seccion["Nombre"]) + "/"

    # SECOND PART - seccion (group and bellow)
    if subtype in [ "Grupo", "Familia", "Subfamilia" ]:
        url += tmklib.support.alphaOnly(
                    tmklib.support.noDiacritics(
                        tmklib.support.capitalize(
                            grupo["Nombre"]))).lower() + \
               "--" + str(grupo["id"]) + "/"

    # THIRD PART - seccion (family and bellow)
    if subtype in [ "Familia", "Subfamilia" ]:
        url += tmklib.support.alphaOnly(
                    tmklib.support.noDiacritics(
                        tmklib.support.capitalize(
                            familia["Nombre"]))).lower() + \
               "--" + str(familia["id"]) + "/"

    # FOURT PART - seccion (subfamily and bellow)
    if subtype in [ "Subfamilia" ]:
        url += tmklib.support.alphaOnly(
                    tmklib.support.noDiacritics(
                        tmklib.support.capitalize(
                            subfamilia["Nombre"]))).lower() + \
               "--" + str(subfamilia["id"]) + "/"

    # FILE EXTENSION (ONLY IF NOT "Seccion")
    if subtype in [ "Grupo", "Familia", "Subfamilia" ]:
        # remove the trailing "/" (if present)
        if url[-1] == "/":
            url = url[:-1]
        
        # append the file extension
        #####url += ".htm"

    # set the url
    row["LinkBase"] = url

    return row if rowBack else url


########################################################
#
# PRODucts - categorias
#

def PROD(row, rowBack = True):

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
                            grupo["Nombre"]))).lower() + \
               "--" + str(grupo["id"]) + "/"

    # THIRD PART - familia (if any)
    if familia is not None and familia["id"] != 0:
        url += tmklib.support.alphaOnly(
                    tmklib.support.noDiacritics(
                        tmklib.support.capitalize(
                            familia["Nombre"]))).lower() + \
               "--" + str(familia["id"]) + "/"

    # FOURTH PART - subfamilia (if any)
    if subfamilia is not None and subfamilia["id"] != 0:
        url += tmklib.support.alphaOnly(
                    tmklib.support.noDiacritics(
                        tmklib.support.capitalize(
                            subfamilia["Nombre"]))).lower() + \
               "--" + str(subfamilia["id"]) + "/"

    # FIFTH PART - title
    url += tmklib.support.alphaOnly(
                tmklib.support.noDiacritics(
                    tmklib.support.capitalize(
                        row.get("Title")))).lower() + \
           "--" + str(row["EntityId"])

    # set the url
    row["LinkBase"] = url

    return row if rowBack else url


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

    # encode the url params
    params = urllib.urlencode( {
        "seccion"           : seccionId,
        "idSeccion"         : seccionId,
        "criterioDeOrden"   : 2,
        "claveDeBusqueda"   : "porIDdeEditorial",
        "texto"             : imprintName,
        "idEditor"          : imprintId
    } )

    # build the url
    linkBase = "/buscador/productos.jsp?" + params

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

    # encode the url params
    params = urllib.urlencode( {
        "seccion"           : seccionId,
        "idSeccion"         : seccionId,
        "criterioDeOrden"   : 2,
        "claveDeBusqueda"   : "porIDdeAutor",
        "texto"             : contributorName,
        "idEditor"          : contributorId
    } )

    # build the url
    linkBase = "/buscador/productos.jsp?" + params

    # set the URL
    row["ContributorURL"] = linkBase

    return row if rowBack else linkBase


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
        "CONT" : CONT
    }
    partials = {
        "SUBJ" : { },
        "PROD" : { },
        "IMPR" : { },
        "CONT" : { }
    }
    for e in range(len(entities)):
        EntityType, EntityId = entities[e][0], entities[e][1]
        if EntityType not in partials:
            # create some bougs entry
            partials[EntityType] = { }
        partials[EntityType][EntityId] = None

    # fetch data (from DB) for each type
    for p in partials:
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

__all__ = [ "SUBJ", "PROD", "CONT", "IMPR", "cannonicals" ]
