import subprocess
import stegtest.types.compatibility as compatibility
from stegtest.types.embeddor import Embeddor
from stegtest.utils.lookup import embeddor, create_asset_file

class LSB(Embeddor):
    """LSB steganographic algorithm"""
    def __init__(self, secret_txt:str):
        super().__init__()
        self.secret_txt = create_asset_file(embeddor, secret_txt)

    @compatibility.register(compatibility.file_check, compatibility.png, compatibility.bmp)
    def embed(self, path_to_input:str, path_to_output:str):
        assert(file_exists(path_to_input))
        commands = ['LSBSteg', 'encode', '-i', path_to_input, '-o', path_to_output, -f, self.secret_txt]
        subprocess.run(' '.join(commands), shell=True)
