import subprocess
import stegtest.types.compatibility as compatibility

from stegtest.utils.lookup import embeddor, create_asset_file
from stegtest.utils.filesystem import remove_file
from stegtest.types.embeddor import Embeddor

#outguess -k password -d secret.txt cover.jpg stego.jpg

class Outguess(Embeddor):
    """Redundant bits steganographic algorithm"""
    def __init__(self, secret_txt:str, password:str):
        super().__init__()
        self.secret_txt = create_asset_file(embeddor, secret_txt)
        self.password = password

    def update_parameters(self, secret_txt:str, password:str):
        remove_file(self.secret_txt)
        self.secret_txt = create_asset_file(embeddor, secret_txt)
        self.password = password

    @compatibility.register(compatibility.file_check, compatibility.jpeg, compatibility.jpg)
    def embed(self, path_to_input:str, path_to_output:str):
        #outguess -k password -d secret.txt cover.jpg stego.jpg
        commands = ['outguess', '-k', self.password, '-d', self.secret_txt, path_to_input, path_to_output]
        subprocess.run(' '.join(commands), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
