
import subprocess

from stegtest.types.embeddor import Embeddor

# from stegtest.utils.filesystem import file_exists

##NEED TO FINISH EMBEDDING PROCESS

class CloackedPixel(Embeddor):

    def __init__(self, secret_txt, password):
        super().__init__()
        self.secret_txt = secret_txt
        self.password = password

    def embed(self, path_to_input, path_to_output):
        # assert(file_exists(path_to_input))
        # assert(file_type(path_to_input, [".pmg"]))
        # assert(file_type(path_to_output, [".pmg"]))

    	commands = ['cloackedpixel', 'hide', path_to_input, self.secret_txt, self.password]
    	subprocess.run(commands)


CloackedPixel('ajinkya', 'ajinkya')