import subprocess
from stegtest.types.embeddor import Embeddor
from stegtest.utils.filesystem import file_exists

class Outguess(Embeddor):

    def __init__(self, secret_txt:str, password:str):
        super().__init__()
        self.secret_txt = secret_txt
        self.password = password

    def embed(self, path_to_input, path_to_output):
        assert(file_exists(path_to_input))

        # assert(file_type(path_to_input, [".pmg"]))
        # assert(file_type(path_to_output, [".pmg"]))

        #outguess -k password -d secret.txt cover.jpg stego.jpg
        commands = ['outguess', '-k', self.password, '-d', self.secret_txt, path_to_input, path_to_output]
        subprocess.run(commands)
