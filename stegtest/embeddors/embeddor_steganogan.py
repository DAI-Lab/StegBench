from steganogan import SteganoGAN
import stegtest.types.compatibility as compatibility
from stegtest.types.embeddor import Embeddor

class Steganogan(Embeddor):
	"""SteganoGAN algorithm"""
	def __init__(self):
	    super().__init__()
	    self.model = SteganoGAN.load('dense')

	@compatibility.register(compatibility.file_check, compatibility.png)
	def embed(self, path_to_input:str, path_to_output:str, secret_txt:str):
		self.model.encode(path_to_input, path_to_output, secret_txt)
