# -*- coding: utf-8 -*-

"""Console script for StegTest."""
import sys
import subprocess
import os
import click

import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs

import stegtest.db.downloader as dl 
import stegtest.db.processor as pr

import stegtest.algo.algorithm as algo
import stegtest.algo.config_processor as config_processor

from stegtest.orchestrator import Embeddor, Detector

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
@click.option('-c', '--config', help='path to config file', type=str)
@click.option('-d', '--directory', help='path to a directory of config files', type=str)
@click.pass_context
def add_config(ctx, config, directory):
    """adds stegtest configuration"""
    assert(config or directory)
    if config:
        config_processor.process_config_file(config)
    if directory:
        config_processor.process_config_directory(directory)

@pipeline.command()
@click.pass_context
def initialize(ctx):
    """initializes stegtest configurations"""
    directory = os.getcwd()
    lookup.initialize_filesystem(directory)

#TODO downloads a certain database to a specific directory. Renames files. Adds some sort of metadata list a .txt file at the top. Adds 
@pipeline.command()
@click.option('-n', '--name', help='specify a pre-loaded download routine', type=click.Choice(dl.get_download_routines().keys()))
@click.option('-f', '--file', help='specify a properly-formatted file (<img_name, img_url, *args> for each row) to download from')
@click.option('-db', '--db', help='specify the name of the db if you want to override the default')
@click.pass_context
def download(ctx, name, file, db):
    """downloads a specified database"""
    assert ((name and not file) or (file and not name))
    if name:
        dl.download_routine(name)
    else:
        dl.download_from_file(file, db)

#TODO downloads a certain database to a specific directory. Renames files. Adds some sort of metadata list a .txt file at the top. Adds 
@pipeline.command()
@click.option('-d', '--directory', help='specify an already downloaded database')
@click.option('-n', '--name', help='specify the name for the database')
@click.option('-o', '--operation', help='applies specified operation to all images', type=click.Choice(lookup.get_image_operations()))
@click.pass_context
def process(ctx, directory, name, operation):
    """processes a specified database. select small for faster analysis speeds (512x512 images)"""
    assert(directory and name)
    db_uuid = pr.process_image_directory(directory, name, operation, None)
    click.echo('The UUID of the dataset you have processed is: ' + db_uuid)

@pipeline.command()
@click.option('-a', '--algorithm', help='specify an embedding routine by uuid', type=str)
@click.option('-n', '--new', help='set new for a new embeddor set', is_flag=True, default=False)
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
@click.option('-a', '--algorithm', type=str)
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

        db_info = lookup.get_all_dbs()
        source_db = list(filter(lambda d: len(d.keys()) == len(lookup.db_header), db_info))
        steganographic_db = list(filter(lambda d: len(d.keys()) == len(lookup.steganographic_header), db_info))

        click.echo('Source Databases processed: (' + str(len(source_db)) + ')')
        for db in source_db: 
            click.echo('\t' + str(db[lookup.db_descriptor]))
            click.echo('\t\t' + 'UUID: ' + str(db[lookup.uuid_descriptor]))
            click.echo('\t\t' + 'Image Count: ' + str(db[lookup.db_image_count]))
            click.echo('\t\t' + 'Image Types: ' + str(db[lookup.compatible_descriptor]))
        click.echo(breaker)

        click.echo('Steganographic Databases processed: (' + str(len(steganographic_db)) + ')')
        for db in steganographic_db: 
            click.echo('\t' + 'UUID: ' + str(db[lookup.uuid_descriptor]))
            click.echo('\t\t' + 'Source DB: ' + str(db[lookup.source_db]))
            click.echo('\t\t' + 'Source Embeddor Set: ' + str(db[lookup.source_embeddor_set]))
            click.echo('\t\t' + 'Image Types: ' + str(db[lookup.compatible_descriptor]))
        click.echo(breaker)

    if all or embeddor:
        click.echo(breaker)
        embeddor_info = algo.get_all_algorithms(lookup.embeddor)
        click.echo('Embeddors available: (' + str(len(embeddor_info)) + ')')
        for embeddor in embeddor_info:
            click.echo('\t' + str(embeddor[lookup.name_descriptor]))
            click.echo('\t\t' + 'UUID: ' + str(embeddor[lookup.uuid_descriptor]))
            click.echo('\t\t' + 'Compatible Types: ' + str(embeddor[lookup.compatible_descriptor]))
            click.echo('\t\t' + 'Maximum Embedding Ratio: ' + str(embeddor[lookup.embedding_descriptor]))
            click.echo('\t\t' + 'Command Type: ' + str(embeddor[lookup.COMMAND_TYPE]))
        click.echo(breaker)

        embeddor_set_info = algo.get_all_algorithm_sets(lookup.embeddor)
        click.echo('Embeddor sets available: (' + str(len(embeddor_set_info)) + ')')
        for embeddor_set in embeddor_set_info:
            click.echo('\tUUID: ' + embeddor_set[lookup.uuid_descriptor])
            click.echo('\t\t' + 'Compatible Types: ' + str(embeddor_set[lookup.compatible_descriptor]))
            click.echo('\t\t' + 'Maximum Embedding Ratio: ' + str(embeddor_set[lookup.embedding_descriptor]))
            click.echo('\t\t' + 'Embeddors: ' + str(len(embeddor_set[lookup.embeddor])))
            for embeddor in embeddor_set[lookup.embeddor]:
                click.echo('\t\t\t' + '(' + embeddor[lookup.name_descriptor] + ', ' + embeddor[lookup.uuid_descriptor] + ')')
        click.echo(breaker)

    if all or detector:
        click.echo(breaker)
        detector_info = algo.get_all_algorithms(lookup.detector)
        click.echo('Detectors available: (' + str(len(detector_info)) + ')')
        for detector in detector_info:
            click.echo('\t' + str(detector[lookup.name_descriptor]))
            click.echo('\t\t' + 'UUID: ' + str(detector[lookup.uuid_descriptor]))
            click.echo('\t\t' + 'Compatible Types: ' + str(detector[lookup.compatible_descriptor]))
            click.echo('\t\t' + 'Command Type: ' + str(detector[lookup.COMMAND_TYPE]))
        click.echo(breaker)

        detector_set_info = algo.get_all_algorithm_sets(lookup.detector)
        click.echo('Detector sets available: (' + str(len(detector_set_info)) + ')')
        for detector_set in detector_set_info:
            click.echo('\tUUID: ' + detector_set[lookup.uuid_descriptor])
            click.echo('\t\t' + 'Compatible Types: ' + str(detector_set[lookup.compatible_descriptor]))
            click.echo('\t\t' + 'Detectors: ' + str(len(detector_set[lookup.detector])))
            for detector in detector_set[lookup.detector]:
                click.echo('\t\t\t' + '(' + detector[lookup.name_descriptor] + ', ' + detector[lookup.uuid_descriptor] + ')')
        click.echo(breaker)
    
    click.echo(breaker)
    click.echo('All information printed.')

@pipeline.command()
@click.option('-e', '--embeddor', help='uuid of the embeddor set being used', type=str)
@click.option('-d', '--db', help=' uuid of the db being used', type=str)
@click.option('-r', '--ratio', help='embedding ratio to be used', type=float)
@click.pass_context
def embed(ctx, embeddor, db, ratio):
    """Embeds a db using embeddors and db images"""
    assert(embeddor and db and ratio) 
    embeddor_set = algo.get_algorithm_set(lookup.embeddor, embeddor)
    generator = Embeddor(embeddor_set)
    db_uuid = generator.embed_ratio(db, ratio)
    click.echo('The UUID of the dataset you have created is: ' + db_uuid)

@pipeline.command()
@click.option('-d', '--detector', help='uuid of the detector set being used')
@click.option('-db', '--db', help='hash of the generated db set being used')
@click.pass_context
def detect(ctx, detector, db):
    """analyzes a set detectors using a pre-processed database"""
    assert(detector and db)
    detector_set = algo.lookup_algorithm_set(lookup.detector, detector)
    analyzer = Detector(detector_set)

    output_file_path = analyzer.analyze(db, write_results=True)
    click.echo('The results can be found here: ' + output_file_path)

# @pipeline.command()
# @click.option('-e', '--embeddor', help='uuid of the embeddor being used', type=str)
# @click.option('-m', '--message', help='message to send the embeddor', type=str)
# @click.option('-i', '--input', help='path to image file')
# @click.option('-o', '--output', help='path to output file')
# @click.pass_context
# def embedImage(ctx, embeddor, message, input, output):
#     """Embeds a specific image using an embeddor"""
#     assert(embeddor and fs.file_exists(input) and output)

#     click.echo('Retrieving embeddor...')
#     algorithm_info = algo.get_algorithm_info(lookup.embeddor, embeddor)

#     click.echo('Embedding image...')
#     params = {
#         lookup.SECRET_TXT_PLAINTEXT: message,
#         lookup.INPUT_IMAGE_PATH: input,
#         lookup.OUTPUT_IMAGE_PATH: output,
#     }
#     algo.embed(lookup.SINGLE, algorithm_info, params)

# @pipeline.command()
# @click.option('-d', '--detector', help='uuid of the detector being used', type=str)
# @click.option('-i', '--image', help='path to image file')
# @click.pass_context
# def detectImage(ctx, detector, image):
#     """Detects a specific image using a detector"""
#     algorithm_parameters = algo.get_algorithm_info(lookup.detector, detector, params_only=True)
#     parameter_values = None

#     if algorithm_parameters:
#         parameters = request_parameters(algorithm_parameters)
#         parameter_values = list(parameters.values())
    
#     click.echo('Initializing detector...')
#     instance = algo.instantiate_algorithm(lookup.detector, detector, parameter_values)
#     click.echo('Analyzing image...')
#     result = instance.detect(image)
#     click.echo('The detector has found the following result: ' + str(result))

def main():
    pipeline(obj={})