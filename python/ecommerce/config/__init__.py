#!/usr/bin/env python
"""Ecommerce module for ILHSA SA
by Alejo Sanchez, Jose Luis Campanello and Mariano Goldsman
"""
from os.path import exists, join
from sys import exc_info
from yaml import safe_load


dirs = [ "./config", "/etc/ecommerce" ] # Directories to find XXX S3

__all__ = [ "test" ] # Exported names

if __name__ == "__main__":
    print "Exports: ", __all__

def find_file(name, paths):
    '''Find an existing file in a list of paths'''
    for dir in paths:
        fn = join(dir, name)
        if exists(fn):
            return fn
    raise IOError('File not found: ' + name)

def merge_files(*args):
    '''Open multiple files and return content concatenated'''
    if len(args) == 0:
        return ''
    ret = ''
    for f in args:
        print 'Config file: ', f
        try:
            fd = open(f, 'r')
        except:
            print 'Error opening configuration file "' + f + '"', exc_info()[0]
            raise # re-raise exception
        ret += fd.read() # join strings
    return ret

class Config(object):
    '''Configuration pareser
           paths:   paths where to look up configuration files
           fglobal: file name for global configuration file
           flocal:  file name for local configuration file
    '''
    def __init__(self, paths=dirs, fglobal='global.yaml', flocal='local.yaml'):
        # Open and concatenate files
        # Find global file
        self.conf = safe_load(merge_files(find_file(fglobal, paths),
                                          find_file(flocal,  paths)))
        #print "DEBUG\n", self.conf

