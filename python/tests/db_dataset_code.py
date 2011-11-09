import hashlib


def md5Hash(dataset, entityType, datasetName, idList):
    """For each entry, return an md5 hash of the id"""

    result = { }
    for id in idList:
        result[id] = hashlib.md5(str(id)).hexdigest()

    return result
