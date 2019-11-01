import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs
import stegtest.algo.runner as runner
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

def secret_message_from_embedding(embedding_ratio, img_info):
	str_len_in_bits = float(img_info[lookup.embedding_max])*embedding_ratio
	strlen_in_bytes = int(str_len_in_bits/8)
	return generate_random_string(strlen_in_bytes)

def generate_password(byte_length):
	return generate_random_string(byte_length)

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

##### DOCKER ####
def preprocess_docker(algorithm_info, to_embed_list):
	#need to start the docker process
	image_name = algorithm_info[lookup.DOCKER_IMAGE]
	container_id = runner.start_docker(image_name, volumes=None)
	
	for to_embed in to_embed_list:
		to_embed[lookup.container_id] = container_id

	return [], to_embed_list

def generate_docker_cmd(algorithm_info, to_embed):
	cmd = get_cmd(algorithm_info)
	new_cmd = replace(cmd, to_embed)

	params = [to_embed[lookup.container_id], new_cmd]
	if lookup.WORKING_DIR in algorithm_info:
		params.append(algorithm_info[lookup.WORKING_DIR])

	return {lookup.COMMAND_TYPE: lookup.DOCKER, lookup.COMMAND: params}

def postprocess_docker(algorithm_info, embedded_list):
	#need to end the docker process 
	post_cmds = []
	if not embedded_list:
		return post_cmds

	docker_containers = list(set(list(map(lambda embedded: embedded[lookup.container_id], embedded_list))))
	for container_id in docker_containers:
		post_cmds.append({lookup.COMMAND_TYPE: lookup.END_DOCKER, lookup.COMMAND: [container_id]})

	return post_cmds

### NATIVE ###

def preprocess_native(algorithm_info, to_embed_list):
	#probably need to transform from directory to list, vice versa.
	raise NotImplementedError

def generate_native_cmd(algorithm_info, params):
	#need to do regular substitutions
	raise NotImplementedError

def postprocess_native(algorithm_info, embedded_list):
	raise NotImplementedError

### REST ###

def preprocess_rest(algorithm_info, to_embed_list):
	raise NotImplementedError

def generate_rest_cmd(algorithm_info, params):
	raise NotImplementedError

def postprocess_rest(algorithm_info, embedded_list):
	raise NotImplementedError

### CLASS ###

def preprocess_class(algorithm_info, to_embed_list):
	raise NotImplementedError

def generate_class_cmd(algorithm_info, params):
	raise NotImplementedError

def postprocess_class(algorithm_info, embedded_list):
	raise NotImplementedError

def generate_commands(algorithm_info, to_embed_list):
	command_type = algorithm_info[lookup.COMMAND_TYPE]

	preprocess_function = {
		lookup.DOCKER: preprocess_docker,
		lookup.NATIVE: preprocess_native,
		lookup.REST: preprocess_rest,
		lookup.CLASS: preprocess_class,
	}[command_type]

	pre_cmds, updated_embed_list = preprocess_function(algorithm_info, to_embed_list)

	generate_function = {
		lookup.DOCKER: generate_docker_cmd,
		lookup.NATIVE: generate_native_cmd,
		lookup.REST: generate_rest_cmd,
		lookup.CLASS: generate_class_cmd
	}[command_type]

	cmds = [generate_function(algorithm_info, to_embed) for to_embed in updated_embed_list]

	postprocess_function = {
		lookup.DOCKER: postprocess_docker,
		lookup.NATIVE: postprocess_native,
		lookup.REST: postprocess_rest,
		lookup.CLASS: postprocess_class
	}[command_type]

	post_cmds = postprocess_function(algorithm_info, updated_embed_list)

	sequential_cmds = pre_cmds + cmds + post_cmds
	
	return pre_cmds, cmds, post_cmds
