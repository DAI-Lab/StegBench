import subprocess
import shutil
import stegtest.types.compatibility as compatibility

from stegtest.utils.filesystem import remove_file
from stegtest.utils.lookup import embeddor, create_asset_file, run_cmd
from stegtest.types.embeddor import Embeddor

class CloackedPixel(Embeddor):
    """LSB steganographic algorithm"""
    @compatibility.register(compatibility.file_check, compatibility.png)
    def embed(self, path_to_input:str, path_to_output:str, secret_txt:str, password:str):
        secret_txt_file = create_asset_file(embeddor, secret_txt)
        commands = ['cloackedpixel', 'hide', path_to_input, secret_txt_file, password]

        run_cmd(commands)

        output_file_name = path_to_input + '-stego.png'
        shutil.move(output_file_name, path_to_output)