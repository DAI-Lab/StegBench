from steganogan import SteganoGAN
import stegtest.types.compatibility as compatibility
from stegtest.types.embeddor import Embeddor

class Steganogan(Embeddor):
	"""SteganoGAN algorithm"""
	def __init__(self, secret_txt:str):
	    super().__init__()
	    self.model = SteganoGAN.load('basic')
	    self.secret_txt = secret_txt

	def update_parameters(self, secret_txt:str):
	    self.secret_txt = self.secret_txt

	@compatibility.register(compatibility.file_check, compatibility.png)
	def embed(self, path_to_input:str, path_to_output:str):
		self.model.encode(path_to_input, path_to_output, self.secret_txt)