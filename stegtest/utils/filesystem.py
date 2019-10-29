"""Filesystem utility functions."""
import os
import csv
import errno
import uuid
import shutil
import json

from hashlib import sha512
from os import path

def get_uuid():
    return str(uuid.uuid4())

def get_directory(file_path):
    return os.path.dirname(file_path)

def get_extension(file_path):
    filename, file_extension = os.path.splitext(file_path)
    return file_extension

def create_name_from_hash(to_hash):
    return sha512(to_hash.encode('utf-8')).hexdigest() 

def create_file_from_hash(to_hash:str, type:str):
    return create_name_from_hash(to_hash) + '.' + type

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

def make_dir(path):
    """Creates directory recursively if it does not exist."""
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

def write_to_text_file(path_to_file, rows, override=False):
    """writes data to a text file"""
    if file_exists(path_to_file) and not override:
        mode = 'a'
    else:
        mode = 'w'

    with open(path_to_file, mode) as text_file:
        for row in rows:
            text_file.write(row)
    text_file.close()

def write_to_csv_file(path_to_file, rows, override=False):
    """writes data to a csv file"""
    if file_exists(path_to_file) and not override:
        mode = 'a'
    else:
        mode = 'w'
 
    with open(path_to_file, mode) as out:
        csv_out = csv.writer(out)
        
        for row in rows:
            csv_out.writerow(row)

    out.close()

def write_to_json_file(path_to_file, data):
    """writes json data to a file"""
    with open(path_to_file, 'w') as out:
        json.dump(data, out)

    out.close()

def convert_csv_to_dict(rows):
    header = rows[0]
    data = rows[1:]

    data_to_dict = []
    for row in data:
        assert(len(row) == len(header)) #have to be the same to match properly
        
        row_dict = {}
        for i in range(len(row)):
            row_dict[header[i]] = row[i]

        data_to_dict.append(row_dict)

    return data_to_dict

def read_csv_file(path_to_file, return_as_dict=False):
    with open(path_to_file, 'r') as in_file:
        reader = csv.reader(in_file)
        rows = [list(row) for row in reader]

    in_file.close()

    if return_as_dict:
        return convert_csv_to_dict(rows)

    return rows

def read_json_file(path_to_file):
    with open(path_to_file, 'r') as in_file:
        datastore = json.load(in_file)

    in_file.close()

    return datastore

def remove_file(path_to_file):
    if file_exists(path_to_file):
        os.remove(path_to_file)

def clean_filesystem(directories):
    """removes directories defined in bindings"""
    for directory in directories:
        if dir_exists(directory):
            shutil.rmtree(directory)
