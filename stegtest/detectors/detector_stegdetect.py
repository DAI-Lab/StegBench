
import subprocess

from stegtest.types.detector import Detector
from stegtest.utils.filesystem import dir_exists, file_exists

# from stegtest.utils.filesystem import file_exists
# http://old-releases.ubuntu.com/ubuntu/pool/universe/s/stegdetect/

class StegDetect(Detector):
    def __init__(self, *args):
        super().__init__()

    def train(self, path_to_directory):
        pass

    def detect(self, path_to_input):
        assert(file_exists(path_to_input))
        # assert(file_type(path_to_input, [".jpg"]))

        commands = ['stegdetect', path_to_input,]
        subprocess.run(commands)

    def detect_bulk(self, path_to_directory, input_list):
        if not input_list:
            assert(dir_exists(path_to_directory))
            input_list = [] #get_images_in_directory(input_list, ['jpg'])

        num_images = len(input_list)

        for i in range(num_images): #can parallelize this code a lot
            self.detect(input_list[i])