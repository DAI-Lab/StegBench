import subprocess
from utils import Embeddor
from utils.filesystem import file_exists

class F5(Embeddor):

    def __init__(self, secret_txt):
        super().__init__()
        self.secret_txt = secret_txt

    def embed(self, path_to_input, path_to_output):
        assert(file_exists(path_to_input))
        assert(file_type(path_to_input, [".pmg"]))
        assert(file_type(path_to_output, [".pmg"]))

    	commands = ['f5', '-t', 'e', '-i', path_to_input, '-o', path_to_output, -f, self.secret_txt]
    	subprocess.run(commands)


F5 = 

# f5 -t e -i cover.jpg -o stego.jpg -d 'secret message'