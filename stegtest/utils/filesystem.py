"""Filesystem utility functions."""
import os
import errno
import uuid

from os import path
from stegtest.utils.helpers.embeddor_helpers import add_embeddor_to_file

# from stegtest.

def get_uuid():
    return uuid.uuid4()

def file_exists(file):
    return path.exists(file)

def makefile(path):
    """Creates file if it does not exist."""
    print(path)
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

def get_file_from_hash(hash):
    #TODO can optimize here with a database
    #TODO open_lookup_table
    raise NotImplementedError

def get_hash_of_file(file):
    raise NotImplementedError

def write_to_file(type, file, options):
    assert(type == 'embeddor' or type == 'detector' or type == 'db')
    def get_writer(type):
        return {
        'embeddor': add_embeddor_to_file,
        'detector': None,
        'db': None,
        }[type]

    writer = get_writer(type)
    wrtier(options)

def clean_filesystem():
    raise NotImplementedError