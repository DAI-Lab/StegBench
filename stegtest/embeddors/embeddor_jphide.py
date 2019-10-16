import subprocess
import stegtest.types.compatibility as compatibility
from stegtest.types.embeddor import Embeddor
from stegtest.utils.filesystem import file_exists

class JPHide(Embeddor):

    def __init__(self, secret_txt:str):
        super().__init__()
        self.secret_txt = secret_txt

    @compatibility.register(compatibility.jpeg, compatibility.jpg)
    def embed(self, path_to_input, path_to_output):
        assert(file_exists(path_to_input))

        # assert(file_type(path_to_input, [".jpg", ".jpeg"]))
        # assert(file_type(path_to_output, [".jpg", ".jpeg"]))
        commands = ['jphide', 'hide', path_to_input, path_to_output, self.secret_txt, ]
        subprocess.run(' '.join(commands), shell=True)