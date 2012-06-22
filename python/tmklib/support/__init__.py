"""Support functions for TMK library

by Jose Luis Campanello
"""

import types
import string
import unicodedata

########################################################

def decode(value, encoding = None):
    """If a string type and there's an encoding other than UTF-8, convert"""

    # need enconding and a string type
    if encoding is None:
        return value

    # if not a string => just return as is
    if not isinstance(value, types.StringType):
        return value

    # only for strings (non-unicode)
    try:
        if isinstance(value, types.StringType):
            if encoding != "UTF-8" and encoding != "utf-8":
                value = value.decode(encoding).encode('utf8')
    except UnicodeEncodeError:
        # if there was a unicode error, assume the input is unicode
        value = value.decode('utf-8') ###unicode(value)

    return value

########################################################


def noDiacritics(s):
    """Removes any diacritics"""

    # sanity check
    if s is None:
        return None

    # try the right way first
    try:
        str = unicode(s, 'utf-8')
        # remove some chars
        str = str.replace(unichr(0xba), "")     # 4o
        str = str.replace(unichr(0xaa), "")     # 4a
        # normalization
        ret = unicodedata.normalize('NFKD', str)
        ret = ret.encode('ascii', 'ignore')
    except:
        ret = None

    # try as a unicode encoded string
    if ret is None:
        try:
            str = s.decode(s, 'utf-8')
            # remove some chars
            str = str.replace(unichr(0xba), "")     # 4o
            str = str.replace(unichr(0xaa), "")     # 4a
            # normalization
            ret = unicodedata.normalize('NFKD', str)
            ret = ret.encode('ascii', 'ignore')
        except:
            ret = s     # return as received

    return ret

########################################################


def alphaOnly(s, endDots = False):
    """Removes any character that is not a letter or digit"""

    dotCount = 0
    dotStr   = ""
    if endDots:
        while s.endswith(".", 1, len(s) - dotCount):
            dotStr   += "."
            dotCount += 1

    # strip non digits, non letters (upper or lower) and non ",", "-", "." or space AS "_"
    s = s.translate(string.maketrans(",-. ", "____"))
    s = "".join(i for i in s if i in \
                ("0123456789" + \
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + \
                "abcdefghijklmnopqrstuvwxyz" + \
                "_"))

    if endDots and dotCount > 0:
        s = s[:len(s)-dotCount] + dotStr

    return s

########################################################

def smartStrip(s):

    # remove _
    s = s.strip("_")

    # replace ending dot by _
    dotCount = 0
    dotStr   = ""
    while s.endswith(".", 1, len(s) - dotCount):
        dotStr   += "_"
        dotCount += 1
    if dotCount > 0:
        s = s[:len(s)-dotCount] + dotStr

    return s

########################################################

def capitalize(s, fullReplacement = True):

    ######### FROM method corregir

    # trim, uppercase and do some replacements
    #
    # NOTE: this can look nice as s.replace(...).replace(...) but
    #       creating strings like that kills performance...
    #
    s = s.strip().upper()
    if "\\." in s:
        s = s.replace("\\.", " .",  1)
    if "," in s:
        s = s.replace(",", " , ",  1)
    if ";" in s:
        s = s.replace(";", " ; ",  1)
    if "-" in s:
        s = s.replace("-", " - ",  1)
    if "/" in s:
        s = s.replace("/", " / ",  1)
    if "  " in s:
        s = s.replace("  ", " ")

    # swap articulos (ej: "inmortales, los" => "los inmortales")
    s = swapArticulos(s, capitalize.rList, fullReplacement)

    ######### FROM call to method capitalizarOriginal
    su = unicode(s, 'utf-8')
    s  = su.title().encode('utf-8')
    #
    # JLUIS - the following leaves diacritics in the wrong case
    #
    #s = s.title()

    ######### FROM call to method minisculizar
    s = minusculizar(s)

    ######### FROM call to method mayusculizar
    s = mayusculizar(s)

    # some replacements and trim
    #
    # NOTE: this can look nice as s.replace(...).replace(...) but
    #       creating strings like that kills performance...
    #
    if " \\." in s:
        s = s.replace(" \\.", ".",  1)
    if " ," in s:
        s = s.replace(" ,", ",",  1)
    if " ;" in s:
        s = s.replace(" ;", ";",  1)
    s = s.strip()

    return s
capitalize.rList = [   \
    (", EL ",  "EL "),  \
    (", LA ",  "LA "),  \
    (", LO ",  "LO "),  \
    (", LOS ", "LOS "), \
    (", LAS ", "LAS "), \
    (", THE ", "THE "), \
    (", LES ", "LES ")  \
]

########################################################

def swapArticulos(s, rList, fullReplacement = True):

    # append a space
    s += " "

    # full replacement => iterate
    if fullReplacement:

        # iterate (if needed)
        lastSpot = 0
        while fullReplacement and (lastSpot < len(s)):

            # find the place where the swap is to happen
            spot = s.find(".", lastSpot)
            if spot < 0:
                spot = s.find("-", lastSpot)
                if spot < 0:
                    #    if s.find(" Y ", lastSpot) >= 0:
                    #        spot = s.find(" Y ", lastSpot) + 1
                    #    else:
                    #        spot = -1
                    spot = -1
                    if spot < 0:
                        spot = len(s)

            # replace
            for r in rList:
                #
                # the endswith performs a find but does not create
                # a new string
                #
                ####if s[spot - len(r[0]):spot] == r[0]:
                if s.endswith(r[0], spot - len(r[0]), spot):
                    if lastSpot == 0:
                        # move to the begining
                        s = r[1] + s[:spot - len(r[0])] + s[spot:]
                    else:
                        # move to the begining of lastSpot
                        s = s[:lastSpot - 1] + r[1] + s[lastSpot - 1:spot - len(r[0])]
                    break

            # go from this spot
            lastSpot = spot + 1

    else:
        # single replacement

        # find the place where the swap is to happen
        lastSpot = 0
        spot = s.find(".", lastSpot)
        if spot < 0:
            spot = s.find("-", lastSpot)
            if spot < 0:
                spot = len(s)

        # replace
        for r in rList:
            #
            # the endswith performs a find but does not create
            # a new string
            #
            if s.endswith(r[0], spot - len(r[0]), spot):
                if lastSpot == 0:
                    # move to the begining
                    s = r[1] + s[:spot - len(r[0])] + s[spot:]
                else:
                    # move to the begining of lastSpot
                    s = s[:lastSpot - 1] + r[1] + s[lastSpot - 1:spot - len(r[0])]
                break

    return s

########################################################

def mayusculizar(s):
    """Convert some words to upper case"""
    
    # iterate over the words to capitalize
    for word in mayusculizar.words:
        if word in s:
            s = s.replace(word, word.upper())

    return s
mayusculizar.words = [                              \
    " Cd ", " Dvd ", " Egb ", " Mtv ", " Ntsc ",    \
    " Pal ", " Palm ", " Vhs ",                     \
    #roman numbers
    " Ii ", " Iii ", " Iv ", " Vi ", " Vii ",       \
    " Viii ", " Ix ", " Xi ", " Xii ", " Xiii ",    \
    " Xiv", " Xv ", " Xvi ", " Xvii ", " Xviii ",   \
    " Xix ", " Xx ", " Xxi "
]

########################################################

def minusculizar(s):
    """Convert some words to lower case
    
    NOTE: it does not work very well. If the word is at the
          begining is not replaced (even if it appears further
          ahead)
    """

    for word in minusculizar.words:
        pos = s.find(word)
        if pos > 0:             # only if not at the begining
            if not s[pos - 1] in "./:-#!#?{}()[]":      # previous not a termination
                if (pos + len(word)) < len(s) and s[pos + len(word)] in " ./:-#!#?{}()[]":
                    s = s.replace(word, word.lower())

    return s
minusculizar.words = [ \
    "A", "B", "C", "E", "O", "Y", "Al", "Ante",         \
    "Aquel", "Como", "Con", "Contra", "Cualquier",      \
    "De", "Del", "Desde", "Dos", "El", "En",            \
    "Entre", "Es", "Esa", "Ese", "Esta", "Fue",         \
    "Hacia", "La", "Las", "Lo", "Los", "Me",            \
    "Mejor", "Menos", "Mi", "Ni", "No", "Para",         \
    "Por", "Que", "Se", "Ser", "Sin", "Sobre",          \
    "Sola", "Solo", "Son", "Soy", "Su", "Sus",          \
    "Te", "Tema", "Tiene", "Toda", "Todas", "Tres",     \
    "Tu", "Un", "Una", "Unas", "Uno", "Unos", "Va"      \
]


__all__ = [ "decode", "noDiacritics", "alphaOnly", 
            "capitalize", "swapArticulos", "mayusculizar", 
            "minusculizar" ]
