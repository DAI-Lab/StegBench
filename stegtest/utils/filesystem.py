"""Filesystem utility functions."""
import os
import errno

from os import path
from stegtest.utils.helpers.embeddor_helpers import add_embeddor_to_file
# from stegtest.

def file_exists(path):
    return path.exists(path)

def makedirs(path):
    """Create directory recursively if not exists.
    Similar to `makedir -p`, you can skip checking existence before this function.

    Parameters
    ----------
    path : str
        Path of the desired dir
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

def get_last_file(type):
    return 'stub_last_file'

def get_file_from_hash(hash):
    #TODO can optimize here with a database
    open_lookup_table


def get_hash_of_file(file):
    return 0

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