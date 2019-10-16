import subprocess
import stegtest.types.compatibility as compatibility
import stegtest.utils.filesystem as fs

from stegtest.types.embeddor import Embeddor

class Outguess(Embeddor):
    def __init__(self, secret_txt:str, password:str, noice:str):
        super().__init__()
        self.secret_txt = secret_txt
        self.password = password

        #embeddor create text file...

    @compatibility.register(compatibility.jpeg, compatibility.jpg)
    def embed(self, path_to_input, path_to_output):
        # assert(fs.file_exists(path_to_input))

        # assert(file_type(path_to_input, [".pmg"]))
        # assert(file_type(path_to_output, [".pmg"]))

        #outguess -k password -d secret.txt cover.jpg stego.jpg
        commands = ['outguess', '-k', self.password, '-d', self.secret_txt, path_to_input, path_to_output]
        subprocess.run(' '.join(commands), shell=True)
