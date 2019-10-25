import subprocess
import stegtest.types.compatibility as compatibility

from stegtest.types.embeddor import Embeddor
from stegtest.utils.lookup import embeddor, create_asset_file, run_cmd
from stegtest.utils.filesystem import remove_file

#jsteg hide cover.jpg secret.txt stego.jpg
class JSteg(Embeddor):
	"""LSB steganographic algorithm"""
	@compatibility.register(compatibility.file_check, compatibility.jpeg, compatibility.jpg)
	def embed(self, path_to_input:str, path_to_output:str, secret_txt:str):
		secret_txt_file = create_asset_file(embeddor, secret_txt)
		commands = ['jsteg', 'hide', path_to_input, secret_txt_file, path_to_output]
		run_cmd(commands)
