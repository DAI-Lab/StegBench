import subprocess
from utils import Embeddor
from utils.filesystem import file_exists

class LSB(Embeddor):

    def initialize(self, secret_txt):
        super().__init__()
        self.secret_txt = secret_txt

    def embed(self, path_to_input, path_to_output):
        assert(file_exists(path_to_input))
        assert(file_type(path_to_input, [".pmg"]))
        assert(file_type(path_to_output, [".pmg"]))

    	commands = ['LSBSteg', 'encode', '-i', path_to_input, '-o', path_to_output, -f, self.secret_txt]
    	subprocess.run(commands)