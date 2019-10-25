
import stegtest.types.compatibility as compatibility

from stegtest.types.embeddor import Embeddor
from stegtest.utils.lookup import embeddor, create_asset_file, run_cmd
from stegtest.utils.filesystem import remove_file


class LSB(Embeddor):
	"""LSB steganographic algorithm"""

	@compatibility.register(compatibility.file_check, compatibility.png, compatibility.bmp)
	def embed(self, path_to_input:str, path_to_output:str, secret_txt:str):
		secret_txt_file = create_asset_file(embeddor, secret_txt)
		commands = ['LSBSteg', 'encode', '-i', path_to_input, '-o', path_to_output, '-f', secret_txt_file]
		run_cmd(commands)

