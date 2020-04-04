# -*- coding: utf-8 -*-

"""Console script for StegTest."""
import sys
import subprocess
import os
import collections
import click

import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs

import stegtest.db.downloader as dl 
import stegtest.db.images as img
import stegtest.db.processor as pr

import stegtest.algo.algo_info as algo
import stegtest.algo.algo_processor as algo_processor
import stegtest.algo.robust as robust

from os.path import isfile, join, abspath

from stegtest.orchestrator import Embeddor, Detector, Verifier, Scheduler

@click.pass_context
def request_parameters(ctx, parameters):
    parameter_values = {}
    prompt_string = 'Please enter a parameter value for: '
    for parameter_name in parameters.keys():
        value = None
        parameter_type = parameters[parameter_name]

        if isinstance(parameter_type, list):
            click.echo('Enter parameter values for ' +  parameter_name + ' list. To end, press q')
            value = []
            list_type = parameter_type[0]

            list_value = click.prompt(prompt_string + parameter_name, type=str)
            while list_value != 'q':
                value.append(list_type(list_value))
                list_value = click.prompt(prompt_string + parameter_name, type=str)
        elif isinstance(parameter_type, dict):
            get_options = parameter_type.keys()
            value = click.prompt('Select your choice for ' + parameter_name, type=click.Choice(get_options))
            value = parameter_type[value]
        else:
            value = click.prompt(prompt_string + parameter_name, type=parameter_type)

        parameter_values[parameter_name] = value

    if len(parameter_values) == 0:
        return parameter_values

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
@click.option('-c', '--config', help='path to config file', type=str, multiple=True)
@click.option('-d', '--directory', help='path to a directory of config files', type=str, multiple=True)
@click.pass_context
def add_config(ctx, config, directory):
    """adds stegtest configuration"""
    for c in config:
            algo_processor.process_config_file(c)
    for d in directory:
            algo_processor.process_config_directory(d)

@pipeline.command()
@click.pass_context
def initialize(ctx):
    """initializes stegtest configurations"""
    directory = os.getcwd()
    lookup.initialize_filesystem(directory)

@pipeline.command()
@click.option('-r', '--routine', help='specify a pre-loaded download routine', type=click.Choice(dl.get_download_routines().keys()))
@click.option('-n', '--name', help='specify the name for the database')
@click.option('-o', '--operation', help='applies specified operation(s) to all images', type=click.Choice(lookup.get_image_operations()), multiple=True)
@click.option('-m', '--metadata', help='applies metadata or operation to directory', type=click.Choice(lookup.get_directory_operations()), multiple=True)
@click.pass_context
def download(ctx, routine, name, operation, metadata):
    """downloads a specified database"""
    assert(routine and name)
    operation_dict = collections.OrderedDict({})
    metadata_dict = collections.OrderedDict({})
    if operation:
        for op in operation:
            operation_parameters = request_parameters(img.get_operation_args(op))
            operation_dict[op] = list(operation_parameters.values())

    if metadata:
        for dir_op in metadata:
            operation_parameters = {}
            if pr.get_metadata_operation_args(dir_op) is not None:
                operation_parameters = request_parameters(pr.get_metadata_operation_args(dir_op))
                
            metadata_dict[dir_op] = list(operation_parameters.values())

    download_directory = dl.download_routine(routine)
    db_uuid = pr.process_directory(metadata_dict, download_directory, name, operation_dict)
    click.echo('The UUID of the dataset(s) you have processed is: ' + str(db_uuid))

@pipeline.command()
@click.option('-d', '--directory', help='specify an already downloaded database')
@click.option('-n', '--name', help='specify the name for the database')
@click.option('-o', '--operation', help='applies specified operation to each image', type=click.Choice(lookup.get_image_operations()), multiple=True)
@click.option('-m', '--metadata', help='applies metadata or operation to directory', type=click.Choice(lookup.get_directory_operations()), multiple=True)
@click.pass_context
def process(ctx, directory, name, operation, metadata):
    """processes a specified database"""
    assert(directory and name)
    operation_dict = collections.OrderedDict({})
    metadata_dict = collections.OrderedDict({})
    if operation:
        for op in operation:
            operation_parameters = {}
            if img.get_operation_args(op) is not None:
                operation_parameters = request_parameters(img.get_operation_args(op))

            operation_dict[op] = list(operation_parameters.values())

    if metadata:
        for dir_op in metadata:
            operation_parameters = {}
            if pr.get_metadata_operation_args(dir_op) is not None:
                operation_parameters = request_parameters(pr.get_metadata_operation_args(dir_op))
                
            metadata_dict[dir_op] = list(operation_parameters.values())

    db_uuid = pr.process_directory(metadata_dict, directory, name, operation_dict)
    click.echo('The UUID of the dataset(s) you have processed is: ' + str(db_uuid))

@pipeline.command()
@click.option('-e', '--embeddor', help='specify an embedding routine(s) by uuid', type=str, multiple=True)
@click.option('-u', '--uuid', help='specifies an existing embeddor set')
@click.pass_context
def add_embeddor(ctx, embeddor, uuid):
    """adds to or creates a new embeddor set"""
    assert(embeddor)
    click.echo('Adding embeddors: ' + str(embeddor))
    if uuid:
        uuid = algo.add_to_algorithm_set(lookup.embeddor, uuid, embeddor)
        message = 'The UUID of the set you have added to is: '
    else:
        uuid = algo.create_algorithm_set(lookup.embeddor, embeddor)
        message = 'The new UUID of the set you have created is: '

    click.echo('Added embeddor successfully')
    click.echo(message + uuid)

@pipeline.command()
@click.option('-d', '--detector', help='specify an detecting routine(s) by uuid', type=str, multiple=True)
@click.option('-u', '--uuid', help='specifies an existing embeddor set')
@click.pass_context
def add_detector(ctx, detector, uuid):
    """adds to or creates a new detector set"""
    assert(detector)
    click.echo('Adding detectors: ' + str(detector))
    if uuid:
        uuid = algo.add_to_algorithm_set(lookup.detector, uuid, detector)
        message = 'The UUID of the set you have added to is: '
    else:
        uuid = algo.create_algorithm_set(lookup.detector, detector)
        message = 'The new UUID of the set you have created is: '

    click.echo('Added detector successfully')
    click.echo(message + uuid)

@pipeline.command()
@click.option('-a', '--all', help='shows all available information', is_flag=True, default=False)
@click.option('-db', '--database', help='database info', is_flag=True, default=False)
@click.option('-e', '--embeddor', help='embeddor info', is_flag=True, default=False)
@click.option('-d', '--detector', help='detector info', is_flag=True, default=False)
@click.pass_context
def info(ctx, all, database, embeddor, detector):
    """provides system info"""
    #TODO print the master.txt files in each of the subdirectories in a easy to read way
    breaker = ['-' for i in range(100)]
    breaker = ''.join(breaker)
    click.echo('Listing all requested information....')
    click.echo(breaker)

    if all or database:
        click.echo(breaker)
        click.echo('All database information')
        click.echo(breaker)
        click.echo(breaker)

        db_info = lookup.get_all_dbs()
        source_db = list(filter(lambda d: len(d.keys()) == len(lookup.db_header), db_info))
        steganographic_db = list(filter(lambda d: len(d.keys()) == len(lookup.steganographic_header), db_info))

        click.echo('Source Databases processed: (' + str(len(source_db)) + ')')
        for db in source_db: 
            click.echo('\t' + str(db[lookup.db_descriptor]))
            click.echo('\t\t' + 'UUID: ' + str(db[lookup.uuid_descriptor]))
            click.echo('\t\t' + 'Directory path: ' + str(db[lookup.path_descriptor]))
            click.echo('\t\t' + 'Image Count: ' + str(db[lookup.db_image_count]))
            click.echo('\t\t' + 'Image Types: ' + str(db[lookup.compatible_descriptor]))
        click.echo(breaker)

        click.echo('Steganographic Databases processed: (' + str(len(steganographic_db)) + ')')
        for db in steganographic_db: 
            click.echo('\t' + str(db[lookup.db_descriptor]))
            click.echo('\t\t' + 'UUID: ' + str(db[lookup.uuid_descriptor]))
            click.echo('\t\t' + 'Directory path: ' + str(db[lookup.path_descriptor]))
            click.echo('\t\t' + 'Image Count: ' + str(db[lookup.db_image_count]))
            click.echo('\t\t' + 'Image Types: ' + str(db[lookup.compatible_descriptor]))
            click.echo('\t\t' + 'Source DB: ' + str(db[lookup.source_db]))
            click.echo('\t\t' + 'Source Embeddor Set: ' + str(db[lookup.source_embeddor_set]))
            click.echo('\t\t' + 'Payload: ' + str(db[lookup.embedding_ratio]))
        click.echo(breaker)

    if all or embeddor:
        click.echo(breaker)
        click.echo('All embeddor information')
        click.echo(breaker)
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
        click.echo('All detector information')
        click.echo(breaker)
        click.echo(breaker)
        detector_info = algo.get_all_algorithms(lookup.detector)
        binary_detectors = list(filter(lambda d: d[lookup.DETECTOR_TYPE] == lookup.binary_detector, detector_info))
        probability_detectors = list(filter(lambda d: d[lookup.DETECTOR_TYPE] == lookup.probability_detector, detector_info))
        
        click.echo('Binary Detectors available: (' + str(len(binary_detectors)) + ')')
        for detector in binary_detectors:
            click.echo('\t' + str(detector[lookup.name_descriptor]))
            click.echo('\t\t' + 'UUID: ' + str(detector[lookup.uuid_descriptor]))
            click.echo('\t\t' + 'Compatible Types: ' + str(detector[lookup.compatible_descriptor]))
            click.echo('\t\t' + 'Command Type: ' + str(detector[lookup.COMMAND_TYPE]))
        click.echo(breaker)

        click.echo('Probability Detectors available: (' + str(len(probability_detectors)) + ')')
        for detector in probability_detectors:
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
@click.option('-db', '--database', help=' uuid of the db being used', type=str)
@click.option('-r', '--ratio', help='embedding ratio to be used', type=float)
@click.option('-n', '--name', help='name of the generated database', type=str)
@click.pass_context
def embed(ctx, embeddor, database, ratio, name):
    """Embeds a db using embeddors and db images"""
    assert(embeddor and database and ratio and name) 
    embeddor_set = algo.get_algorithm_set(lookup.embeddor, embeddor)
    generator = Embeddor(embeddor_set)
    db_uuid = generator.embed_ratio(name, database, ratio)
    click.echo('The UUID of the dataset you have created is: ' + db_uuid)

@pipeline.command()
@click.option('-d', '--detector', help='uuid of the detector set being used')
@click.option('-db', '--database', help='uuid of the db or db set being used', multiple=True)
@click.pass_context
def detect(ctx, detector, database):
    """analyzes a set detectors using a pre-processed database"""
    assert(detector and database)
    detector_set = algo.get_algorithm_set(lookup.detector, detector)
    analyzer = Detector(detector_set)
    results = analyzer.detect(database)

    breaker = ['-' for i in range(100)]
    breaker = ''.join(breaker)
    small_breaker = ['-' for i in range(75)]
    small_breaker = ''.join(breaker)

    click.echo('Experiment information')
    click.echo(breaker)
    click.echo(breaker)
    for db in database:
        db_info = lookup.get_db_info(db)

        if db_info[lookup.stego]:
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
        else:
            click.echo('Database Information')
            click.echo('\t' + 'UUID: ' + str(db_info[lookup.uuid_descriptor]))
            click.echo('\t\t' + 'Image Types: ' + str(db_info[lookup.compatible_descriptor]))
            click.echo(breaker)

    click.echo(breaker)
    click.echo('Listing all results...')
    click.echo(breaker)

    for detector_uuid in results:
        detector_info = algo.get_algorithm_info(lookup.detector, detector_uuid)
        click.echo('\tName: ' + detector_info[lookup.name_descriptor])
        click.echo('\tDetector Type: ' + detector_info[lookup.DETECTOR_TYPE])
        click.echo('\tUUID: ' + detector_uuid)
        detector_result = results[detector_uuid]

        if detector_info[lookup.DETECTOR_TYPE] == lookup.binary_detector:
            raw_results = detector_result[lookup.result_raw]
            true_positive = raw_results[lookup.true_positive_raw]
            true_negative = raw_results[lookup.true_negative_raw]
            total_stego = raw_results[lookup.total_stego_raw]
            total_cover = raw_results[lookup.total_cover_raw]

            click.echo('\tRaw Results:') #TODO change this when thresholding gets introduced
            click.echo('\t\t(' + str(true_positive)  + '/' + str(total_stego) + ') stego images identified correctly')
            click.echo('\t\t(' + str(true_negative)  + '/' + str(total_cover) + ') cover images identified correctly')
            click.echo('\t\t(' + str(true_positive + true_negative)  + '/' + str(total_stego + total_cover) + ') total images identified correctly')
        
        click.echo('\tMetrics:')

        metric_results = detector_result[lookup.result_metric]
        for metric in metric_results:
            click.echo('\t\t' + metric + ': ' +str(metric_results[metric]))

        click.echo(small_breaker)

    click.echo(breaker)
    click.echo('All results printed.')

@pipeline.command()
@click.option('-db', '--database', help='uuid of the db to verify')
@click.pass_context
def verify(ctx, database):
    """verifies a steganographic database"""
    assert(database)
    verifier = Verifier()
    results = verifier.verify(database)
    
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

@pipeline.command()
@click.option('-p', '--path', help='path to experiment file')
@click.option('-db', '--database', help='uuid of the source db(s) to run experiment on', multiple=True)
@click.pass_context
def run_experiment(ctx, path, database):
    """runs pipelines specified in experiment configuration file"""
    assert(path)
    metadata, embeddor_set_uuid, detector_set_uuid = algo_processor.process_experiment_file(path)
    scheduler = Scheduler(metadata, embeddor_set_uuid, detector_set_uuid)
    results = scheduler.run(database)
    print(results)

@pipeline.command()
@click.option('-m', '--model', help='path of the model', type=str)
@click.option('-db', '--database', help='uuid of the db(s) to work with',  multiple=True)
@click.option('-a', '--attack', help='adversarial attack options', type=click.Choice(lookup.get_attack_methods()))
@click.pass_context
def adv_attack(ctx, model, database, attack):
    """performs an adversarial attack on a predefined model with specific configuration details"""
    assert(fs.file_exists(model))

    configurations = request_parameters(robust.get_model_arguments())
    configurations[lookup.attack_method] = attack
    #load data 
    data = [pr.load_data_as_array(db) for db in database]
    x, y = [], []
    for db in data:
        for (x_t, y_t) in db:
            x.append(x_t)
            y.append(y_t)



    #based of the attack need to get the list of required configuration options 
    dataset = (x, y)
    robust.apply_attack(model, dataset, configurations)

@pipeline.command()
@click.option('-db', '--database', help='uuid of the stego db(s) to work with',  multiple=True)
@click.option('-o', '--output', help='name of output file', default='labels.csv')
@click.option('--absolute', help='absolute path in file', is_flag=True, default=False)
@click.pass_context
def generate_labels(ctx, database, output, absolute):
    """generates labels.csv file for a set of databases"""
    db_image_list = [('cover', 'steganographic')]
    for db in database:
        db_image_dict = lookup.get_image_list(db)
        db_image_list = db_image_list + list(map(lambda img: (img[lookup.source_image], img[lookup.file_path]), db_image_dict))

    path_to_label_file = abspath(join(lookup.get_top_level_dirs()[lookup.db], output))
    fs.write_to_csv_file(path_to_label_file, db_image_list)

    print('The labels file can be found here: ' + path_to_label_file)

def main():
    pipeline(obj={})