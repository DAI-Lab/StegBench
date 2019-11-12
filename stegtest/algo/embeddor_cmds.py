import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs
import stegtest.algo.runner as runner
import os
from collections import defaultdict

from os.path import abspath, join

removal_prefix = 'rm'

def replace(cmd:str, replacements):
	for replacement_key in replacements:
		cmd = cmd.replace(replacement_key, str(replacements[replacement_key]))
	return cmd

#### NATIVE ####
def preprocess_native(algorithm_info, to_embed_list):
	#probably need to transform from directory to list, vice versa.
	cmd = lookup.get_cmd(algorithm_info)
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
	cmd = lookup.get_cmd(algorithm_info)
	new_cmd = replace(cmd, to_embed)

	return {lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: [new_cmd]}

def postprocess_native(algorithm_info, embedded_list):
	cmd = lookup.get_post_cmd(algorithm_info)
	if cmd is None:
		return []

	new_cmd = replace(cmd, to_embed)
	return [{lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: new_cmd}]

def termination_native(algorithm_info, embedded_list):
	cmd = lookup.get_cmd(algorithm_info)

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
	cmd = lookup.get_cmd(algorithm_info)
	volumes = {}

	updated_embed_list = to_embed_list

	if lookup.SECRET_TXT_FILE in cmd: #creates secret txt file
		for to_embed in updated_embed_list:
			txt_file_path = lookup.create_asset_file(algorithm_info[lookup.ALGORITHM_TYPE], to_embed[lookup.SECRET_TXT_PLAINTEXT])
			local_asset_dir = fs.get_directory(txt_file_path)
			volumes[local_asset_dir] = { 'bind': lookup.asset_dir, 'mode': 'rw'}
			asset_filename = fs.get_filename(txt_file_path)
			new_asset_path = join(lookup.asset_dir, asset_filename)
			to_embed[lookup.SECRET_TXT_FILE] = new_asset_path

	if lookup.INPUT_IMAGE_DIRECTORY in cmd: #mount input directory 
		directories = lookup.get_directories(updated_embed_list)
		sorted_by_directory = defaultdict(list)
		for to_embed in updated_embed_list:
			sorted_by_directory[fs.get_directory(abspath(to_embed[lookup.INPUT_IMAGE_PATH]))].append(to_embed)

		new_embed_list = []
		for input_directory in sorted_by_directory:
			files = sorted_by_directory[input_directory]
			payloads = set(list(map(lambda f: f[lookup.PAYLOAD], files)))
			output_directories = set(list(map(lambda f: fs.get_directory(abspath(f[lookup.OUTPUT_IMAGE_PATH])), files)))
			assert(len(payloads) == 1)
			assert(len(output_directories) == 1)
			payload = payloads.pop()
			output_directory = output_directories.pop()

			docker_input_dir = '/' + fs.get_uuid()
			volumes[input_directory] = { 'bind': docker_input_dir, 'mode': 'rw'}

			docker_output_dir = '/' + fs.get_uuid()
			volumes[output_directory] = { 'bind': docker_output_dir, 'mode': 'rw'}

			new_embed_list.append({lookup.INPUT_IMAGE_DIRECTORY: docker_input_dir, lookup.PAYLOAD: payload, lookup.OUTPUT_IMAGE_DIRECTORY: docker_output_dir})

		updated_embed_list = new_embed_list

	else: #mount input path volumes
		for to_embed in updated_embed_list:
			original_input_path = to_embed[lookup.INPUT_IMAGE_PATH]
			original_input_path = abspath(original_input_path)

			local_input_dir = fs.get_directory(original_input_path)
			volumes[local_input_dir] = { 'bind': lookup.input_dir, 'mode': 'rw'}

			input_filename = fs.get_filename(original_input_path)
			new_input_path = join(lookup.input_dir, input_filename)
			to_embed[lookup.INPUT_IMAGE_PATH] = new_input_path

		#mount output paths for directory
		if lookup.OUTPUT_IMAGE_DIRECTORY in cmd:
			for to_embed in updated_embed_list:
				docker_directory = '/' + fs.get_uuid()
				local_output_dir = fs.get_directory(abspath(to_embed[lookup.OUTPUT_IMAGE_PATH]))
				volumes[local_output_dir] = { 'bind': docker_directory, 'mode': 'rw'}
				to_embed[lookup.OUTPUT_IMAGE_DIRECTORY] = docker_directory

		elif look.OUTPUT_IMAGE_PATH in cmd:
			for to_embed in updated_embed_list:
				original_output_path = abspath(to_embed[lookup.OUTPUT_IMAGE_PATH])
				local_output_dir = fs.get_directory(original_output_path)
				volumes[local_output_dir] = { 'bind': lookup.output_dir, 'mode': 'rw'}

				output_filename = fs.get_filename(original_output_path)
				new_output_path = join(lookup.output_dir, output_filename)
				to_embed[lookup.OUTPUT_IMAGE_PATH] = new_output_path

	container_id = runner.start_docker(image_name, volumes=volumes)
	for to_embed in updated_embed_list:
		to_embed[lookup.container_id] = container_id

	return [], updated_embed_list

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

	cmd = lookup.get_cmd(algorithm_info)

	if lookup.SECRET_TXT_FILE in cmd:
		for embedded in embedded_list:
			asset_file_name = fs.get_filename(embedded[lookup.SECRET_TXT_FILE])
			asset_directory = lookup.get_algo_asset_dirs()[algorithm_info[lookup.ALGORITHM_TYPE]]

			old_asset_file_path = join(asset_directory, asset_file_name)
			removal_cmd = ' '.join([removal_prefix, old_asset_file_path])

			termination_cmds.append({ lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: [removal_cmd] })

	return termination_cmds

def generate_native(algorithm_info, to_detect_list):
	pre_cmds, updated_detect_list = preprocess_native(algorithm_info, to_detect_list)
	cmds = [generate_native_cmd(algorithm_info, to_detect) for to_detect in updated_detect_list]
	post_cmds = postprocess_native(algorithm_info, updated_detect_list)
	termination_cmds = termination_native(algorithm_info, updated_detect_list)
	return pre_cmds, cmds, post_cmds, termination_cmds	

def generate_docker(algorithm_info, to_detect_list):
	pre_cmds, updated_detect_list = preprocess_docker(algorithm_info, to_detect_list)
	cmds = [generate_docker_cmd(algorithm_info, to_detect) for to_detect in updated_detect_list]
	post_cmds = postprocess_docker(algorithm_info, updated_detect_list)
	termination_cmds = terimination_docker(algorithm_info, updated_detect_list)
	return pre_cmds, cmds, post_cmds, termination_cmds	

def generate_commands(algorithm_info, to_detect_list):
	command_type = algorithm_info[lookup.COMMAND_TYPE]
	generate_function = {
		lookup.DOCKER: generate_docker,
		lookup.NATIVE: generate_native,
	}[command_type]

	return generate_function(algorithm_info, to_detect_list)