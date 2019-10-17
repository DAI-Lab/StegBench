import subprocess
import stegtest.types.compatibility as compatibility

from stegtest.types.embeddor import Embeddor
from stegtest.utils.lookup import embeddor, create_asset_file
from stegtest.utils.filesystem import remove_file

#jsteg hide cover.jpg secret.txt stego.jpg
class JSteg(Embeddor):
	"""LSB steganographic algorithm"""
	def __init__(self, secret_txt:str):
	    super().__init__()
	    self.secret_txt = create_asset_file(embeddor, secret_txt)

	def update_parameters(self, secret_txt:str):
	    remove_file(self.secret_txt)
	    self.secret_txt = create_asset_file(embeddor, secret_txt)

	@compatibility.register(compatibility.file_check, compatibility.jpeg, compatibility.jpg)
	def embed(self, path_to_input:str, path_to_output:str):
	    commands = ['jsteg', 'hide', path_to_input, self.secret_txt, path_to_output]
	    subprocess.run(' '.join(commands), shell=True)