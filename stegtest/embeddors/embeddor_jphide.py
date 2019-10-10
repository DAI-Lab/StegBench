import subprocess
from utils import Embeddor
from utils.filesystem import file_exists

class JPHide(Embeddor):

    def initialize(self, secret_txt):
        super().__init__()
        self.secret_txt = secret_txt

    def embed(self, path_to_input, path_to_output):
        assert(file_exists(path_to_input))
        assert(file_type(path_to_input, [".jpg", ".jpeg"]))
        assert(file_type(path_to_output, [".jpg", ".jpeg"]))

    	commands = ['jphide', 'hide', path_to_input, path_to_output, self.secret_txt, ]
    	subprocess.run(commands)