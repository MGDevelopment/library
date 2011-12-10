#!/usr/bin/env python
"""Key generation program

This file contains a class that implements password management. The
class is created inside a Config object and handles access to
passwords.
"""

import sys

import random
import hashlib

from os.path   import exists, join as os_path_join
from yaml      import safe_load
import pyDes

from loader    import *

defaultConfig = """
---
keychain:
  file:     keychain.yaml
  dirs:
    - ./config
    - /etc/ecommerce
"""

class Keychain(object):
    """Keychain class

    The Keychain is contained in a separate file. Each key (password)
    has a name. In this implementation passwords are stored in cleartext,
    but the existence of the class provides for a mechanism to have them
    encrypted.

    Keys are accessed by name. The method "fetch" receives a key name and
    returns the decrypted password. Key names are represented by a string
    of the form "keychain:{keyname}:{value}". If the method "fetch" receives
    an input that does not conform to that syntax, it returns the same value.
    This allows for keys to be stored cleartext in config files without
    requiring the application to be aware of which keys are encrypted.
    The application can just get the password attribute and pass the value
    thru the keychain, which will decrypt if encrypted or do nothing.

    Two configuration variables are required:
    - keychain.file (default keychain.yaml)
    - keychain.dirs (defaults to [ "./config", "/etc/ecommerce" ])
    """

    def __init__(self, config = None):

        # be sure we have a config or create one with default values
        if config is None:
            config = getConfigFromString(defaultConfig)

        # get the config
        self._fileName = config.get("keychain.file")
        self._dirNames = config.get("keychain.dirs", [ ])

        # find and load the keychain file
        self._fullPath = self._keychainFind()
        self._keychain = self._keychainLoad()

        # figure out the master key
        self._getMasterKey()



    def _keychainFind(self):
        """Finds the keychain file"""

        # iterate each dir
        for d in self._dirNames:

            # build the expected name
            fullPath = os_path_join(d, self._fileName)

            # if exists, return that
            if exists(fullPath):
                return fullPath

        # fail
        #####raise IOError('Keychain file [%s] not found' % self._fileName)
        return None


    def _keychainLoad(self):
        """Loads the keychain file"""

        # only if it makes sense
        if self._fullPath is None:
            return { }      # empty keychain

        # read the file content
        f = open(self._fullPath, "r")
        keys = f.read()
        f.close()

        # parse the keychain
        return safe_load(keys)


    def _getMasterKey(self):
        """Finds the master key (or calculates one if none)"""

        # if no master key => calculate one
        if "master-key" not in self._keychain:

            self._keychain["master-key"] = { }

        # get the data (or generate one)
        if "data" not in self._keychain["master-key"]:

            # initialize the random seed
            random.seed()

            # generate 256 bytes of random data (512 chars) and save it
            data = "".join( [ "%02.2x" % random.randint(0, 255) for i in range(256) ] )
            self._keychain["master-key"]["data"] = data

            # initialize the random seed
            random.seed()

        # get the data
        data = self._keychain["master-key"]["data"]

        # initialize the random seed
        random.seed(data)

        # generate 4kb random data to calculate the master key
        self._mkSeed        = "".join( [ "%02.2x" % random.randint(0, 255)
                                         for i in range(4096) ] )
        self._mkSeedDigest  = hashlib.sha512(self._mkSeed).digest()


    def fetch(self, key):
        """Fetches the given key from the keychain

        If key does not conform to the syntax "keychain:{keyname}:{value}"
        it is returned without any change. If the key named "{keyname}"
        is not found, an KeyError exception is raised
        """

        # if doesn't match the keychain syntax, return as is
        if not key.startswith("keychain:"):
            return key

        # get the key parts
        parts = key.split(":")
        if len(parts) != 3:
            raise KeyError("Key [%s] is not a valid keychain id" % key)
        (protocol, keyName, keyValue) = (parts[0], parts[1], parts[2])

        # if the key is not in the keychain, raise
        if keyName not in self._keychain:
            raise KeyError("Key [%s] not in keychain" % keyName)
        keyData = self._keychain[keyName]

        # figure out the algorithm (asume clear if none informed) and get it
        algorithm = "alg_" + keyData.get("algorithm", "clear")
        try:
            _alg = self.__getattribute__(algorithm)
        except AttributeError:
            raise KeyError("Keychain Key [%s] has an algorithm [%s] that does not exist" % (keyName, algorithm))

        # dispatch the method
        return _alg(protocol, keyName, keyValue, keyData)


    def alg_clear(self, protocol, keyName, keyValue, keyData):
        """Clear text algorithm"""

        # check there is a "data" element
        if "data" not in keyData:
            raise KeyError("Keychain Key [%s] has no data" % keyName)

        # for now, return the value as is
        return self._keychain[keyName]["data"].get(keyValue)


    def alg_3DES_CBC(self, protocol, keyName, keyValue, keyData):
        """Triple-DES/CBC algorithm"""

        # check there is a "data" element
        if "data" not in keyData:
            raise KeyError("Keychain Key [%s] has no data" % keyName)

        # get the encripted value
        ciphertext = self._keychain[keyName]["data"].get(keyValue)

        # get the 3des key and iv
        mKey = self._mkSeedDigest[0:24]
        mIV  = self._mkSeedDigest[-8:]

        # create the triple-des object and decrypt
        cipher = pyDes.triple_des(mKey, pyDes.CBC, mIV, pad=None, padmode=pyDes.PAD_PKCS5)
        value = cipher.decrypt(ciphertext)

        return value

###################################################

_mkSeed         = None
_mkSeedDigest   = None

def _masterKey(master):

    global _mkSeed
    global _mkSeedDigest

    # initialize the random seed
    random.seed(master)

    # generate 4kb random data to calculate the master key
    _mkSeed        = "".join( [ "%02.2x" % random.randint(0, 255)
                                for i in range(4096) ] )
    _mkSeedDigest  = hashlib.sha512(_mkSeed).digest()


###################################################

def fcn_3DES_CBC(isCrypt, master, text):

    # process the master key
    _masterKey(master)

    # prepare the input text
    inputText = text
    if not isCrypt:
        # is decrypt and the input is hexa string
        inputText = "".join([ chr(int(text[i:i+2], 16)) for i in range(0, len(text), 2) ])

    # get the 3des key and iv
    mKey = _mkSeedDigest[0:24]
    mIV  = _mkSeedDigest[-8:]

    # create the triple-des object and decrypt
    cipher = pyDes.triple_des(mKey, pyDes.CBC, mIV, pad=None, padmode=pyDes.PAD_PKCS5)

    # crypt or decrypt
    value = cipher.encrypt(inputText) if isCrypt else cipher.decrypt(inputText)

    # make printable (if needed)
    if isCrypt:
        value = "".join( [ "%02.2x" % ord(i) for i in value ] )

    return value

###################################################

def fcn_clear(isCrypt, master, text):

    return text

###################################################

algorithms = {
    "3DES_CBC":     {
        "desc"      : "Triple-DES CBC encription (24 bits password + Initialization vector)",
        "fcn"       : fcn_3DES_CBC
    },
    "clear":        {
        "desc"      : "Clear text password",
        "fcn"       : fcn_clear
    }
}

###################################################

def cmdAlgorithms():

    print ""
    print "The list of encription algorithms is:"
    for a in sorted(algorithms.keys()):
        print "%-10s = %s" % (a, algorithms[a]["desc"])
    print ""

    return True

###################################################

def cmdCrypt():

    # check we have 3 parameters (plus pname and command)
    if len(sys.argv) < 5:
        print ""
        print "Crypt command requires 3 parameters, use command help"
        print ""
        return False

    # get the param values
    (master, algorithm, text) = (sys.argv[2], sys.argv[3], sys.argv[4])

    # check algorithm is valid
    if algorithm not in algorithms:
        print ""
        print "ERROR: algorithm [%s] is unknown, use command algorithms" % algorithm
        print ""
        return False

    # call the algorithm to get the cyphertext
    cyphertext = algorithms[algorithm]["fcn"](True, master, text)

    # print the encrypted text
    print """
The encrypted text is:

%s

""" % cyphertext

    return True


###################################################

def cmdDecrypt():

    # check we have 3 parameters (plus pname and command)
    if len(sys.argv) < 5:
        print ""
        print "Decrypt command requires 3 parameters, use command help"
        print ""
        return False

    # get the param values
    (master, algorithm, cyphertext) = (sys.argv[2], sys.argv[3], sys.argv[4])

    # check algorithm is valid
    if algorithm not in algorithms:
        print ""
        print "ERROR: algorithm [%s] is unknown, use command algorithms" % algorithm
        print ""
        return False

    # call the algorithm to get the clear
    text = algorithms[algorithm]["fcn"](False, master, cyphertext)

    # print the encrypted text
    print """
The decrypted text is:

%s

""" % text

    return True

###################################################

def cmdHelp():
    """Print usage help"""

    print """
usage: python keygen.py <command> [<params>]

where command is one of:

- algorithms --- list the encryption algorithms
- crypt --- crypt some text. Requires 3 params: master-key algorithm text
- decrypt --- decrypt some text. Requires 3 params: master-key algorithm text
- help --- this screen
- master --- requires no params, prints a master key
"""

    return True

###################################################

def cmdMaster():

    # generate a 
    master = "".join( [ "%02.2x" % random.randint(0, 255) for i in range(64) ] )

    # print the master key
    print ""
    print "The new master key is\n\n%s" % master
    print ""
    print "You must edit keychain.yaml and add the following:"
    print """
master-key:
    data: %s
    """ % master
    print ""
    print ""

    return True

###################################################

commands = {
    "algorithms":   cmdAlgorithms,
    "crypt":        cmdCrypt,
    "decrypt":      cmdDecrypt,
    "help":         cmdHelp,
    "master":       cmdMaster
}

def main():

    # figure out the command (default is help)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd not in commands:
        cmd = "help"

    # dispatch the command
    commands[cmd]()


if __name__ == "__main__":
    main()
