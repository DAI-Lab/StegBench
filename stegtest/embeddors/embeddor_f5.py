import subprocess
import stegtest.types.compatibility as compatibility
from stegtest.types.embeddor import Embeddor
from stegtest.utils.lookup import run_cmd

# f5 -t e -i cover.jpg -o stego.jpg -d 'secret message'
class F5(Embeddor):
	"""F5 steganographic algorithm"""
	@compatibility.register(compatibility.file_check, compatibility.jpeg, compatibility.jpg)
	def embed(self, path_to_input:str, path_to_output:str, secret_txt:str):
		commands = ['f5 -t e -i', path_to_input, '-o', path_to_output, '-d', secret_txt]
		run_cmd(commands)