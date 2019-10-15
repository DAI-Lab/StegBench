
import subprocess

from stegtest.types.detector import Detector

class YeNet(Detector):
    def __init__(self, *args):
        super().__init__()

    def train(self, path_to_directory):
        pass

    def detect(self, path_to_input):
    	pass

    def detect_bulk(self, path_to_directory, input_list):
    	pass