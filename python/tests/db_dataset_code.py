import hashlib


def md5Hash(dataset, entityType, datasetName, idList):
    """For each entry, return an md5 hash of the id"""

    result = { }
    for id in idList:
        result[id] = hashlib.md5(str(id)).hexdigest()

    return result

def title_reverse(row):
    """Add an attribute with the reversed value of the attribute Title"""

    # if the attribute is there...
    if "Title" in row:
        row["RTitle"] = row["Title"][::-1]

    return row

