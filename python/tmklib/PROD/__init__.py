"""Product (PROD) dataset related functions

by Jose Luis Campanello
"""

import re
from decimal import Decimal
import os
import os.path
import urllib

import ecommerce.config
import ecommerce.db

import tmklib.support
import tmklib.cache

import tmklib.url.tree

from price import calculateTaxes

###################################################

def categories(row):
    """Returns the categories for the product"""

    cat_seccion     = row["Categoria_Seccion"]
    cat_grupo       = row["Categoria_Grupo"]
    cat_familia     = row["Categoria_Familia"]
    cat_subfamilia  = row["Categoria_Subfamilia"]

    seccion    = tmklib.url.tree.findNode(cat_seccion, -1, -1, -1)
    grupo      = tmklib.url.tree.findNode(cat_seccion, cat_grupo, -1, -1)
    familia    = tmklib.url.tree.findNode(cat_seccion, cat_grupo, cat_familia, -1)
    subfamilia = tmklib.url.tree.findNode(cat_seccion, cat_grupo, cat_familia, cat_subfamilia)

    # prepare the result
    categories = [ ]

    ##########################################
    # grupo
    if cat_grupo != -1 and grupo is not None:
        categories.append( {
            "Title"     : tmklib.support.capitalize(grupo["Nombre"]),
            "URL"       : "/buscador/productos.jsp?" + urllib.urlencode( {
                                "seccion"           : cat_seccion,
                                "idSeccion"         : cat_seccion,
                                "criterioDeOrden"   : 6,
                                "claveDeBusqueda"   : "porCategorias",
                                "texto"             : grupo["Descripcion"],
                                "grupo"             : cat_grupo
                            } )
        } )

    ##########################################
    # familia
    if cat_familia != -1 and familia is not None:
        categories.append( {
            "Title"     : tmklib.support.capitalize(familia["Nombre"]),
            "URL"       : "/buscador/productos.jsp?" + urllib.urlencode( {
                                "seccion"           : cat_seccion,
                                "idSeccion"         : cat_seccion,
                                "criterioDeOrden"   : 6,
                                "claveDeBusqueda"   : "porCategorias",
                                "texto"             : familia["Descripcion"],
                                "grupo"             : cat_grupo,
                                "familia"           : cat_familia
                            } )
        } )

    ##########################################
    # subfamilia
    if cat_subfamilia != -1 and subfamilia is not None:
        categories.append( {
            "Title"     : tmklib.support.capitalize(subfamilia["Nombre"]),
            "URL"       : "/buscador/productos.jsp?" + urllib.urlencode( {
                                "seccion"           : cat_seccion,
                                "idSeccion"         : cat_seccion,
                                "criterioDeOrden"   : 6,
                                "claveDeBusqueda"   : "porCategorias",
                                "texto"             : subfamilia["Descripcion"],
                                "grupo"             : cat_grupo,
                                "familia"           : cat_familia,
                                "subfamilia"        : cat_subfamilia
                            } )
        } )

    # add the categories
    row["Categories"] = categories

    return row

###################################################

def getTexts(dataset, entityType, datasetName, idList):
    """Returns the texts fro products (PROD) entities
    
    Fetches texts from the database (Articulos_Textos) and
    completes with file system files
    """
    
    # prepare the result
    texts = { }

    # protect from exceptions
    try:

        # connect to the database and get a cursor
        conn = ecommerce.db.getConnection()
        cursor = conn.cursor()

        # build the query
        ids = ", ".join( [ str(id) for id in idList ] )
        query = """
SELECT          A.Id_Articulo, A.Tipo, A.Parte, A.Tipo_Texto, A.Texto, A.Idioma,
                Ref.RV_Meaning
        FROM        Articulos_Textos A
        LEFT JOIN   CG_Ref_Codes Ref
            ON      Ref.RV_Domain = 'ONIX:TextTypeCode' AND
                    A.Tipo = Ref.RV_Low_Value
        WHERE       Id_Articulo IN (""" + ids + """)
        ORDER BY    Id_Articulo, Tipo, Parte"""
        cursor.execute(query)

        # fetch the results
        row = cursor.fetchone()
        while row is not None:

            # get some values
            id_articulo = int(row[0])
            tipo        = row[1]
            parte       = int(row[2])
            tipo_texto  = row[3]
            texto       = tmklib.support.decode("" if row[4] is None else row[4], 'iso-8859-1')
            idioma      = row[5]
            tipo_desc   = tmklib.support.decode("" if row[6] is None else row[6], 'iso-8859-1')

            # convert tipo_texto
            tipos_texto     = {
                "00"        : ("06", "Default text format"),
                "01"        : ("02", "HTML"),
                "02"        : ("02", "HTML")
            }
            tipo_texto      = tipos_texto[tipo_texto if tipo_texto in tipos_texto else "00"][0]
            tipo_texto_desc = tipos_texto[tipo_texto if tipo_texto in tipos_texto else "00"][1]

            # create the key
            key = (id_articulo, tipo)
            if key not in texts:
                # create entry
                texts[key] = {
                    "EntityType"        : "PROD",
                    "EntityId"          : id_articulo,
                    "ProductId"         : id_articulo,
                    "EntryCode"         : tipo,
                    "EntryCode_list"    : "ONIX.153",
                    "EntryCode_desc"    : tipo_desc,
                    "TextFormat"        : tipo_texto,
                    "TextFormat_list"   : "ONIX.34",
                    "TextFormat_desc"   : tipo_texto_desc,
                    "TextContent"       : texto
                }
            else:
                # append texto to existing entry
                texts[key]["TextContent"] += texto

            # next entry
            row = cursor.fetchone()
    except:
        pass

    # get a config object
    config = ecommerce.config.getConfig()

    # append first-chapters to texts
    firstChapterPath = config.get("paths.firstChapter")
    if firstChapterPath is not None:
        texts = _loadFiles("firstChapter", firstChapterPath, idList, texts, {
            "EntityType"        : "PROD",
            "EntryCode"         : "24",
            "EntryCode_list"    : "ONIX.33",
            "EntryCode_desc"    : "First Chapter"
        } )

    # append interviews to texts
    interviewsPath = config.get("paths.interviews")
    if firstChapterPath is not None:
        texts = _loadFiles("interview", interviewsPath, idList, texts, {
            "EntityType"        : "PROD",
            "EntryCode"         : "40",
            "EntryCode_list"    : "ONIX.33",
            "EntryCode_desc"    : "Author interview"
        } )

    # create the real result
    result = { }

    # process the intermediate texts
    keys = sorted(texts.keys())
    for k in keys:

        # get the product id
        productId = Decimal(k[0])

        # if product not in result, create the entry
        if productId not in result:
            result[productId] = [ texts[k] ]
        else:
            result[productId].append(texts[k])

    return result

###################################################

def _loadFiles(fileType, path, idList, texts, entryBase):
    """Scan the idList to see if some data is available in the specified path"""

    for i in range(len(idList)):

        # check the cache to get the path
        fname = None
        if fileType == "firstChapter":
            fname = tmklib.cache.findFirstChapter(idList[i])
        if fileType == "interview":
            fname = tmklib.cache.findInterview(idList[i])
        if fname is None:
            continue            # not in cache => not present...

        # if no file => next
        fname = path + os.sep + fname

        # get the file contents
        text = None
        try:
            f = open(fname, "r")
            text = tmklib.support.decode(f.read(), 'iso-8859-1')
            f.close()
        except:
            pass
        if text is None:
            continue

        # try to figure out the text format
        textFormat = "06"       # assume is plain text
        if re.search("<[a-zA-Z]( |>|\/)?", text) is not None:
            textFormat = "02"

        # got a first chapter, add it to the list
        key = (idList[i], "24")

        # create entry
        data = entryBase.copy()
        data["EntityId"]    = Decimal(idList[i])
        data["ProductId"]   = Decimal(idList[i])
        data["TextContent"] = text

        if textFormat == "02":
            data["TextFormat"]      = "02"
            data["TextFormat_list"] = "ONIX.34"
            data["TextFormat_desc"] = "HTML"
        if textFormat == "06":
            data["TextFormat"]      = "06"
            data["TextFormat_list"] = "ONIX.34"
            data["TextFormat_desc"] = "Default text format"


        # save the entry
        texts[key] = data

    return texts

###################################################

def author_texts(row):
    """Check if the author has texts (biography) and add the content"""

    # get a config object
    config = ecommerce.config.getConfig()

    # create an empty Text item in the record
    row["Texts"] = [ ]

    # if no contributor id => do nothing
    if "ContributorId" not in row:
        return row
    contributorId = row["ContributorId"].to_integral_value()

    # get the file name from the cache
    fname = tmklib.cache.findBiography(contributorId)
    if fname is None:
        return row

    # get the path to biographies
    biographyPath = config.get("paths.biography")
    fname = biographyPath + os.sep + fname

    # read the file
    text = None
    try:
        f = open(fname, "r")
        text = tmklib.support.decode(f.read(), 'iso-8859-1')
        f.close()

        # append only if there is text
        if text is None:
            return row

        # try to figure out the text format
        textFormat = "06"       # assume is plain text
        if re.search("<[a-zA-Z]( |>|\/)?", text) is not None:
            textFormat = "02"

        # append the entry
        row["Texts"].append( {
            "EntityType"        : "CONT",
            "EntityId"          : contributorId,
            "ContributorId"     : contributorId,
            "EntryCode"         : "13",
            "EntryCode_list"    : "ONIX.33",
            "EntryCode_desc"    : "Biographical note",
            "TextFormat"        : textFormat,
            "TextFormat_list"   : "ONIX.34",
            "TextFormat_desc"   : "HTML" if textFormat == "02" else "Default text format",
            "TextContent"       : text
        } )
    except:
        pass

    return row


__all__ = [ "getTexts", "author_texts", "categories" ]
