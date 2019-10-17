import subprocess
import stegtest.types.compatibility as compatibility
from stegtest.types.embeddor import Embeddor

# f5 -t e -i cover.jpg -o stego.jpg -d 'secret message'
class F5(Embeddor):
	"""F5 steganographic algorithm"""
	def __init__(self, secret_txt:str):
	    super().__init__()
	    self.secret_txt = secret_txt

	def update_parameters(self, secret_txt:str):
	    self.secret_txt = self.secret_txt

	@compatibility.register(compatibility.file_check, compatibility.jpeg, compatibility.jpg)
	def embed(self, path_to_input:str, path_to_output:str):
	    commands = ['f5 -t e -i', path_to_input, '-o', path_to_output, '-d', self.secret_txt]

	    subprocess.run(' '.join(commands), shell=True)