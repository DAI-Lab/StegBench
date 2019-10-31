import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs
import random
import string

from os.path import abspath, join

docker_run_cmd = 'docker_run'
docker_wdir_cmd = 'docker_wdr'
docker_input_mount = '/input'
docker_output_mount = '/output'

docker_precepts = {
	docker_run_cmd: 'docker run --rm -d',
	docker_wdir_cmd: 'bash -c cd /my/app && for image in images; do'
}

input_dir = 'data-input'
output_dir = 'data-output'
asset_dir = 'data-asset'

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
OUTPUT_IMAGE_DIRECTORY = 'OUTPUT_DIRECTORY'
OUTPUT_IMAGE_NAME = 'OUTPUT_IMAGE_NAME'
OUTPUT_IMAGE_PATH = 'OUTPUT_IMAGE_PATH'

def get_cmd(algorithm_info):
	return algorithm_info[lookup.COMMAND]

def generate_random_string(byte_length=20):
	return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(byte_length))

def generate_random_float(max_flt=100):
	return random.random()*max_flt

def generate_random_int(max_int=100):
	return int(generate_random_float(max_int))

def generate_param(type, *args):
	function = {
		lookup.SECRET_TXT_PLAINTEXT: generate_random_string, 
		lookup.SECRET_TXT_FILE: generate_random_string,
		lookup.PASSWORD: generate_password,
		lookup.BPP: generate_random_float,
		lookup.bpnzAC: generate_random_float
	}[type]
	return function(*args)

def secret_message_from_embedding(img_info, embedding_ratio):
	str_len_in_bits = None
	if img_info[lookup.image_type] is in lookup.get_frequency_types():
		str_len_in_bits = (img_info[lookup.bpnzAC]*embedding_ratio)
	else:
		num_channels = lookup.convert_channels_to_int(img_info[])
		str_len_in_bits = img_info[lookup.image_width]*img_info[lookup.image_height]*num_channels

	strlen_in_bytes = int(strlen_in_bits/8)
	return generate_random_string(strlen_in_bytes)

def generate_password(byte_length):
	return generate_random_string(byte_length)

# def generate_secret_text(file_info, bpp):
# 	width = int(file_info[lookup.image_width])
# 	height = int(file_info[lookup.image_height])
# 	channels = lookup.convert_channels_to_int(file_info[lookup.image_channels])

# 	pixels = width*height*channels
# 	strlen_in_bits = pixels*bpp
# 	strlen_in_bytes = int(strlen_in_bits/8)

# 	return generate_random_string(strlen_in_bytes)

def validate_single(command):
	if lookup.INPUT_IMAGE_PATH not in command:
		raise ValueError('Command does not support single image inputs')

def validate_batch(command):
	if lookup.INPUT_IMAGE_DIRECTORY not in command:
		raise ValueError('Command does not support batch image inputs')

def validate(command_type, algorithm_info):
	validate_function = {
		lookup.SINGLE: validate_single,
		lookup.BATCH: validate_batch,
	}[command_type]

	command = get_cmd(algorithm_info)
	validate_function(command)

def replace(cmd:str, replacements):
	cmd = cmd.split()
	cmd = [subpart if subpart not in replacements else replacements[subpart] for subpart in cmd]
	return ' '.join(cmd)

def generate_docker_cmd(algorithm_info, params):
	cmd = get_cmd(algorithm_info)
	
	replacements = {}
	if lookup.INPUT_IMAGE_DIRECTORY in params: #TODO
		raise NotImplementedError
	elif lookup.INPUT_IMAGE_PATH in params:
		input_path = abspath(params[lookup.INPUT_IMAGE_PATH])
		file_name = fs.get_filename(input_path)
		new_file_path = join(docker_input_mount, file_name)
		replacements[lookup.INPUT_IMAGE_PATH] = new_file_path

	if lookup.OUTPUT_IMAGE_DIRECTORY in params: #TODO
		raise NotImplementedError
	elif lookup.OUTPUT_IMAGE_PATH in params:
		output_path = abspath(params[lookup.OUTPUT_IMAGE_PATH])
		file_name = fs.get_filename(output_path)
		new_file_path = join(docker_output_mount, file_name)
		replacements[lookup.OUTPUT_IMAGE_PATH] = new_file_path

	new_cmd = replace(cmd, replacements)

	print(new_cmd)
	return new_cmd

def generate_native_cmd(algorithm_info, params):
	raise NotImplementedError

def generate_rest_cmd(algorithm_info, params):
	raise NotImplementedError

def generate_class_cmd(algorithm_info, params):
	raise NotImplementedError

def generate_command(algorithm_info, params):
	command_type = algorithm_info[lookup.COMMAND_TYPE]
	generate_function = {
		lookup.DOCKER: generate_docker_cmd,
		lookup.NATIVE: generate_native_cmd,
		lookup.REST: generate_rest_cmd,
		lookup.CLASS: generate_class_cmd
	}[command_type]

	cmd = generate_function(algorithm_info, params)
	return cmd

def generate_detect_command(command):
	raise NotImplementedError


