# -*- coding: utf-8 -*-

"""Console script for StegTest."""
import sys
import subprocess
import os
import click

import stegtest.utils.lookup as lookup
import stegtest.utils.downloader as dl 
import stegtest.utils.processor as pr
import stegtest.utils.filesystem as fs
import stegtest.utils.algorithm as algo

from stegtest.scheduler import Scheduler

@click.pass_context
def request_parameters(ctx, parameters):
    parameter_values = {}
    prompt_string = 'Please enter a parameter value for: '

    for parameter_name in parameters.keys():
        parameter_type = parameters[parameter_name]
        click_type = lookup.get_parameter_type(parameter_type)

        value = click.prompt(prompt_string + parameter_name, type=click_type)
        parameter_values[parameter_name] = value

    click.echo('\nYou have set the following parameters: ' + str(parameter_values))

    if click.confirm('Do you want to continue?'):
        click.echo('continuing!')
        return parameter_values

    ctx.abort()

@click.group()
@click.pass_context
def pipeline(ctx):
    pass

@pipeline.command()
@click.pass_context
def start(ctx):
    """starts docker image"""
    build_command = ['bin/build.sh']
    run_command = ['bin/run.sh']
    subprocess.run(build_command)
    subprocess.run(run_command)

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
    pr.process_image_directory(directory, name)

@pipeline.command()
@click.option('-a', '--algorithm', help='specify an embedding routine', type=click.Choice(algo.get_algorithm_names(lookup.embeddor)))
# @click.option('-w', '--weight', help='weight indicates embeddors weight for db generation', type=float) #TODO for v1.
@click.option('-n', '--new', help='set new for a new embeddor set', is_flag=True, default=False, )
@click.option('-u', '--uuid', help='specifies an existing embeddor set')
@click.pass_context
def add_embeddor(ctx, algorithm, new, uuid):
    """adds embeddor with options <algorithm> and <weight>"""
    assert(algorithm and (new or uuid))
    click.echo('Adding embeddor: [' + algorithm + ']')
    if new:
        uuid = algo.create_algorithm_set(lookup.embeddor, algorithm)
        message = 'The new UUID of the set you have created is: '
    else:
        uuid = algo.add_to_algorithm_set(lookup.embeddor, uuid, algorithm)
        message = 'The UUID of the set you have added to is: '

    click.echo('Added embeddor successfully')
    click.echo(message + uuid)

@pipeline.command()
@click.option('-a', '--algorithm', type=click.Choice(algo.get_algorithm_names(lookup.detector)))
@click.option('-n', '--new', help='set new for a new detector set', is_flag=True, default=False, )
@click.option('-u', '--uuid', help='specifies an existing embeddor set')
@click.pass_context
def add_detector(ctx, algorithm, new, uuid):
    """adds detector with options <algorithm> and <weight>"""
    assert(algorithm and (new or uuid))
    click.echo('Adding detector: [' + algorithm + ']')
    if new:
        uuid = algo.create_algorithm_set(lookup.detector, algorithm)
        message = 'The new UUID of the set you have created is: '
    else:
        uuid = algo.add_to_algorithm_set(lookup.detector, uuid, algorithm)
        message = 'The UUID of the set you have added to is: '

    click.echo('Added detector successfully')
    click.echo(message + uuid)

@pipeline.command()
@click.option('-a', '--all', help='shows all available information', is_flag=True, default=False)
@click.option('-db', '--db', help='database info', is_flag=True, default=False)
@click.option('-e', '--embeddor', help='embeddor info', is_flag=True, default=False)
@click.option('-d', '--detector', help='detector info', is_flag=True, default=False)
@click.pass_context
def info(ctx, all, db, embeddor, detector):
    """provides system info"""
    #TODO print the master.txt files in each of the subdirectories in a easy to read way
    breaker = ['-' for i in range(100)]
    breaker = ''.join(breaker)
    click.echo('Listing all requested information....')
    click.echo(breaker)

    if all or db:
        click.echo(breaker)
        click.echo('Databases processed: ')
        db_info = lookup.get_db_names()
        for db in db_info:
            click.echo('\t' + str(db))
        click.echo(breaker)

    if all or embeddor:
        click.echo(breaker)
        click.echo('Embeddors available: ')
        embeddor_info = algo.get_all_algorithms(lookup.embeddor)
        for embeddor in embeddor_info:
            click.echo('\t' + str(embeddor[lookup.algorithm_name]))
            click.echo('\t\t' + ' Description: ' + str(embeddor[lookup.description]))
            click.echo('\t\t' + ' Compatible Types: ' + str(embeddor[lookup.compatibile_types_decorator]))
        click.echo(breaker)

        click.echo('Embeddor sets available: ')
        embeddor_set_info = algo.get_all_algorithm_sets(lookup.embeddor)
        for uuid in embeddor_set_info.keys():
            embeddor_set = embeddor_set_info[uuid]
            click.echo('\tUUID: ' + uuid)
            click.echo('\t\t' + ' Compatible Types: ' + str(embeddor_set[lookup.compatibile_types_decorator]))
            click.echo('\t\t' + ' Embeddors: ' + str(embeddor_set[lookup.embeddor]))
        click.echo(breaker)

    if all or detector:
        click.echo(breaker)
        click.echo('Detectors available: ')
        detector_info = algo.get_all_algorithms(lookup.detector)
        for detector in detector_info:
            click.echo('\t' + str(detector[lookup.algorithm_name]))
            click.echo('\t\t' + ' Description: ' + str(detector[lookup.description]))
            click.echo('\t\t' + ' Compatible Types: ' + str(detector[lookup.compatibile_types_decorator]))
        click.echo(breaker)

        click.echo('Detector sets available: ')
        detector_set_info = algo.get_all_algorithm_sets(lookup.detector)
        for uuid in detector_set_info.keys():
            detector_set = detector_set_info[uuid]
            click.echo('\tUUID: ' + uuid)
            click.echo('\t\t' + ' Compatible Types: ' + str(detector_set[lookup.compatibile_types_decorator]))
            click.echo('\t\t' + ' Detectors: ' + str(detector_set[lookup.detector]))
        click.echo(breaker)
    
    click.echo(breaker)
    click.echo('All information printed.')

@pipeline.command()
@click.pass_context
def reset(ctx):
    """cleans up system"""
    top_level_directories = lookup.get_top_level_directories().values()
    fs.clean_filesystem(top_level_directories)

@pipeline.command()
@click.option('-e', '--embeddor', help='uuid of the embeddor set being used')
@click.option('-db', '--db', help='name or uuid of the db being used')
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

@pipeline.command()
@click.option('-e', '--embeddor', help='name of the embeddor being used', type=click.Choice(algo.get_algorithm_names(lookup.embeddor)))
@click.option('-i', '--input', help='path to image file')
@click.option('-o', '--output', help='path to output file')
@click.pass_context
def embedImage(ctx, embeddor, input, output):
    """Embeds a specific image using an embeddor"""
    algorithm_parameters = algo.get_algorithm_info(lookup.embeddor, embeddor, params_only=True)

    if algorithm_parameters:
        parameters = request_parameters(algorithm_parameters)
    
    click.echo('Creating the embeddor')
    parameter_values = list(parameters.values())
    instance = algo.instantiate_algorithm(lookup.embeddor, embeddor, parameter_values)

    instance.embed(input, output)

@pipeline.command()
@click.option('-d', '--detector', help='name of the detector being used', type=click.Choice(algo.get_algorithm_names(lookup.detector)))
@click.option('-i', '--image', help='path to image file')
@click.pass_context
def detectImage(ctx, detector, image):
    """Detects a specific image using a detector"""
    algorithm_parameters = algo.get_algorithm_info(lookup.detector, detector, params_only=True)

    if algorithm_parameters:
        parameters = request_parameters(algorithm_parameters)
    
    click.echo('Creating the detector')
    parameter_values = list(parameters.values())
    instance = algo.instantiate_algorithm(lookup.detector, detector, parameter_values)

    instance.detect(image)

def main():
    pipeline(obj={})