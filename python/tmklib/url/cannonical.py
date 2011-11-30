"""DB data fetch for Entity Types

by Jose Luis Campanello
"""

import ecommerce.config
import ecommerce.db

import tmklib.support
import tmklib.fixes
import tmklib.fixes.PROD
import tmklib.fixes.SUBJ
import tmklib.fixes.CONT
import tmklib.fixes.IMPR
import tmklib.fixes.PAGE

########################################################

def fetch(entityType, entityIds):
    """Fetch data depending on the entity type
    
    NOTE: entityIds is a dictionary where keys are entity ids
    """

    print "cannonical.fetch. entity [%s], ids %s" % (entityType, entityIds)

    # call the appropriate function
    if entityType == "SUBJ":
        return fetchSUBJ(entityType, entityIds)
    elif entityType == "PROD":
        return fetchPROD(entityType, entityIds)
    elif entityType == "IMPR":
        return fetchIMPR(entityType, entityIds)
    elif entityType == "CONT":
        return fetchCONT(entityType, entityIds)
    elif entityType == "PAGE":
        return fetchPAGE(entityType, entityIds)

    # return empty for anything we don't know
    return { id : { } for id in entityIds }


########################################################

def fetchSUBJ(entityType, entityIds):
    """Fetch data for SUBJ entities"""

    # get a connection and cursor
    conn = ecommerce.db.getConnection()
    cursor = conn.cursor()

    # execute que query
    idlist = ", ".join( [ str(k) for k in entityIds.keys() ])
    query  = """
SELECT      SubjectId               AS SubjectId,
            Categoria_Seccion       AS Categoria_Seccion,
            Categoria_Grupo         AS Categoria_Grupo,
            Categoria_Familia       AS Categoria_Familia,
            Categoria_Subfamilia    AS Categoria_Subfamilia,
            Subtype                 AS Subtype
    FROM    Stage0_Subjects
    WHERE   SubjectId IN (""" + idlist + ")"
    cursor.execute(query)

    row = cursor.fetchone()
    while row is not None:

        # get the id
        (id, seccion, grupo, familia, subfamilia, subtype) = (
            int(row[0]), int(row[1]), int(row[2]), 
            int(row[3]), int(row[4]), row[5]
        )

        # set the values
        entityIds[id] = {
            "SubjectId"             : id,
            "Categoria_Seccion"     : seccion,
            "Categoria_Grupo"       : grupo,
            "Categoria_Familia"     : familia,
            "Categoria_Subfamilia"  : subfamilia,
            "Subtype"               : subtype
        }

        # next row
        row = cursor.fetchone()

    # close the cursor
    cursor.close()

    return entityIds


########################################################

def fetchPROD(entityType, entityIds):
    """Fetch data for PROD entities"""

    # get a connection and cursor
    conn = ecommerce.db.getConnection()
    cursor = conn.cursor()

    # execute que query
    idlist = ", ".join( [ str(k) for k in entityIds.keys() ])
    query  = """
SELECT      Id_Articulo             AS ProductId,
            Categoria_Seccion       AS Categoria_Seccion,
            Categoria_Grupo         AS Categoria_Grupo,
            Categoria_Familia       AS Categoria_Familia,
            Categoria_Subfamilia    AS Categoria_Subfamilia,
            Titulo                  AS Title
    FROM    Articulos
    WHERE   Id_Articulo IN (""" + idlist + ")"
    cursor.execute(query)

    row = cursor.fetchone()
    while row is not None:

        # get the id
        (id, seccion, grupo, familia, subfamilia, title) = (
            int(row[0]), int(row[1]), int(row[2]), 
            int(row[3]), int(row[4]), row[5]
        )

        # set the values
        entityIds[id] = tmklib.fixes.PROD.title( {
            "ProductId"             : id,
            "EntityId"              : id,
            "Categoria_Seccion"     : seccion,
            "Categoria_Grupo"       : grupo,
            "Categoria_Familia"     : familia,
            "Categoria_Subfamilia"  : subfamilia,
            "Title"                 : title
        } )

        # next row
        row = cursor.fetchone()

    # close the cursor
    cursor.close()

    return entityIds


########################################################

def fetchIMPR(entityType, entityIds):
    """Fetch data for IMPR entities
    
    NOTE: not returning data because it requires Categoria_Seccion
    """

    # return empty for anything we don't know
    return { id : { } for id in entityIds }


########################################################

def fetchCONT(entityType, entityIds):
    """Fetch data for CONT entities
    
    NOTE: not returning data because it requires Categoria_Seccion
    """

    # return empty for anything we don't know
    return { id : { } for id in entityIds }


########################################################

def fetchPAGE(entityType, entityIds):
    """Fetch data for PAGE entities
    
    NOTE: returning empty for all pages
    """

    print "fetchPAGE"

    # return empty for anything we don't know
    return { id : { } for id in entityIds }
