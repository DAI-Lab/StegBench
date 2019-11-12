# -*- coding: utf-8 -*-

"""Console script for StegTest."""
import sys
import subprocess
import os
import click

import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs

import stegtest.db.downloader as dl 
import stegtest.db.images as img
import stegtest.db.processor as pr

import stegtest.algo.algorithm as algo
import stegtest.algo.algo_processor as algo_processor

from stegtest.orchestrator import Embeddor, Detector, Verifier

@click.pass_context
def request_parameters(ctx, parameters):
    parameter_values = {}
    prompt_string = 'Please enter a parameter value for: '

    for parameter_name in parameters.keys():
        parameter_type = parameters[parameter_name]
        value = click.prompt(prompt_string + parameter_name, type=parameter_type)
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
        algo_processor.process_config_file(config)
    if directory:
        algo_processor.process_config_directory(directory)

@pipeline.command()
@click.pass_context
def initialize(ctx):
    """initializes stegtest configurations"""
    directory = os.getcwd()
    lookup.initialize_filesystem(directory)

@pipeline.command()
@click.option('-r', '--routine', help='specify a pre-loaded download routine', type=click.Choice(dl.get_download_routines().keys()))
@click.option('-n', '--name', help='specify the name for the database')
@click.option('-o', '--operation', help='applies specified operation to all images', type=click.Choice(lookup.get_image_operations()))
@click.pass_context
def download(ctx, routine, name, operation):
    """downloads a specified database"""
    assert(routine)
    operation_parameters = None
    if operation:
        operation_parameters = request_parameters(img.get_operation_args(operation))
        operation_parameters = list(operation_parameters.values())

    download_directory = dl.download_routine(routine)
    db_uuid = pr.process_image_directory(download_directory, name, operation, operation_parameters)
    click.echo('The UUID of the dataset you have processed is: ' + db_uuid)

@pipeline.command()
@click.option('-d', '--directory', help='specify an already downloaded database')
@click.option('-n', '--name', help='specify the name for the database')
@click.option('-o', '--operation', help='applies specified operation to all images', type=click.Choice(lookup.get_image_operations()))
@click.pass_context
def process(ctx, directory, name, operation):
    """processes a specified database. select small for faster analysis speeds (512x512 images)"""
    assert(directory and name)
    if operation:
        operation_parameters = request_parameters(img.get_operation_args(operation))
        db_uuid = pr.process_image_directory(directory, name, operation, list(operation_parameters.values()))
    else:
        db_uuid = pr.process_image_directory(directory, name)
    click.echo('The UUID of the dataset you have processed is: ' + db_uuid)

@pipeline.command()
@click.option('-e', '--embeddor', help='specify an embedding routine(s) by uuid', type=str)
@click.option('-n', '--new', help='set new for a new embeddor set', is_flag=True, default=False)
@click.option('-u', '--uuid', help='specifies an existing embeddor set')
@click.pass_context
def add_embeddor(ctx, embeddor, new, uuid):
    """adds embeddor with options <algorithm> and <weight>"""
    assert(embeddor and (new or uuid))
    embeddor = embeddor.split(',')
    click.echo('Adding embeddors: ' + str(embeddor))
    if new:
        uuid = algo.create_algorithm_set(lookup.embeddor, embeddor)
        message = 'The new UUID of the set you have created is: '
    else:
        uuid = algo.add_to_algorithm_set(lookup.embeddor, uuid, embeddor)
        message = 'The UUID of the set you have added to is: '

    click.echo('Added embeddor successfully')
    click.echo(message + uuid)

@pipeline.command()
@click.option('-d', '--detector', help='specify an detecting routine(s) by uuid', type=str)
@click.option('-n', '--new', help='set new for a new detector set', is_flag=True, default=False, )
@click.option('-u', '--uuid', help='specifies an existing embeddor set')
@click.pass_context
def add_detector(ctx, detector, new, uuid):
    """adds detector with options <algorithm> and <weight>"""
    assert(detector and (new or uuid))
    detector = detector.split(',')
    click.echo('Adding detectors: ' + str(detector))
    if new:
        uuid = algo.create_algorithm_set(lookup.detector, detector)
        message = 'The new UUID of the set you have created is: '
    else:
        uuid = algo.add_to_algorithm_set(lookup.detector, uuid, detector)
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
            click.echo('\t\t' + 'Payload: ' + str(db[lookup.embedding_ratio]))
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
@click.option('-db', '--db', help=' uuid of the db being used', type=str)
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
@click.option('-db', '--db', help='uuid of the db being used')
@click.pass_context
def detect(ctx, detector, db):
    """analyzes a set detectors using a pre-processed database"""
    assert(detector and db)
    detector_set = algo.get_algorithm_set(lookup.detector, detector)
    analyzer = Detector(detector_set)
    results = analyzer.detect(db)

    db_info = lookup.get_steganographic_db_info(db)

    breaker = ['-' for i in range(100)]
    breaker = ''.join(breaker)
    click.echo('Experiment information')
    click.echo(breaker)
    click.echo(breaker)
    click.echo('Database Information')
    click.echo('\t' + 'UUID: ' + str(db_info[lookup.uuid_descriptor]))
    click.echo('\t\t' + 'Source DB: ' + str(db_info[lookup.source_db]))
    click.echo('\t\t' + 'Source Embeddor Set: ' + str(db_info[lookup.source_embeddor_set]))
    click.echo('\t\t' + 'Image Types: ' + str(db_info[lookup.compatible_descriptor]))
    click.echo('\t\t' + 'Payload: ' + str(db_info[lookup.embedding_ratio]))
    click.echo(breaker)

    click.echo('Embeddor Set Information')
    embeddor_set = algo.get_algorithm_set(lookup.embeddor, str(db_info[lookup.source_embeddor_set]))
    click.echo('\tUUID: ' + embeddor_set[lookup.uuid_descriptor])
    click.echo('\t\t' + 'Compatible Types: ' + str(embeddor_set[lookup.compatible_descriptor]))
    click.echo('\t\t' + 'Embeddors: ' + str(len(embeddor_set[lookup.embeddor])))
    for embeddor in embeddor_set[lookup.embeddor]:
        click.echo('\t\t\t' + '(' + embeddor[lookup.name_descriptor] + ', ' + embeddor[lookup.uuid_descriptor] + ')')
    click.echo(breaker)

    click.echo(breaker)
    click.echo('Listing all results...')
    click.echo(breaker)

    for detector_uuid in results:
        detector_info = algo.get_algorithm_info(lookup.detector, detector_uuid)
        click.echo('\tName: ' + detector_info[lookup.name_descriptor])
        click.echo('\tUUID: ' + detector_uuid)
        detector_result = results[detector_uuid]
        for metric in detector_result:
            click.echo('\t\t' + metric + ': ' +str(detector_result[metric]))

    click.echo(breaker)
    click.echo('All results printed.')

@pipeline.command()
@click.option('-db', '--db', help='uuid of the db to veriy')
@click.pass_context
def verify(ctx, db):
    """verifies a steganographic database"""
    assert(db)
    verifier = Verifier()
    results = verifier.verify(db)
    
    verified_total = 0
    error_total = 0

    breaker = ['-' for i in range(100)]
    breaker = ''.join(breaker)
    click.echo('Listing all verification results...')
    click.echo(breaker)
    click.echo('Specific Embeddor Results')
    for embeddor_uuid in results:
        embeddor_result = results[embeddor_uuid]
        embeddor_info = algo.get_algorithm_info(lookup.embeddor, embeddor_uuid)
        click.echo('\tName: ' + embeddor_info[lookup.name_descriptor])
        click.echo('\tUUID: ' + embeddor_uuid)
        
        verified = len(list(filter(lambda r: r[lookup.result], embeddor_result)))
        errors = len(list(filter(lambda r: not r[lookup.result], embeddor_result)))

        click.echo('\t\tCorrectly Embedded (%): ' + str(100*(float(verified)/float(verified + errors))))     
        click.echo('\t\tIncorrect Embedding (%): ' + str(100*(float(errors)/float(verified + errors))))

        verified_total += verified
        error_total += errors  

    click.echo(breaker)
    click.echo('Total Results')
    click.echo('\tCorrectly Embedded (%): ' + str(100*(float(verified_total)/float(verified_total + error_total))))
    click.echo('\tIncorrect Embedding (%): ' + str(100*(float(error_total)/float(verified_total + error_total))))


def main():
    pipeline(obj={})