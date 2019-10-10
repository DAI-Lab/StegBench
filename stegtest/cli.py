# -*- coding: utf-8 -*-

"""Console script for StegTest."""
import sys
import os
import click

import stegtest.utils.filesystem as fs
from stegtest.scheduler import Scheduler

# from stegtest.utils.filesystem import write_to_file

@click.group()
@click.pass_context
def pipeline(ctx):
    pass

#TODO creates all the relevant directories and files or ensures that they exist. cleans file system for these directories as well#
@pipeline.command()
@click.option('-d', '--directory', help='directory to initalize stegtest files in', type=str, )
@click.pass_context
def initialize(ctx, directory):
    """initializes the directory so stegtest can operate properly"""
    if directory is not None:
        cwd = directory
    else:
        cwd = os.getcwd()

    Scheduler._initializeFS(cwd)

#TODO downloads a certain database to a specific directory. Renames files. Adds some sort of metadata list a .txt file at the top. Adds 
@pipeline.command()
@click.pass_context
def download(ctx):
    click.echo('Downloading the database')

@pipeline.command()
@click.option('-a', '--algorithm', type=click.Choice(['BrokenArrows', 'CloackedPixel', 'F5', 'JpHide', 'JSteg', 'LSB', 'OpenStego', 'Outguess', 'Stegano', 'StegHide', 'StegPy']))
@click.option('-w', '--weight', type=float)
@click.option('--new/--old', default=False)
@click.option('-h', '-hash')
@click.pass_context
def add_embeddor(ctx, algorithm, weight, new, hash):
    assert(new or hash)
    if new:
        file = fs.get_last_file('embeddor')
    else:
        file = fs.get_file_from_hash(hash)

    click.echo('Adding embeddor: [' + algorithm + ']' ' with options -- weight:[' + str(weight) + ']')

    fs.write_to_file('embeddor', file, (algorithm, weight))
    file_hash = fs.get_hash_of_file(file)

    click.echo('Added embeddor to file with hash' + str(file_hash))

@pipeline.command()
@click.option('--algorithm', type=click.Choice(['StegDetect', 'StegExpose', 'YeNet']))
@click.pass_context
def add_detector(ctx, algorithm):
	click.echo('Adding detector: [' + algorithm + ']')

@pipeline.command()
@click.pass_context
def info(ctx):
	pass

@pipeline.command()
@click.pass_context
def reset(ctx):
	pass


@pipeline.command()
@click.argument('hash')
@click.pass_context
def parse_db(ctx):
	click.echo('parsing db for information')

@pipeline.command()
@click.pass_context
def generate(ctx):
	#FOR NOW, max make make our datasets 10,000 images. 
	#assert() something about number of embeddor
	#this needs to be an orchestrator for some sort of parallelization parameter
    click.echo('Here is information on the db that was just generated')

@pipeline.command()
@click.argument('algorithm')
@click.pass_context
def analyze(ctx):
	#assert() something about number of detectors
	#should produce some sort of csv with statistics about each of the detectors
	click.echo('Analyzing steganalyzers')

def main():
	#need a way to dispatch this... lol
	#can use click commands nice.
    pipeline(obj={})