import subprocess

from stegtest.types.embeddor import Embeddor
import stegtest.types.compatibility as compatibility

from shutil import copyfile

##BROKEN ARROWS IS NOT WORKING JUST YET###
class BrokenArrows(Embeddor):
	"""BOWS2 Challenge algorithm"""
	def __init__(self):
	    super().__init__()

	def update_parameters(self):
	    pass

	@compatibility.register(compatibility.file_check, compatibility.jpeg, compatibility.jpg)
	def embed(self, path_to_input:str, path_to_output:str):

	    copyfile(path_to_input, path_to_output)
	    commands = ['ba-embed', 'embed', path_to_output]
	    subprocess.run(' '.join(commands), shell=True)