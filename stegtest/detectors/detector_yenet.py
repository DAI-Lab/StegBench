
import subprocess
import stegtest.types.compatibility as compatibility

from stegtest.types.detector import Detector

from stegdetect import StegDetect

class YeNet(Detector):
	"""YeNet CNN Detection Architecture"""
	def __init__(self):
	    super().__init__()
	    self.model = StegDetect.load()

	def train(self, path_to_directory):
	    pass

	@compatibility.register(compatibility.png, compatibility.jpg, compatibility.jpeg)
	def detect(self, path_to_input):
		result = self.model.detect(path_to_input)
		return result

	def detect_bulk(self, input_list, path_to_directory=None):
		results = list(map(self.detect, input_list))
		return results