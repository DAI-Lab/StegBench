
import subprocess
import stegtest.types.compatibility as compatibility

from stegtest.types.detector import Detector

class YeNet(Detector):
	"""YeNet CNN Detection Architecture"""
	def __init__(self, *args):
	    super().__init__()

	def train(self, path_to_directory):
	    pass

	@compatibility.register(compatibility.png, compatibility.bmp)
	def detect(self, path_to_input):
		pass

	def detect_bulk(self, path_to_directory, input_list):
		pass