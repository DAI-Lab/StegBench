import subprocess
import os
import stegtest.types.compatibility as compatibility

from stegtest.types.embeddor import Embeddor
from stegtest.utils.filesystem import file_exists

from stegano import lsb

class SteganoLSB(Embeddor):
    """LSB steganographic algorithm"""
    @compatibility.register(compatibility.file_check, compatibility.png)
    def embed(self, path_to_input:str, path_to_output:str, secret_txt:str):
        secret = lsb.hide(path_to_input, secret_txt)
        secret.save(path_to_output)