import subprocess
from utils import Embeddor
from utils.filesystem import file_exists

class JSteg(Embeddor):

    def initialize(self, secret_txt):
        super().__init__()
        self.secret_txt = secret_txt

    def embed(self, path_to_input, path_to_output):
        assert(file_exists(path_to_input))
        assert(file_type(path_to_input, [".pmg"]))
        assert(file_type(path_to_output, [".pmg"]))

    	commands = ['jsteg', 'hide', path_to_input, self.secret_txt, path_to_output]
    	subprocess.run(commands)


#jsteg hide cover.jpg secret.txt stego.jpg