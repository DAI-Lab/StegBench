import subprocess
import stegtest.types.compatibility as compatibility
import stegtest.utils.filesystem as fs
from stegtest.types.detector import Detector
from stegtest.utils.lookup import run_cmd


def generate_csv_file():
    """generates a csv file for stegexpose results"""
    return fs.create_file_from_hash(fs.get_uuid(), 'csv')

class StegExpose(Detector):
    """Sample Pairs, RS Analysis, Chi Square Attack, Primary Sets"""

    def __init__(self):
        super().__init__()

    def train(self, path_to_directory):
        pass

    @compatibility.register(compatibility.png, compatibility.bmp)
    def detect(self, path_to_input):
        #TODO -- need to move the image to it's own localized directory
        #read the csv results
        #return the csv results
        commands = ['java -jar', '/usr/bin/StegExpose.jar', path_to_input, 'default', 'default']
        commands.append(generate_csv_file())

        subprocess.run(' '.join(commands), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def detect_bulk(self, input_list, path_to_directory):
        assert(path_to_directory is not None)
        commands = ['java -jar', '/usr/bin/StegExpose.jar', path_to_directory, 'default', 'default']
        csv_file = generate_csv_file() 
        commands.append(csv_file)

        run_cmd(commands)

        csv_results = fs.read_csv_file(csv_file)
        csv_results = csv_results[2:] #get rid of header
        csv_results = [(result[1])  for result in csv_results]
        csv_results = [True if result=='true' else False for result in csv_results]

        fs.remove_file(csv_file)
        return csv_results