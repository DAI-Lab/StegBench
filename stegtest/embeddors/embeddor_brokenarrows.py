import subprocess
from stegtest.types.embeddor import Embeddor
from shutil import copyfile

##BROKEN ARROWS IS NOT WORKING JUST YET###

class BrokenArrows(Embeddor):

    def __init__(self):
        super().__init__()

    def embed(self, path_to_input, path_to_output):
        assert(file_exists(path_to_input))
        # assert(file_type(path_to_input, [".pmg"]))
        # assert(file_type(path_to_output, [".pmg"]))

        copyfile(path_to_input, path_to_output)
        commands = ['ba-embed', 'embed', path_to_output]
        subprocess.run(commands)