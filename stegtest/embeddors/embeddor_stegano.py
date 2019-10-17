import subprocess
import os
import stegtest.types.compatibility as compatibility

from stegtest.types.embeddor import Embeddor
from stegtest.utils.filesystem import file_exists

##Need more work on this embeddor

class Stegano(Embeddor):
    """Various LSB steganographic algorithm"""
    def __init__(self, secret_txt:str, mode:str):
        super().__init__()
        self.secret_txt = secret_txt
        self.mode = mode

    @compatibility.register(compatibility.file_check, compatibility.png)
    def embed(self, path_to_input:str, path_to_output:str):
        # assert(file_type(path_to_input, [".pmg"]))
        # assert(file_type(path_to_output, [".pmg"]))

        # stegano-lsb hide --input cover.jpg -f secret.txt -e UTF-8 --output stego.png 
        # stegano-red hide --input cover.png -m "secret msg" --output stego.png 
        # stegano-lsb-set hide --input cover.png -f secret.txt -e UTF-8 -g $GENERATOR --output stego.png for various generators (stegano-lsb-set list-generators)
        commands = []
        if self.mode == 'LSB':
            commands = ['stegano-lsb', 'hide', '--input', path_to_input, '-m', self.secret_txt, '-e', 'UTF-8', '--output', path_to_output]
        elif self.mode == 'RED':
            commands = ['stegano-red', 'hide', '--input', path_to_input, '-m', self.secret_txt, '--output', path_to_output]
        else:
            commands = ['stegano-lsb-set', 'hide', '--input', path_to_input, '-f', self.secret_txt, 
            '-e', 'UTF-8', '-g', '$GENERATOR', '--output', path_to_output, 'for various generators (stegano-lsb-set list-generators)']

        subprocess.run(' '.join(commands), shell=True)