"""Filesystem utility functions."""
import os
import errno
import uuid
import shutil

import stegtest.utils.bindings as bd

from os import path
from stegtest.utils.helpers.embeddor_helpers import add_embeddor_to_file

# from stegtest.

def get_uuid():
    return uuid.uuid4()

def dir_exists(directory):
    return path.isdir(directory)

def file_exists(file):
    return path.exists(file)

def makefile(path):
    """Creates file if it does not exist."""
    if not file_exists(path):
        with open(path, 'w'): pass

def makedirs(path):
    """Creates directory recursively if it does not exist."""
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

def get_last_file(type):
    raise NotImplementedError

def get_file_from_hash(type, hash):

    #TODO can optimize here with a database
    #TODO open_lookup_table
    raise NotImplementedError

def get_hash_of_file(file):
    raise NotImplementedError

def write_to_file(type, file, options):
    assert(type == bd.embeddor or type == bd.detector or type == bd.db)
    def get_writer(type):
        return {
        'embeddor': add_embeddor_to_file,
        'detector': None,
        'db': None,
        }[type]

    writer = get_writer(type)
    wrtier(options)

def clean_filesystem():
    """removes directories defined in bindings"""
    directories = bd.get_directories()
    for directory in directories:
        if dir_exists(directory):
            shutil.rmtree(directory)
