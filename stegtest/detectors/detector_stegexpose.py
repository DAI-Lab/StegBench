import subprocess
import stegtest.types.compatibility as compatibility
from stegtest.types.detector import Detector

class StegExpose(Detector):
    """Sample Pairs, RS Analysis, Chi Square Attack, Primary Sets"""

    def __init__(self):
        super().__init__()

    def generate_csv_file(self, path_to_directory):
        #some sort of hash
        return 'default'

    def train(self, path_to_directory):
        pass

    @compatibility.register(compatibility.png, compatibility.bmp)
    def detect(self, path_to_input):
        #TODO -- need to move the image to it's own localized directory
        #read the csv results
        #return the csv results
        commands = ['java -jar', '/usr/bin/StegExpose.jar', path_to_directory, 'default', 'default']
        if self.output_csv:
            commands.append(generate_csv_file(path_to_directory))

        subprocess.run(commands)

    def detect_bulk(self, input_list, path_to_directory=None):
        commands = ['java -jar', '/usr/bin/StegExpose.jar', path_to_directory, 'default', 'default']
        if self.output_csv:
            commands.append(generate_csv_file(path_to_directory))

        subprocess.run(commands)

        results = [True for i in range(len(input_list))] #default for now