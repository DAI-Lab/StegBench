import subprocess
import stegtest.types.compatibility as compatibility

from stegtest.types.detector import Detector
from stegtest.utils.filesystem import dir_exists

# from stegtest.utils.filesystem import file_exists

##NEED TO FINISH EMBEDDING PROCESS


class StegExpose(Detector):

    def __init__(self, output_csv:bool=False):
        super().__init__()
        self.output_csv = output_csv

    def generate_csv_file(self, path_to_directory):
        #some sort of hash
        return 'default'

    def train(self, path_to_directory):
        pass

    @compatibility.register(compatibility.png, compatibility.bmp)
    def detect(self, path_to_input):
        pass #only runs ond directorys

    def detect_bulk(self, path_to_directory, input_list):
        assert(dir_exists(path_to_directory))
        commands = ['java -jar', 'StegExpose.jar', path_to_directory, 'default', 'default']
        if self.output_csv:
            commands.append(generate_csv_file(path_to_directory))

        subprocess.run(commands)