"""Product (PROD) price calculation functions

This is related to taxes

by Jose Luis Campanello
"""

from decimal import Decimal

import ecommerce.db

_taxes = None

TWODIGITS = Decimal('0.01')

def calculateTaxes(row):
    """Do a tax calculation and set the new price"""

    # initialize (if needed)
    _initialize()    

    # sanity checks
    if row["PriceAmount"] is None or row["Id_Impuesto"] is None:
        return row

    # get handy data
    priceAmount = Decimal(row["PriceAmount"])
    taxId       = int(row["Id_Impuesto"])
    taxDef      = _taxes[taxId] if taxId in _taxes else { }

    # calculate the individual taxes values
    partials = [ priceAmount ]
    for tax in taxDef:

        # calculate the tax amount
        taxAmount = Decimal(priceAmount * taxDef[tax] / Decimal(100.0)).quantize(TWODIGITS)

        # append to the partials list
        partials.append(taxAmount)

    # set the new price
    row["PriceAmount"] = sum(partials)

    return row

def _initialize():
    """Load the taxes from the database (just once)"""

    global _taxes

    # if initialized, do nothing
    if _taxes is not None:
        return

    # get a connection to the database
    conn = ecommerce.db.getConnection()
    cursor = conn.cursor()

    # execute the query
    cursor.execute("""
SELECT          TT.Id_Impuesto, TT.Tasa_General, TT.Tasa_Percep_Video
    FROM        (
        SELECT          T.Id_Impuesto, T.Tasa_General, T.Tasa_Percep_Video,
                        row_number() OVER (PARTITION BY T.Id_Impuesto ORDER BY T.Fecha_Vigencia DESC)
                                            AS Row_Number
            FROM        Tasas T
            WHERE       T.Id_Tipo_Contribuyente = 5 AND
                        T.Anulado = 'NO'
    ) TT
    WHERE       TT.Row_Number = 1
    ORDER BY    TT.Id_Impuesto
""")

    # process the taxes
    taxes = { }
    row = cursor.fetchone()
    while row is not None:

        # get the data
        taxId = int(row[0])

        taxes[taxId] = {
            "VAT"       : Decimal(row[1]),
            "Video"     : Decimal(0) if row[2] is None else Decimal(row[2])
        }

        # next
        row = cursor.fetchone()

    cursor.close()

    # set the cache
    _taxes = taxes
