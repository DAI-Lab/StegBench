"""Filesystem utility functions."""
import configparser
import csv
import errno
import json
import os
import shutil
import uuid
from os import path


def get_directory(file_path):
    return path.dirname(file_path)


def get_filename(file_path, extension=True):
    if extension:
        return path.basename(file_path)
    else:
        filename, _ = path.splitext(path.basename(file_path))
        return filename


def change_extension(file_path, new_extension):
    filename, _ = path.splitext(file_path)
    return filename + '.' + new_extension


def get_extension(file_path):
    filename, file_extension = path.splitext(file_path)
    return file_extension


def get_uuid():
    return str(uuid.uuid4())


def create_name_from_uuid(uuid: str, file_type: str):
    return uuid + '.' + file_type


def dir_exists(directory):
    return path.isdir(directory)


def file_exists(file):
    return path.exists(file)


def make_file(path):
    """Creates file if it does not exist."""
    if not file_exists(path):
        with open(path, 'w'):
            pass


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
            text_file.write(str(row))
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
        assert(len(row) == len(header))  # have to be the same to match properly

        row_dict = {}
        for i in range(len(row)):
            row_dict[header[i]] = row[i]

        data_to_dict.append(row_dict)

    return data_to_dict


def read_txt_file(path_to_file):
    with open(path_to_file) as in_file:
        lines = in_file.readlines()

    return lines


def read_csv_file(path_to_file, return_as_dict=False):
    with open(path_to_file, 'r') as in_file:
        reader = csv.reader(in_file)
        rows = [list(row) for row in reader]

    in_file.close()

    if return_as_dict:
        return convert_csv_to_dict(rows)

    return rows


def read_config_file(path_to_file):
    config = configparser.ConfigParser()
    config.read(path_to_file)

    config_to_dict = {s: dict(config.items(s)) for s in config.sections()}
    return config_to_dict


def read_json_file(path_to_file):
    with open(path_to_file, 'r') as in_file:
        datastore = json.load(in_file)

    in_file.close()

    return datastore


def copy_file(file, dest):
    shutil.copy(file, dest)


def remove_file(file):
    if not file_exists(file):
        print('file does not exist')
        return

    os.remove(file)


def remove_directory(directory):
    if not dir_exists(directory):
        print('directory does not exist')
        return

    shutil.rmtree(directory)


def clean_filesystem(directories):
    """removes directories defined in bindings"""
    for directory in directories:
        remove_directory(directory)
