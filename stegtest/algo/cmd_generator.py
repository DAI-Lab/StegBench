import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs
import stegtest.algo.runner as runner
import random
import string
import os

from os.path import abspath, join

docker_run_cmd = 'docker_run'
docker_wdir_cmd = 'docker_wdr'
docker_input_mount = '/input'
docker_output_mount = '/output'

docker_precepts = {
	docker_run_cmd: 'docker run --rm -d',
	docker_wdir_cmd: 'bash -c cd /my/app && for image in images; do'
}

input_dir = '/data-input'
output_dir = '/data-output'
asset_dir = '/data-asset'

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

def get_post_cmd(algorithm_info):
	if lookup.POST_COMMAND in algorithm_info:
		return algorithm_info[lookup.POST_COMMAND]

	return None

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
	for replacement_key in replacements:
		cmd = cmd.replace(replacement_key, replacements[replacement_key])
	return cmd

#### NATIVE ####
def preprocess_native(algorithm_info, to_embed_list):
	#probably need to transform from directory to list, vice versa.
	cmd = get_cmd(algorithm_info)
	if lookup.SECRET_TXT_FILE in cmd:
		for to_embed in to_embed_list:
			if lookup.SECRET_TXT_FILE not in cmd:
				txt_file_path = lookup.create_asset_file(algorithm_info[lookup.ALGORITHM_TYPE], to_embed[lookup.SECRET_TXT_PLAINTEXT])
				to_embed[lookup.SECRET_TXT_FILE] = txt_file_path

	if lookup.INPUT_IMAGE_DIRECTORY in cmd:
		raise NotImplementedError

	if lookup.OUTPUT_IMAGE_DIRECTORY in cmd:
		raise NotImplementedError

	return [], to_embed_list

def generate_native_cmd(algorithm_info, to_embed):
	#need to do regular substitutions
	cmd = get_cmd(algorithm_info)
	new_cmd = replace(cmd, to_embed)

	return {lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: [new_cmd]}

def postprocess_native(algorithm_info, embedded_list):
	cmd = get_post_cmd(algorithm_info)
	if cmd is None:
		return []

	new_cmd = replace(cmd, to_embed)
	return [{lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: new_cmd}]

def termination_native(algorithm_info, embedded_list):
	cmd = get_cmd(algorithm_info)

	removal_prefix = 'rm'
	termination_cmds = []
	if lookup.SECRET_TXT_FILE in cmd:
		for embedded in embedded_list:
			removal_cmd = ' '.join([removal_prefix, embedded[lookup.SECRET_TXT_FILE]])
			termination_cmds.append({ lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: [removal_cmd] })

	return termination_cmds

##### DOCKER ####
def preprocess_docker(algorithm_info, to_embed_list):
	"""starts docker command and updates parameters appropriately"""
	image_name = algorithm_info[lookup.DOCKER_IMAGE]
	cmd = get_cmd(algorithm_info)
	volumes = {}

	if lookup.SECRET_TXT_FILE in cmd:
		#TODO write all the secret txt to the assets folder and update to_embed_list
		for to_embed in to_embed_list:
			if lookup.SECRET_TXT_FILE not in to_embed:
				txt_file_path = lookup.create_asset_file(algorithm_info[lookup.ALGORITHM_TYPE], to_embed[lookup.SECRET_TXT_PLAINTEXT])
			else:
				txt_file_path = to_embed[lookup.SECRET_TXT_FILE]

			local_asset_dir = fs.get_directory(txt_file_path)
			volumes[local_asset_dir] = { 'bind': asset_dir, 'mode': 'rw'}

			asset_filename = fs.get_filename(txt_file_path)
			new_asset_path = join(asset_dir, asset_filename)
			to_embed[lookup.SECRET_TXT_FILE] = new_asset_path

	#inputs
	# if lookup.INPUT_IMAGE_DIRECTORY in cmd:
	# 	raise NotImplementedError
	# 	#need to update the commands 

	for to_embed in to_embed_list:
		assert(lookup.INPUT_IMAGE_PATH in to_embed)
		#TODO update this to be more dynamic
		original_input_path = to_embed[lookup.INPUT_IMAGE_PATH]
		original_input_path = abspath(original_input_path)

		local_input_dir = fs.get_directory(original_input_path)
		volumes[local_input_dir] = { 'bind': input_dir, 'mode': 'rw'}

		input_filename = fs.get_filename(original_input_path)
		new_input_path = join(input_dir, input_filename)
		to_embed[lookup.INPUT_IMAGE_PATH] = new_input_path

	#outputs
	# if lookup.OUTPUT_IMAGE_DIRECTORY in cmd:
	# 	raise NotImplementedError

	for to_embed in to_embed_list:
		assert(lookup.OUTPUT_IMAGE_PATH in to_embed)
		original_output_path = to_embed[lookup.OUTPUT_IMAGE_PATH]
		original_output_path = abspath(original_output_path)

		local_output_dir = fs.get_directory(original_output_path)
		volumes[local_output_dir] = { 'bind': output_dir, 'mode': 'rw'}

		output_filename = fs.get_filename(original_output_path)
		new_output_path = join(output_dir, output_filename)
		to_embed[lookup.OUTPUT_IMAGE_PATH] = new_output_path

	container_id = runner.start_docker(image_name, volumes=volumes)
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
	post_cmd = get_post_cmd(algorithm_info)

	if post_cmd:
		for embedded in embedded_list:
			new_cmd = replace(post_cmd, embedded)
			params = [embedded[lookup.container_id], new_cmd]
			if lookup.WORKING_DIR in algorithm_info:
				params.append(algorithm_info[lookup.WORKING_DIR])

			docker_cmd = {lookup.COMMAND_TYPE: lookup.DOCKER, lookup.COMMAND: params}
			post_cmds.append(docker_cmd)

	return post_cmds

def terimination_docker(algorithm_info, embedded_list):
	termination_cmds = []

	docker_containers = list(set(list(map(lambda embedded: embedded[lookup.container_id], embedded_list))))
	for container_id in docker_containers:
		termination_cmds.append({lookup.COMMAND_TYPE: lookup.END_DOCKER, lookup.COMMAND: [container_id]})

	cmd = get_cmd(algorithm_info)
	removal_prefix = 'rm'

	if lookup.SECRET_TXT_FILE in cmd:
		for embedded in embedded_list:
			asset_file_name = fs.get_filename(embedded[lookup.SECRET_TXT_FILE])
			asset_directory = lookup.get_algo_asset_dirs()[algorithm_info[lookup.ALGORITHM_TYPE]]

			old_asset_file_path = join(asset_directory, asset_file_name)
			removal_cmd = ' '.join([removal_prefix, old_asset_file_path])

			termination_cmds.append({ lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: [removal_cmd] })

	return termination_cmds

#### REST ####
def preprocess_rest(algorithm_info, to_embed_list):
	raise NotImplementedError

def generate_rest_cmd(algorithm_info, params):
	raise NotImplementedError

def postprocess_rest(algorithm_info, embedded_list):
	raise NotImplementedError

def termination_rest(algorithm_info, embedded_list):
	raise NotImplementedError

#### CLASS ####
def preprocess_class(algorithm_info, to_embed_list):
	raise NotImplementedError

def generate_class_cmd(algorithm_info, params):
	raise NotImplementedError

def postprocess_class(algorithm_info, embedded_list):
	raise NotImplementedError

def termination_class(algorithm_info, embedded_list):
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

	termination_function = {
		lookup.DOCKER: terimination_docker,
		lookup.NATIVE: termination_native,
		lookup.REST: termination_rest,
		lookup.CLASS: termination_class
	}[command_type]

	termination_cmds = termination_function(algorithm_info, updated_embed_list)
	return pre_cmds, cmds, post_cmds, termination_cmds
