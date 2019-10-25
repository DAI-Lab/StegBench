import subprocess
import stegtest.types.compatibility as compatibility

from stegtest.utils.lookup import embeddor, create_asset_file, run_cmd
from stegtest.utils.filesystem import remove_file
from stegtest.types.embeddor import Embeddor

class Outguess(Embeddor):
    """Redundant bits steganographic algorithm"""
    @compatibility.register(compatibility.file_check, compatibility.jpeg, compatibility.jpg)
    def embed(self, path_to_input:str, path_to_output:str, secret_txt:str, password:str):
        secret_txt_file = create_asset_file(embeddor, secret_txt)
        commands = ['outguess', '-k', password, '-d', secret_txt_file, path_to_input, path_to_output]
        run_cmd(commands)

