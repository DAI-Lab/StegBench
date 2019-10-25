import subprocess
import os
import stegtest.types.compatibility as compatibility

from stegtest.types.embeddor import Embeddor
from stegtest.utils.filesystem import file_exists

from stegano import lsbset
from stegano.lsbset import generators

class SteganoGenerator(Embeddor):
    """Uses Sieve of Erathostenes to embed information using LSB"""
    def __init__(self, secret_txt:str):
        super().__init__()
        self.secret_txt = secret_txt

    def update_parameters(self, secret_txt:str):
        self.secret_txt = secret_txt

    @compatibility.register(compatibility.file_check, compatibility.png)
    def embed(self, path_to_input:str, path_to_output:str):
        secret_image = lsbset.hide(path_to_input, self.secret_txt, generators.eratosthenes())
        secret_image.save(path_to_output)