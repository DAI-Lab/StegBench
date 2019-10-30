import stegtest.utils.lookup as lookup
import stegtest.utils.bash as bash
import random
import string

#COMMAND
COMMAND = 'run'

#COMMAND SPECIFIC - COVER
INPUT_IMAGE_DIRECTORY = 'INPUT_DIRECTORY'
INPUT_IMAGE_NAME = 'INPUT_IMAGE_NAME'
INPUT_IMAGE_PATH = 'INPUT_IMAGE_PATH'

#COMMAND SPECIFIC - SECRET MESSAGE
SECRET_TXT_PLAINTEXT = 'SECRET_TXT_PLAINTEXT'
SECRET_TXT_FILE = 'SECRET_TXT_FILE'

#COMMAND-SPECIFIC - SUPPORTED INPUT PARAMETERS
PASSWORD = 'PASSWORD'
BPP = 'BPP'
bpnzAC = 'BPNZAC'

#COMMAND-SPECIFIC - OUTPUT
OUTPUT_DIRECTORY = 'OUTPUT_DIRECTORY'
OUTPUT_IMAGE_NAME = 'OUTPUT_IMAGE_NAME'
OUTPUT_IMAGE_PATH = 'OUTPUT_IMAGE_PATH'

docker_run_cmd = 'docker_run'
docker_wdir_cmd = 'docker_wdr'
docker_precepts = {
	docker_run_cmd: 'docker run --rm',
	docker_wdir_cmd: 'bash -c cd /my/app && for image in images; do'
}

def generate_random_string(byte_length=20):
	return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(byte_length))

def generate_random_float():
	return random.random()*10000

def generate_random_int():
	return int(generate_random_float())

def generate_param(type, *args):
	function = {
		'str': generate_random_string, 
		'float': generate_random_float,
		'int': generate_random_int,
	}[type]
	return function(*args)

def generate_password(byte_length):
	return generate_random_string(byte_length)

def generate_secret_text(file_info, bpp):
	width = int(file_info[lookup.image_width])
	height = int(file_info[lookup.image_height])
	channels = lookup.convert_channels_to_int(file_info[lookup.image_channels])

	pixels = width*height*channels
	strlen_in_bits = pixels*bpp
	strlen_in_bytes = int(strlen_in_bits/8)

	return generate_random_string(strlen_in_bytes)

def validate_single(command):
	if INPUT_IMAGE_PATH not in command:
		raise ValueError('Command does not support single image inputs')

def validate_batch(command):
	if INPUT_IMAGE_DIRECTORY not in command:
		raise ValueError('Command does not support batch image inputs')

def get_cmd(algorithm_info):
	return algorithm_info[COMMAND]

def generate_embed_command(command):
	return command



def generate_detect_command(command):
	raise NotImplementedError


