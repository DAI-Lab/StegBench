
import subprocess
import stegtest.types.compatibility as compatibility

from stegtest.types.detector import Detector

# from stegtest.utils.filesystem import file_exists
# http://old-releases.ubuntu.com/ubuntu/pool/universe/s/stegdetect/


"""UNMAINTAINED"""

class StegDetect(Detector):
    """Statistical Detector"""
    def __init__(self, *args):
        super().__init__()

    def train(self, path_to_directory):
        pass

    @compatibility.register(compatibility.jpeg, compatibility.jpg)
    def detect(self, path_to_input):
        commands = ['stegodetect', path_to_input]
        subprocess.run(commands)
        return True

    def detect_bulk(self, input_list, path_to_directory=None):
        print(len(input_list))
        results = list(map(self.detect, input_list))
        return results