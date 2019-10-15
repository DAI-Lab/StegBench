import subprocess
import os
from stegtest.types.embeddor import Embeddor
from stegtest.utils.filesystem import file_exists

class StegPy(Embeddor):

    def __init__(self, secret_txt:str):
        super().__init__()
        self.secret_txt = secret_txt

    def embed(self, path_to_input, path_to_output):
        assert(file_exists(path_to_input))
        # assert(file_type(path_to_input, [".pmg"]))
        # assert(file_type(path_to_output, [".pmg"]))

        commands = ['stegpy', self.secret_txt, path_to_input]
        subprocess.run(commands)

        index_of_slash = path_to_input.rfind("/") + 1
        output_file = path_to_input[0:index_of_slash] + "_" + path_to_input[index_of_slash:]

        os.rename(output_file, path_to_output)  ##TODO CHECK IF THIS IS VALID
