import subprocess
import stegtest.types.compatibility as compatibility
from stegtest.types.embeddor import Embeddor
from stegtest.utils.filesystem import file_exists

class F5(Embeddor):
	"""F5 steganographic algorithm"""
	def __init__(self, secret_txt:str):
	    super().__init__()
	    self.secret_txt = secret_txt

	# f5 -t e -i cover.jpg -o stego.jpg -d 'secret message'
	@compatibility.register(compatibility.file_check, compatibility.jpeg, compatibility.jpg)
	def embed(self, path_to_input:str, path_to_output:str):
	    assert(file_exists(path_to_input))

	    commands = ['f5 -t e -i', path_to_input, '-o', path_to_output, '-d', self.secret_txt]
	    subprocess.run(' '.join(commands), shell=True)