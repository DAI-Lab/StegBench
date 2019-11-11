import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs
import stegtest.algo.runner as runner
import os

from os.path import abspath, join

def replace(cmd:str, replacements):
	for replacement_key in replacements:
		cmd = cmd.replace(replacement_key, replacements[replacement_key])
	return cmd

def generate_temp_file_name(algorithm_info, cmd:str, to_detect):
	output_file_name = algorithm_info[lookup.uuid_descriptor]

	output_directory = None
	if algorithm_info[lookup.COMMAND_TYPE] == lookup.DOCKER:
		output_directory = lookup.result_dir
	else:
		output_directory = lookup.get_algo_asset_dirs()[lookup.detector]

	print(output_directory)

	if lookup.INPUT_IMAGE_PATH in cmd:
		assert(lookup.INPUT_IMAGE_PATH in to_detect)
		output_file_name += '_' + fs.get_filename(to_detect[lookup.INPUT_IMAGE_PATH], extension=False)


	elif lookup.INPUT_IMAGE_DIRECTORY in cmd:
		assert(lookup.INPUT_IMAGE_DIRECTORY in to_detect)
		#TODO NEED TO FIX THIS PART
		output_file_name += '_' + fs.get_filename(to_detect[lookup.INPUT_IMAGE_DIRECTORY])

	output_file_name += '.txt'

	return join(output_directory , output_file_name)

def generate_result_file_name(algorithm_info, cmd:str, to_detect):
	output_file_name = algorithm_info[lookup.uuid_descriptor]

	# output_directory = None
	# if algorithm_info[lookup.COMMAND_TYPE] == lookup.DOCKER:
	# 	output_directory = lookup.result_dir
	# else:
	
	output_directory = abspath(lookup.get_algo_asset_dirs()[lookup.detector])


	if lookup.INPUT_IMAGE_PATH in cmd:
		assert(lookup.INPUT_IMAGE_PATH in to_detect)
		output_file_name += '_' + fs.get_filename(to_detect[lookup.INPUT_IMAGE_PATH], extension=False)


	elif lookup.INPUT_IMAGE_DIRECTORY in cmd:
		assert(lookup.INPUT_IMAGE_DIRECTORY in to_detect)
		#TODO NEED TO FIX THIS PART
		output_file_name += '_' + fs.get_filename(to_detect[lookup.INPUT_IMAGE_DIRECTORY])

	output_file_name += '.txt'

	return join(output_directory , output_file_name)

#### NATIVE ####
def preprocess_native(algorithm_info, to_detect_list):
	#probably need to transform from directory to list, vice versa.
	cmd = lookup.get_cmd(algorithm_info)

	if lookup.INPUT_IMAGE_DIRECTORY in cmd:
		raise NotImplementedError

	if lookup.OUTPUT_IMAGE_DIRECTORY in cmd:
		raise NotImplementedError

	return [], to_detect_list

def generate_native_cmd(algorithm_info, to_detect):
	#need to do regular substitutions
	cmd = lookup.get_cmd(algorithm_info)
	new_cmd = replace(cmd, to_detect)

	if algorithm_info[lookup.PIPE_OUTPUT]:
		result_file = generate_result_file_name(algorithm_info, cmd, to_detect)
		write_to_result_cmd = ' > ' + result_file

		new_cmd += write_to_result_cmd
	#stuff to do with piping output

	return {lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: [new_cmd]}

def postprocess_native(algorithm_info, detected_list):
	post_cmds = []
	post_cmd = lookup.get_post_cmd(algorithm_info)
	if post_cmd is None:
		return post_cmds

	for to_detect in detected_list:
		generated_post_cmd = replace(post_cmd, detected_list)
		post_cmds.append({lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: generated_post_cmd})

	#need to conglomerate results here

	return post_cmds

def termination_native(algorithm_info, detected_list):
	termination_cmds = []

	# if algorithm_info[lookup.PIPE_OUTPUT]:
	# 	cmd = lookup.get_cmd(algorithm_info)
	# 	removal_prefix = 'rm'
	# 	for detected in detected_list:
	# 		result_file = generate_result_file_name(algorithm_info, cmd, detected)
	# 		removal_cmd = ' '.join([removal_prefix, result_file])

	# 		termination_cmds.append({lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: [removal_cmd]})

	return termination_cmds

##### DOCKER ####
def preprocess_docker(algorithm_info, to_detect_list):
	"""starts docker command and updates parameters appropriately"""
	image_name = algorithm_info[lookup.DOCKER_IMAGE]
	cmd = lookup.get_cmd(algorithm_info)
	volumes = {}

	#inputs
	if lookup.INPUT_IMAGE_DIRECTORY in cmd:
		raise NotImplementedError
		#need to update the commands 

	for to_detect in to_detect_list:
		assert(lookup.INPUT_IMAGE_PATH in to_detect)
		original_input_path = to_detect[lookup.INPUT_IMAGE_PATH]
		original_input_path = abspath(original_input_path)

		local_input_dir = fs.get_directory(original_input_path)
		volumes[local_input_dir] = { 'bind': lookup.input_dir, 'mode': 'rw'}

		input_filename = fs.get_filename(original_input_path)
		new_input_path = join(lookup.input_dir, input_filename)
		to_detect[lookup.INPUT_IMAGE_PATH] = new_input_path

	result_directory = abspath(lookup.get_algo_asset_dirs()[lookup.detector])
	assert(fs.dir_exists(result_directory))
	
	volumes[result_directory] = { 'bind': lookup.result_dir, 'mode': 'rw' }

	container_id = runner.start_docker(image_name, volumes=volumes)
	for to_detect in to_detect_list:
		to_detect[lookup.container_id] = container_id

	return [], to_detect_list

def generate_docker_cmd(algorithm_info, to_detect):
	cmd = lookup.get_cmd(algorithm_info)
	new_cmd = replace(cmd, to_detect)

	if algorithm_info[lookup.PIPE_OUTPUT]:
		#need to return a native command for now -- HACKY FIX
		result_file_path = generate_result_file_name(algorithm_info, cmd, to_detect)
		write_to_result_cmd = ' > ' + result_file_path
		docker_cmd = ' '.join(['docker exec', str(to_detect[lookup.container_id]), new_cmd, write_to_result_cmd])
		return {lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: [docker_cmd]}

	params = [to_detect[lookup.container_id], new_cmd]
	if lookup.WORKING_DIR in algorithm_info:
		params.append(algorithm_info[lookup.WORKING_DIR])

	return {lookup.COMMAND_TYPE: lookup.DOCKER, lookup.COMMAND: params}

def postprocess_docker(algorithm_info, detected_list):
	#need to end the docker process 
	post_cmds = []
	post_cmd = lookup.get_post_cmd(algorithm_info)

	if post_cmd:
		for detected in detected_list:
			new_cmd = replace(post_cmd, detected)
			params = [detected[lookup.container_id], new_cmd]
			if lookup.WORKING_DIR in algorithm_info:
				params.append(algorithm_info[lookup.WORKING_DIR])

			docker_cmd = {lookup.COMMAND_TYPE: lookup.DOCKER, lookup.COMMAND: params}
			post_cmds.append(docker_cmd)

	return post_cmds

def terimination_docker(algorithm_info, detected_list):
	termination_cmds = []

	docker_containers = list(set(list(map(lambda detector: detector[lookup.container_id], detected_list))))
	for container_id in docker_containers:
		termination_cmds.append({lookup.COMMAND_TYPE: lookup.END_DOCKER, lookup.COMMAND: [container_id]})

	return termination_cmds

#### CLASS ####
def preprocess_class(algorithm_info, to_detect_list):
	raise NotImplementedError

def generate_class_cmd(algorithm_info, to_detect):
	raise NotImplementedError

def postprocess_class(algorithm_info, detected_list):
	raise NotImplementedError

def termination_class(algorithm_info, detected_list):
	raise NotImplementedError

# def process_results(algorithm_info, detected_list, result_file):
# 	raise NotImplementedError

def generate_commands(algorithm_info, to_detect_list, result_file=None):
	command_type = algorithm_info[lookup.COMMAND_TYPE]

	preprocess_function = {
		lookup.DOCKER: preprocess_docker,
		lookup.NATIVE: preprocess_native,
		lookup.CLASS: preprocess_class,
	}[command_type]

	pre_cmds, updated_detect_list = preprocess_function(algorithm_info, to_detect_list)

	generate_function = {
		lookup.DOCKER: generate_docker_cmd,
		lookup.NATIVE: generate_native_cmd,
		lookup.CLASS: generate_class_cmd
	}[command_type]

	cmds = [generate_function(algorithm_info, to_detect) for to_detect in updated_detect_list]

	postprocess_function = {
		lookup.DOCKER: postprocess_docker,
		lookup.NATIVE: postprocess_native,
		lookup.CLASS: postprocess_class
	}[command_type]

	post_cmds = postprocess_function(algorithm_info, updated_detect_list)

	termination_function = {
		lookup.DOCKER: terimination_docker,
		lookup.NATIVE: termination_native,
		lookup.CLASS: termination_class
	}[command_type]

	termination_cmds = termination_function(algorithm_info, updated_detect_list)
	return pre_cmds, cmds, post_cmds, termination_cmds
