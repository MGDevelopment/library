"""SUBJ URL functions for TMK library

by Jose Luis Campanello
"""

import urllib

import tmklib.support

import tree

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
                            grupo["Nombre"]))).strip("_").lower() + \
               "--" + str(grupo["id"]) + "/"

    # THIRD PART - seccion (family and bellow)
    if subtype in [ "Familia", "Subfamilia" ]:
        url += tmklib.support.alphaOnly(
                    tmklib.support.noDiacritics(
                        tmklib.support.capitalize(
                            familia["Nombre"]))).strip("_").lower() + \
               "--" + str(familia["id"]) + "/"

    # FOURT PART - seccion (subfamily and bellow)
    if subtype in [ "Subfamilia" ]:
        url += tmklib.support.alphaOnly(
                    tmklib.support.noDiacritics(
                        tmklib.support.capitalize(
                            subfamilia["Nombre"]))).strip("_").lower() + \
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
