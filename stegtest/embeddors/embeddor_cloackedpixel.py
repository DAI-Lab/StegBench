import subprocess
import shutil
import stegtest.types.compatibility as compatibility

from stegtest.utils.filesystem import remove_file
from stegtest.utils.lookup import embeddor, create_asset_file
from stegtest.types.embeddor import Embeddor

class CloackedPixel(Embeddor):
    """LSB steganographic algorithm"""
    def __init__(self, secret_txt:str, password:str):
        super().__init__()
        self.secret_txt = create_asset_file(embeddor, secret_txt)
        self.password = password

    def update_parameters(self, secret_txt:str, password:str):
        remove_file(self.secret_txt)
        self.secret_txt = create_asset_file(embeddor, secret_txt)
        self.password = self.password

    @compatibility.register(compatibility.file_check, compatibility.png)
    def embed(self, path_to_input:str, path_to_output:str):
        commands = ['cloackedpixel', 'hide', path_to_input, self.secret_txt, self.password]
        subprocess.run(' '.join(commands), shell=True)

        output_file_name = path_to_input + '-stego.png'
        shutil.move(output_file_name, path_to_output)
