#!/usr/bin/env python
"""Config file keychain

This file contains a class that implements password management. The
class is created inside a Config object and handles access to
passwords.
"""

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

        # get the encripted value and convert to binary (input is hexa string)
        ciphertext = self._keychain[keyName]["data"].get(keyValue)
        ciphertext = "".join([ chr(int(ciphertext[i:i+2], 16)) for i in range(0, len(ciphertext), 2) ])

        # get the 3des key and iv
        mKey = self._mkSeedDigest[0:24]
        mIV  = self._mkSeedDigest[-8:]

        # create the triple-des object and decrypt
        cipher = pyDes.triple_des(mKey, pyDes.CBC, mIV, pad=None, padmode=pyDes.PAD_PKCS5)
        value = cipher.decrypt(ciphertext)

        return value
