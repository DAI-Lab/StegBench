import subprocess
import stegtest.types.compatibility as compatibility
from stegtest.types.embeddor import Embeddor
from stegtest.utils.filesystem import file_exists

class F5(Embeddor):

    def __init__(self, secret_txt:str):
        super().__init__()
        self.secret_txt = secret_txt

    @compatibility.register(compatibility.jpeg, compatibility.jpg)
    def embed(self, path_to_input, path_to_output):
        assert(file_exists(path_to_input))
        # assert(file_type(path_to_input, [".pmg"]))
        # assert(file_type(path_to_output, [".pmg"]))

		# f5 -t e -i cover.jpg -o stego.jpg -d 'secret message'
        commands = ['f5', '-t', 'e', '-i', path_to_input, '-o', path_to_output, -f, self.secret_txt]
        subprocess.run(' '.join(commands), shell=True)