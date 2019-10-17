import subprocess
import os
import stegtest.types.compatibility as compatibility

from stegtest.types.embeddor import Embeddor
from stegtest.utils.filesystem import file_exists

class StegPy(Embeddor):
    """LSB steganographic algorithm"""
    def __init__(self, secret_txt:str):
        super().__init__()
        self.secret_txt = secret_txt

    @compatibility.register(compatibility.file_check, compatibility.png, compatibility.gif, compatibility.bmp)
    def embed(self, path_to_input:str, path_to_output:str):
        commands = ['stegpy', self.secret_txt, path_to_input]
        subprocess.run(' '.join(commands), shell=True)

        # index_of_slash = path_to_input.rfind("/") + 1
        # output_file = path_to_input[0:index_of_slash] + "_" + path_to_input[index_of_slash:]

        # os.rename(output_file, path_to_output)  ##TODO CHECK IF THIS IS VALID
