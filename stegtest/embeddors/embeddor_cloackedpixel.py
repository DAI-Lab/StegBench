
import subprocess
import stegtest.types.compatibility as compatibility

from stegtest.utils.lookup import embeddor, create_asset_file
from stegtest.types.embeddor import Embeddor

class CloackedPixel(Embeddor):
    """LSB steganographic algorithm"""
    def __init__(self, secret_txt:str, password:str):
        super().__init__()
        self.secret_txt = create_asset_file(embeddor, secret_txt)
        self.password = password

    # def update_params(secret_txt:str, password:str):
    #     #TODO need to remove the old text file....
    #     self.secret_txt = secret_txt
    #     self.password = password

    @compatibility.register(compatibility.file_check, compatibility.png)
    def embed(self, path_to_input:str, path_to_output:str):
        commands = ['cloackedpixel', 'hide', path_to_input, self.secret_txt, self.password]
        subprocess.run(' '.join(commands), shell=True)
