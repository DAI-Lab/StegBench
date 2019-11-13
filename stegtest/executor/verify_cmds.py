import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs
import stegtest.utils.generator as generator
import stegtest.executor.runner as runner
import os

from os.path import abspath, join

def replace(cmd:str, replacements):
	for replacement_key in replacements:
		cmd = cmd.replace(replacement_key, replacements[replacement_key])
	return cmd

#### NATIVE ####
def preprocess_native(algorithm_info, to_verify_list):
	return [], to_verify_list

def generate_native_cmd(algorithm_info, to_verify):
	cmd = lookup.get_verify_cmd(algorithm_info)
	new_cmd = replace(cmd, to_verify)

	if lookup.PIPE_OUTPUT in algorithm_info:
		result_file = generator.generate_verify_file(algorithm_info, to_verify)
		write_to_result_cmd = ' > ' + result_file

		new_cmd += write_to_result_cmd

	return {lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: [new_cmd]}

def postprocess_native(algorithm_info, verified_list):
	post_cmds = []
	return post_cmds

def termination_native(algorithm_info, verified_list):
	termination_cmds = []

	for verified in verified_list:
		removal_cmd = ' '.join([lookup.removal_prefix, generator.generate_verify_file(algorithm_info, verified)])
		termination_cmds.append({ lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: [removal_cmd] })

	return termination_cmds

##### DOCKER ####
def preprocess_docker(algorithm_info, to_verify_list):
	"""starts docker command and updates parameters appropriately"""
	image_name = algorithm_info[lookup.DOCKER_IMAGE]
	cmd = lookup.get_verify_cmd(algorithm_info)
	volumes = {}

	if lookup.VERIFY_TXT_FILE in cmd:
		asset_directory = abspath(lookup.get_algo_asset_dirs()[lookup.embeddor])
		volumes[asset_directory] = { 'bind': lookup.asset_dir, 'mode': 'rw'}
		for to_verify in to_verify_list:
			to_verify[lookup.VERIFY_TXT_FILE] = generator.generate_verify_file(algorithm_info, to_verify)

	for to_verify in to_verify_list:
		assert(lookup.INPUT_IMAGE_PATH in to_verify)
		original_input_path = to_verify[lookup.INPUT_IMAGE_PATH]
		original_input_path = abspath(original_input_path)

		local_input_dir = fs.get_directory(original_input_path)
		volumes[local_input_dir] = { 'bind': lookup.input_dir, 'mode': 'rw'}

		input_filename = fs.get_filename(original_input_path)
		new_input_path = join(lookup.input_dir, input_filename)
		to_verify[lookup.INPUT_IMAGE_PATH] = new_input_path


	container_id = runner.start_docker(image_name, volumes=volumes)
	for to_verify in to_verify_list:
		to_verify[lookup.container_id] = container_id

	return [], to_verify_list

def generate_docker_cmd(algorithm_info, to_verify):
	cmd = lookup.get_verify_cmd(algorithm_info)
	new_cmd = replace(cmd, to_verify)

	params = [to_verify[lookup.container_id], new_cmd]
	if lookup.WORKING_DIR in algorithm_info:
		params.append(algorithm_info[lookup.WORKING_DIR])

	return {lookup.COMMAND_TYPE: lookup.DOCKER, lookup.COMMAND: params}

def postprocess_docker(algorithm_info, verified_list):
	post_cmds = []
	post_cmd = lookup.get_post_cmd(algorithm_info)
	return post_cmds

def terimination_docker(algorithm_info, verified_list):
	termination_cmds = []
	cmd = lookup.get_verify_cmd(algorithm_info)

	docker_containers = list(set(list(map(lambda verified: verified[lookup.container_id], verified_list))))
	for container_id in docker_containers:
		termination_cmds.append({lookup.COMMAND_TYPE: lookup.END_DOCKER, lookup.COMMAND: [container_id]})

	for verified in verified_list:
		asset_file_name = fs.get_filename(generator.generate_verify_file(algorithm_info, verified))
		asset_directory = lookup.get_algo_asset_dirs()[algorithm_info[lookup.ALGORITHM_TYPE]]

		old_asset_file_path = join(asset_directory, asset_file_name)
		removal_cmd = ' '.join([lookup.removal_prefix, old_asset_file_path])

		termination_cmds.append({ lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: [removal_cmd] })

	return termination_cmds

def generate_native(algorithm_info, to_verify_list):
	pre_cmds, updated_verify_list = preprocess_native(algorithm_info, to_verify_list)
	cmds = [generate_native_cmd(algorithm_info, to_verify) for to_verify in updated_verify_list]
	post_cmds = postprocess_native(algorithm_info, updated_verify_list)
	termination_cmds = termination_native(algorithm_info, updated_verify_list)
	return pre_cmds, cmds, post_cmds, termination_cmds	

def generate_docker(algorithm_info, to_verify_list):
	pre_cmds, updated_verify_list = preprocess_docker(algorithm_info, to_verify_list)
	cmds = [generate_docker_cmd(algorithm_info, to_verify) for to_verify in updated_verify_list]
	post_cmds = postprocess_docker(algorithm_info, updated_verify_list)
	termination_cmds = terimination_docker(algorithm_info, updated_verify_list)
	return pre_cmds, cmds, post_cmds, termination_cmds	

def generate_commands(algorithm_info, to_verify_list):
	command_type = algorithm_info[lookup.COMMAND_TYPE]
	generate_function = {
		lookup.DOCKER: generate_docker,
		lookup.NATIVE: generate_native,
	}[command_type]

	return generate_function(algorithm_info, to_verify_list)