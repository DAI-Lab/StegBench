# -*- coding: utf-8 -*-

"""Console script for StegTest."""
import sys
import click

@click.group()
def setup():
	pass

"""NEEEDS TO BE IN ITS OWN CLASS OF THINGS"""
@click.command()
def download():
    click.echo('Downloading the database')

@click.command()
@click.option('-a', '--algorithm')
def add_embedder():
	click.echo('Adding an embedder...')

@click.command()
@click.option('-a', '--algorithm')
def add_detector():
	click.echo('Adding a detector....')

@click.command()
def info():
	pass

@click.command()
def reset():
	pass

@click.group()
def pipeline():
    pass

@click.command()
@click.argument('hash')
def parse_db():
	click.echo('parsing db for information')

@click.command()
def generate():
	#FOR NOW, max make make our datasets 10,000 images. 
	#assert() something about number of embedders
	#this needs to be an orchestrator for some sort of parallelization parameter
    click.echo('Here is information on the db that was just generated')

@click.command()
@click.argument('algorithm')
def analyze():
	#assert() something about number of detectors
	#should produce some sort of csv with statistics about each of the detectors
	click.echo('Analyzing steganalyzers')

pipeline.add_command(parse_db)
pipeline.add_command(generate)
pipeline.add_command(analyze)

pipeline.add_command(download)
pipeline.add_command(add_embedder)
pipeline.add_command(add_detector)

@click.command()
@click.argument('name')
def hello(count, name):
    for x in range(count):
        click.echo('Hello %s!' % name)

if __name__ == "__main__":
	#need a way to dispatch this... lol
	#can use click commands nice.
    pipeline()