import subprocess
import stegtest.types.compatibility as compatibility

from stegtest.types.embeddor import Embeddor
from stegtest.utils.lookup import embeddor, create_asset_file

class StegHide(Embeddor):
    """Frequency based steganographic algorithm"""
    def __init__(self, secret_txt:str, password:str):
        super().__init__()
        self.secret_txt = create_asset_file(embeddor, secret_txt)
        self.password = password

    @compatibility.register(compatibility.file_check, compatibility.jpeg, compatibility.jpg, compatibility.bmp)
    def embed(self, path_to_input:str, path_to_output:str):
        commands = ['steghide', 'embed', '-f', '-ef', self.secret_txt, '-cf', path_to_input, '-p', self.password, '-sf', path_to_output]
        subprocess.run(' '.join(commands), shell=True)