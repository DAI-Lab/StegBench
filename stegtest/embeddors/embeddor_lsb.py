import subprocess
import stegtest.types.compatibility as compatibility
from stegtest.types.embeddor import Embeddor
from stegtest.utils.filesystem import file_exists

class LSB(Embeddor):

    def __init__(self, secret_txt:str):
        super().__init__()
        self.secret_txt = secret_txt

    @compatibility.register(compatibility.png, compatibility.bmp)
    def embed(self, path_to_input, path_to_output):
        assert(file_exists(path_to_input))
        # assert(file_type(path_to_input, [".pmg"]))
        # assert(file_type(path_to_output, [".pmg"]))
        commands = ['LSBSteg', 'encode', '-i', path_to_input, '-o', path_to_output, -f, self.secret_txt]
        subprocess.run(' '.join(commands), shell=True)
