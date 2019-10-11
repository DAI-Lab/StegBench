# -*- coding: utf-8 -*-

"""Console script for StegTest."""
import sys
import os
import click

import stegtest.utils.bindings as bd
import stegtest.utils.download as dl 
import stegtest.utils.processor as pr
import stegtest.utils.filesystem as fs

from stegtest.scheduler import Scheduler

# from stegtest.utils.filesystem import write_to_file

@click.group()
@click.pass_context
def pipeline(ctx):
    pass


@pipeline.command()
@click.pass_context
def start(ctx):
    """starts docker image"""
    raise NotImplementedError

@pipeline.command()
@click.option('-d', '--directory', help='directory to initalize stegtest files in', type=str, )
@click.pass_context
def initialize(ctx, directory):
    """initializes stegtest filesystem"""
    if directory is not None:
        cwd = directory
    else:
        cwd = os.getcwd()

    Scheduler._initializeFS(cwd)

#TODO downloads a certain database to a specific directory. Renames files. Adds some sort of metadata list a .txt file at the top. Adds 
@pipeline.command()
@click.option('-n', '--name', help='specify a pre-loaded download routine', type=click.Choice(dl.get_download_routines().keys()))
@click.option('-f', '--file', help='specify a properly-formatted file (<img_name, img_url, *args> for each row) to download from')
@click.pass_context
def download(ctx, name, file):
    """downloads a specified database"""
    assert ((name and not file) or (file and not name))
    if name:
        dl.download_routine(name)
    else:
        dl.download_from_file(file)

#TODO downloads a certain database to a specific directory. Renames files. Adds some sort of metadata list a .txt file at the top. Adds 
@pipeline.command()
@click.option('-d', '--directory', help='specify an already downloaded database')
@click.option('-n', '--name', help='specify the name for the database')
@click.pass_context
def process(ctx, directory, name):
    """processes a specified database"""
    assert(directory and name)
    pr.process_directory(directory, name)

@pipeline.command()
@click.option('-a', '--algorithm', help='specify an embedding routine', type=click.Choice(bd.get_embed_routines()))
@click.option('-w', '--weight', help='weight indicates embeddors weight for db generation', type=float)
@click.option('--new/--old', help='set new for new embedding sets', default=False, )
@click.option('-h', '-hash', help='specifies an existing embeddor set')
@click.pass_context
def add_embeddor(ctx, algorithm, weight, new, hash):
    """adds embeddor"""
    assert(new or hash)
    if new:
        file = fs.get_last_file(bd.embeddor)
    else:
        file = fs.get_file_from_hash(bd.embeddor, hash)

    click.echo('Adding embeddor: [' + algorithm + ']' ' with options -- weight:[' + str(weight) + ']')

    fs.write_to_file('embeddor', file, (algorithm, weight))
    file_hash = fs.get_hash_of_file(file)

    click.echo('Added embeddor to file with hash' + str(file_hash))

@pipeline.command()
@click.option('--algorithm', type=click.Choice(['StegDetect', 'StegExpose', 'YeNet']))
@click.pass_context
def add_detector(ctx, algorithm):
    """adds detector"""
    click.echo('Adding detector: [' + algorithm + ']')@pipeline.command()

@pipeline.command()
@click.pass_context
def info(ctx):
    """provides system info"""
    #print the master.txt files in each of the subdirectories in a easy to read way
    pass

@pipeline.command()
@click.pass_context
def reset(ctx):
    """cleans up system"""
    top_level_directories = bd.get_top_level_directories().values()
    fs.clean_filesystem(top_level_directories)

@pipeline.command()
@click.option('-e', '--embeddor', help='hash of the embeddor set being used')
@click.option('-db', '--db', help='hash of the db set being used')
@click.pass_context
def generate(ctx, embeddor, db):
    """Generates a test db using embeddors and db images"""
    #FOR NOW, max make make our datasets 10,000 images. 
    #assert() something about number of embeddor
    #this needs to be an orchestrator for some sort of parallelization parameter
    click.echo('Here is information on the db that was just generated')

@pipeline.command()
@click.option('-d', '--detector', help='hash of the detector set being used')
@click.option('-db', '--db', help='hash of the generated db set being used')
@click.option('-o', '--output', help='output file to output results to')
@click.pass_context
def analyze(ctx, detector, db, output):
    """analyzes a set of detectors on a specified database producing """
    #assert() something about number of detectors
    #should produce some sort of csv with statistics about each of the detectors
    click.echo('Analyzing steganalyzers')

def main():
    pipeline(obj={})