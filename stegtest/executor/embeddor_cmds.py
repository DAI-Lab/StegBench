import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs
import stegtest.executor.runner as runner
import os
from collections import defaultdict

from os.path import abspath, join

def replace(cmd:str, replacements):
	for replacement_key in replacements:
		cmd = cmd.replace(replacement_key, str(replacements[replacement_key]))
	return cmd

def process_directories(algorithm_info, to_embed_list):
	sorted_by_directories = defaultdict(list)
	for to_embed in to_embed_list:
		input_directory = abspath(fs.get_directory(to_embed[lookup.INPUT_IMAGE_PATH]))
		output_directory = abspath(fs.get_directory(to_embed[lookup.OUTPUT_IMAGE_PATH]))
		sorted_by_directories[(input_directory, output_directory)] = to_embed_list

	updated_embed_list = []
	db_directory = lookup.get_db_dirs()[lookup.dataset]
	for directory_pair in sorted_by_directories:
		temp_directory = abspath(join(db_directory, fs.get_uuid()))
		fs.make_dir(temp_directory)

		to_embed_files = sorted_by_directories[directory_pair]
		for file in to_embed_files: #TODO parallelize this
			fs.copy_file(file[lookup.INPUT_IMAGE_PATH], temp_directory)
		payloads = set(list(map(lambda f: f[lookup.PAYLOAD], sorted_by_directories[directory_pair])))
		assert(len(payloads) == 1)
		payload = payloads.pop()

		to_embed = {lookup.INPUT_IMAGE_DIRECTORY: temp_directory, lookup.OUTPUT_IMAGE_DIRECTORY: directory_pair[1], lookup.PAYLOAD: payload}
		updated_embed_list.append(to_embed)

	return updated_embed_list

#### NATIVE ####
def preprocess_native(algorithm_info, to_embed_list):
	cmd = lookup.get_cmd(algorithm_info)
	for to_embed in to_embed_list:
		if lookup.SECRET_TXT_FILE in cmd and lookup.SECRET_TXT_FILE not in to_embed:
			txt_file_path = lookup.create_asset_file(algorithm_info[lookup.ALGORITHM_TYPE], to_embed[lookup.SECRET_TXT_PLAINTEXT])
			to_embed[lookup.SECRET_TXT_FILE] = txt_file_path

		if lookup.OUTPUT_IMAGE_DIRECTORY in cmd and lookup.OUTPUT_IMAGE_DIRECTORY not in to_embed:
			to_embed[lookup.OUTPUT_IMAGE_DIRECTORY] = fs.get_directory(abspath(to_embed[lookup.OUTPUT_IMAGE_PATH]))

	pre_cmd = lookup.get_pre_cmd(algorithm_info)
	pre_cmds = []
	if pre_cmd:
		pre_cmds = [{lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: replace(pre_cmd, to_embed)} for to_embed in to_embed_list]

	return pre_cmds, to_embed_list

def generate_native_cmd(algorithm_info, to_embed):
	cmd = lookup.get_cmd(algorithm_info)
	new_cmd = replace(cmd, to_embed)

	return {lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: [new_cmd]}

def postprocess_native(algorithm_info, embedded_list):
	cmd = lookup.get_post_cmd(algorithm_info)
	post_cmds = []

	if cmd:
		new_cmd = replace(cmd, to_embed)
		post_cmds.append({lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: new_cmd})

	for embedded in embedded_list:
		if lookup.SECRET_TXT_FILE in embedded:
			removal_cmd = ' '.join([lookup.removal_prefix, embedded[lookup.SECRET_TXT_FILE]])
			post_cmds.append({ lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: [removal_cmd] })

		if lookup.INPUT_IMAGE_DIRECTORY in cmd:
			removal_cmd = ' '.join([lookup.removal_directory_prefix, embedded[lookup.INPUT_IMAGE_DIRECTORY]])
			post_cmds.append({ lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: [removal_cmd] })

	return post_cmds

def termination_native(algorithm_info, embedded_list):
	termination_cmds = []
	return termination_cmds

##### DOCKER ####
def preprocess_docker(algorithm_info, to_embed_list):
	"""starts docker command and updates parameters appropriately"""
	cmd = lookup.get_cmd(algorithm_info)
	pre_cmd = lookup.get_pre_cmd(algorithm_info)
	volumes = {}
	updated_embed_list = to_embed_list

	for to_embed in updated_embed_list:
		if lookup.SECRET_TXT_FILE in cmd: 
			txt_file_path = lookup.create_asset_file(algorithm_info[lookup.ALGORITHM_TYPE], to_embed[lookup.SECRET_TXT_PLAINTEXT])
			local_asset_dir = fs.get_directory(abspath(txt_file_path))
			volumes[local_asset_dir] = { 'bind': lookup.asset_dir, 'mode': 'rw'}
			
			asset_filename = fs.get_filename(txt_file_path)
			new_asset_path = join(lookup.asset_dir, asset_filename)
			to_embed[lookup.SECRET_TXT_FILE] = new_asset_path

		if lookup.INPUT_IMAGE_DIRECTORY in cmd:
			docker_input_dir = '/' + fs.get_uuid()
			volumes[abspath(to_embed[lookup.INPUT_IMAGE_DIRECTORY])] = { 'bind': docker_input_dir, 'mode': 'rw'}
			to_embed[lookup.INPUT_IMAGE_DIRECTORY] = docker_input_dir
		else:
			original_input_path = to_embed[lookup.INPUT_IMAGE_PATH]
			original_input_path = abspath(original_input_path)

			local_input_dir = fs.get_directory(original_input_path)
			volumes[local_input_dir] = { 'bind': lookup.input_dir, 'mode': 'rw'}

			input_filename = fs.get_filename(original_input_path)
			new_input_path = join(lookup.input_dir, input_filename)
			to_embed[lookup.INPUT_IMAGE_PATH] = new_input_path

		if lookup.OUTPUT_IMAGE_DIRECTORY in cmd:
			if lookup.OUTPUT_IMAGE_DIRECTORY in to_embed:
				local_output_dir = to_embed[lookup.OUTPUT_IMAGE_DIRECTORY]
			else:
				local_output_dir = fs.get_directory(abspath(to_embed[lookup.OUTPUT_IMAGE_PATH]))

			docker_directory = '/' + fs.get_uuid()
			volumes[local_output_dir] = { 'bind': docker_directory, 'mode': 'rw'}
			to_embed[lookup.OUTPUT_IMAGE_DIRECTORY] = docker_directory
	
		elif lookup.OUTPUT_IMAGE_PATH in to_embed:
			original_output_path = abspath(to_embed[lookup.OUTPUT_IMAGE_PATH])
			local_output_dir = fs.get_directory(original_output_path)
			volumes[local_output_dir] = { 'bind': lookup.output_dir, 'mode': 'rw'}

			output_filename = fs.get_filename(original_output_path)
			new_output_path = join(lookup.output_dir, output_filename)
			to_embed[lookup.OUTPUT_IMAGE_PATH] = new_output_path

	container_id = runner.start_docker(algorithm_info[lookup.DOCKER_IMAGE], volumes=volumes)
	for to_embed in updated_embed_list:
		to_embed[lookup.container_id] = container_id

	pre_cmd = lookup.get_pre_cmd(algorithm_info)
	pre_cmds = []
	if pre_cmd:
		for to_embed in to_embed_list:
			params = [to_embed[lookup.container_id], replace(pre_cmd, to_embed)]
			pre_cmds.append({lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: params})

	return pre_cmds, updated_embed_list

def generate_docker_cmd(algorithm_info, to_embed):
	cmd = lookup.get_cmd(algorithm_info)
	new_cmd = replace(cmd, to_embed)

	params = [to_embed[lookup.container_id], new_cmd]
	if lookup.WORKING_DIR in algorithm_info:
		params.append(algorithm_info[lookup.WORKING_DIR])

	return {lookup.COMMAND_TYPE: lookup.DOCKER, lookup.COMMAND: params}

def postprocess_docker(algorithm_info, embedded_list):
	#need to end the docker process 
	post_cmds = []
	post_cmd = lookup.get_post_cmd(algorithm_info)
	cmd = lookup.get_cmd(algorithm_info)
	
	if post_cmd:
		for embedded in embedded_list:
			new_cmd = replace(post_cmd, embedded)
			params = [embedded[lookup.container_id], new_cmd]
			if lookup.WORKING_DIR in algorithm_info:
				params.append(algorithm_info[lookup.WORKING_DIR])

			docker_cmd = {lookup.COMMAND_TYPE: lookup.DOCKER, lookup.COMMAND: params}
			post_cmds.append(docker_cmd)

	cmd = lookup.get_cmd(algorithm_info)

	for embedded in embedded_list:
		if lookup.SECRET_TXT_FILE in embedded:
			asset_file_name = fs.get_filename(embedded[lookup.SECRET_TXT_FILE])
			asset_directory = lookup.get_algo_asset_dirs()[algorithm_info[lookup.ALGORITHM_TYPE]]

			old_asset_file_path = join(asset_directory, asset_file_name)
			removal_cmd = ' '.join([lookup.removal_prefix, old_asset_file_path])

			post_cmds.append({ lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: [removal_cmd] })

		if lookup.INPUT_IMAGE_DIRECTORY in cmd:
			docker_input_dir = embedded[lookup.INPUT_IMAGE_DIRECTORY]
			removal_cmd = ' '.join([lookup.removal_directory_prefix, embedded[lookup.INPUT_IMAGE_DIRECTORY]])
			params = [embedded[lookup.container_id], removal_cmd]
			post_cmds.append({ lookup.COMMAND_TYPE: lookup.DOCKER, lookup.COMMAND: params })

	return post_cmds

def terimination_docker(algorithm_info, embedded_list):
	termination_cmds = []

	docker_containers = list(set(list(map(lambda embedded: embedded[lookup.container_id], embedded_list))))
	for container_id in docker_containers:
		termination_cmds.append({lookup.COMMAND_TYPE: lookup.END_DOCKER, lookup.COMMAND: [container_id]})

	return termination_cmds

def generate_native(algorithm_info, to_embed_list):
	pre_cmds, updated_embed_list = preprocess_native(algorithm_info, to_embed_list)
	cmds = [generate_native_cmd(algorithm_info, to_embed) for to_embed in updated_embed_list]
	post_cmds = postprocess_native(algorithm_info, updated_embed_list)
	termination_cmds = termination_native(algorithm_info, updated_embed_list)
	return pre_cmds, cmds, post_cmds, termination_cmds	

def generate_docker(algorithm_info, to_embed_list):
	pre_cmds, updated_embed_list = preprocess_docker(algorithm_info, to_embed_list)
	cmds = [generate_docker_cmd(algorithm_info, to_embed) for to_embed in updated_embed_list]
	post_cmds = postprocess_docker(algorithm_info, updated_embed_list)
	termination_cmds = terimination_docker(algorithm_info, updated_embed_list)
	return pre_cmds, cmds, post_cmds, termination_cmds	

def generate_commands(algorithm_info, to_embed_list):
	command_type = algorithm_info[lookup.COMMAND_TYPE]
	generate_function = {
		lookup.DOCKER: generate_docker,
		lookup.NATIVE: generate_native,
	}[command_type]

	if lookup.INPUT_IMAGE_DIRECTORY in lookup.get_cmd(algorithm_info):
		to_embed_list = process_directories(algorithm_info, to_embed_list)

	return generate_function(algorithm_info, to_embed_list)