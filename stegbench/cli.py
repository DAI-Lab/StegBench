# -*- coding: utf-8 -*-

"""Console script for StegTest."""
import sys
import subprocess
import os
import collections
import click

import stegbench.utils.lookup as lookup
import stegbench.utils.filesystem as fs

import stegbench.db.downloader as dl 
import stegbench.db.images as img
import stegbench.db.processor as pr

import stegbench.algo.algo_info as algo
import stegbench.algo.algo_processor as algo_processor
import stegbench.algo.robust as robust

from os.path import isfile, join, abspath, relpath

from stegbench.orchestrator import Embeddor, Detector, Verifier, Scheduler

import stegbench as steg

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
    """adds stegbench configuration"""
    steg.add_config(config, directory)

@pipeline.command()
@click.pass_context
def initialize(ctx):
    """initializes stegbench configurations"""
    steg.initialize()

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

    steg.download(routine, name, operation_dict, metadata_dict)

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

    steg.process(directory, name, operation_dict, metadata_dict)

@pipeline.command()
@click.option('-e', '--embeddor', help='specify an embedding routine(s) by uuid', type=str, multiple=True)
@click.option('-u', '--uuid', help='specifies an existing embeddor set')
@click.pass_context
def add_embeddor(ctx, embeddor, uuid):
    """adds to or creates a new embeddor set"""
    assert(embeddor)
    steg.add_embeddor(embeddor, uuid)

@pipeline.command()
@click.option('-d', '--detector', help='specify an detecting routine(s) by uuid', type=str, multiple=True)
@click.option('-u', '--uuid', help='specifies an existing embeddor set')
@click.pass_context
def add_detector(ctx, detector, uuid):
    """adds to or creates a new detector set"""
    assert(detector)
    steg.add_detector(detector, uuid)

@pipeline.command()
@click.option('-a', '--all', help='shows all available information', is_flag=True, default=False)
@click.option('-db', '--database', help='database info', is_flag=True, default=False)
@click.option('-e', '--embeddor', help='embeddor info', is_flag=True, default=False)
@click.option('-d', '--detector', help='detector info', is_flag=True, default=False)
@click.pass_context
def info(ctx, all, database, embeddor, detector):
    """provides system info"""
    steg.info(all, database, embeddor, detector)

@pipeline.command()
@click.option('-e', '--embeddor', help='uuid of the embeddor set being used', type=str)
@click.option('-db', '--database', help=' uuid of the db being used', type=str)
@click.option('-r', '--ratio', help='embedding ratio to be used', type=float)
@click.option('-n', '--name', help='name of the generated database', type=str)
@click.pass_context
def embed(ctx, embeddor, database, ratio, name):
    """Embeds a db using embeddors and db images"""
    assert(embeddor and database and ratio and name) 
    steg.embed(embeddor, database, ratio, name)

@pipeline.command()
@click.option('-d', '--detector', help='uuid of the detector set being used')
@click.option('-db', '--database', help='uuid of the db or db set being used', multiple=True)
@click.pass_context
def detect(ctx, detector, database):
    """analyzes a set detectors using a pre-processed database"""
    assert(detector and database)
    steg.detect(detector, database)

@pipeline.command()
@click.option('-db', '--database', help='uuid of the db to verify')
@click.pass_context
def verify(ctx, database):
    """verifies a steganographic database"""
    assert(database)
    steg.verify(database)

@pipeline.command()
@click.option('-p', '--path', help='path to experiment file')
@click.option('-db', '--database', help='uuid of the source db(s) to run experiment on', multiple=True)
@click.pass_context
def run_experiment(ctx, path, database):
    """runs pipelines specified in experiment configuration file"""
    assert(path)
    steg.run_experiment(path, database)

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

    steg.adv_attack(model, database, configurations)

@pipeline.command()
@click.option('-db', '--database', help='uuid of the stego db(s) to work with',  multiple=True)
@click.option('-o', '--output', help='name of output file', default='labels.csv')
@click.option('-r', '--relative', help='requires relative path in file', is_flag=True, default=False)
@click.pass_context
def generate_labels(ctx, database, output, relative):
    """generates labels.csv file for a set of databases"""
    steg.generate_labels(database, output, relative)

def main():
    pipeline(obj={})
