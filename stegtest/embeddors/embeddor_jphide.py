import subprocess
import stegtest.types.compatibility as compatibility

from stegtest.types.embeddor import Embeddor
from stegtest.utils.filesystem import remove_file
from stegtest.utils.lookup import embeddor, create_asset_file

class JPHide(Embeddor):
	"""Frequency space hiding algorithm"""
	def __init__(self, secret_txt:str):
	    super().__init__()
	    self.secret_txt = create_asset_file(embeddor, secret_txt)

	def update_parameters(self, secret_txt:str):
	    remove_file(self.secret_txt)
	    self.secret_txt = create_asset_file(embeddor, secret_txt)

	@compatibility.register(compatibility.file_check, compatibility.jpeg, compatibility.jpg)
	def embed(self, path_to_input:str, path_to_output:str):
	    commands = ['jphide', 'hide', path_to_input, path_to_output, self.secret_txt]

	    print(commands)

	    subprocess.run(' '.join(commands), shell=True)