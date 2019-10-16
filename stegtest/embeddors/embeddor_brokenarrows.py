import subprocess
from stegtest.types.embeddor import Embeddor
import stegtest.types.compatibility as compatibility
from shutil import copyfile

##BROKEN ARROWS IS NOT WORKING JUST YET###

class BrokenArrows(Embeddor):

    def __init__(self):
        super().__init__()

    @compatibility.register(compatibility.jpeg, compatibility.jpg)
    def embed(self, path_to_input, path_to_output):
        assert(file_exists(path_to_input))

        copyfile(path_to_input, path_to_output)
        commands = ['ba-embed', 'embed', path_to_output]
        subprocess.run(' '.join(commands), shell=True)