import subprocess
import stegtest.types.compatibility as compatibility

from stegtest.types.embeddor import Embeddor
from stegtest.utils.lookup import embeddor, create_asset_file, run_cmd
from stegtest.utils.filesystem import remove_file

class StegHide(Embeddor):
    """Frequency based steganographic algorithm"""
    @compatibility.register(compatibility.file_check, compatibility.jpeg, compatibility.jpg, compatibility.bmp)
    def embed(self, path_to_input:str, path_to_output:str, secret_txt:str, password:str):
        secret_txt_file = create_asset_file(embeddor, secret_txt, shortened=True)
        commands = ['steghide embed -f -ef', secret_txt_file, '-cf', path_to_input, '-p', password, '-sf', path_to_output]
        run_cmd(commands)
