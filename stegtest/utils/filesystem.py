"""Filesystem utility functions."""
import os
import csv
import errno
import uuid
import shutil

from hashlib import sha512
from os import path

def get_uuid():
    return str(uuid.uuid4())

def create_file_from_hash(uuid, type):
    return sha512(uuid.encode('utf-8')).hexdigest() + '.' + type

def dir_exists(directory):
    return path.isdir(directory)

def file_exists(file):
    return path.exists(file)

def remove_file(file):
    if not file_exists(file):
        raise Error('file does not exist')

    os.remove(file)

def make_file(path):
    """Creates file if it does not exist."""
    if not file_exists(path):
        with open(path, 'w'): pass

def make_dirs(path):
    """Creates directory recursively if it does not exist."""
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

def write_to_text_file(path_to_file, rows, override=False):
    if file_exists(path_to_file) and not override:
        mode = 'a'
    else:
        mode = 'w'

    with open("Output.txt", "w") as text_file:
        for row in rows:
            text_file.write(row)
    text_file.close()

def write_to_csv_file(path_to_file, rows, override=False):
    """writes data to a csv file"""
    ##TODO need to verify that this adds to a csv file if it already exists and does not override it###
    if file_exists(path_to_file) and not override:
        mode = 'a'
    else:
        mode = 'w'
 
    with open(path_to_file, mode) as out:
        csv_out = csv.writer(out)
        
        for row in rows:
            csv_out.writerow(row)

    out.close()

def read_csv_file(path_to_file):
    with open(path_to_file, 'r') as in_file:
        reader = csv.reader(in_file)
        rows = [list(row) for row in reader]

    in_file.close()
    return rows

def clean_filesystem(directories):
    """removes directories defined in bindings"""
    for directory in directories:
        if dir_exists(directory):
            shutil.rmtree(directory)
