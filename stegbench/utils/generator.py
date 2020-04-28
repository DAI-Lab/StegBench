import stegbench.utils.lookup as lookup
import stegbench.utils.filesystem as fs
import random
import string

from os.path import join, abspath

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

def generate_password(byte_length=20):
	return generate_random_string(byte_length)

def replace(cmd:str, replacements):
	for replacement_key in replacements:
		cmd = cmd.replace(replacement_key, str(replacements[replacement_key]))
	return cmd

def get_directories(params):
	directories = set()
	for param in params:
		if lookup.INPUT_IMAGE_PATH in param:
			directories.add(fs.get_directory(abspath(param[lookup.INPUT_IMAGE_PATH])))
		elif lookup.INPUT_IMAGE_DIRECTORY in param:
			directories.add(abspath(param[lookup.INPUT_IMAGE_DIRECTORY]))

	directories = list(directories)
	directories = list(map(lambda directory: {lookup.INPUT_IMAGE_DIRECTORY: directory}, directories))

	return directories

def generate_verify_file(algorithm_info, to_verify):
	command_type = algorithm_info[lookup.COMMAND_TYPE]
	if command_type == lookup.DOCKER:
		file_dir = lookup.asset_dir
	else:
		file_dir = abspath(lookup.get_algo_asset_dirs()[lookup.embeddor])

	file_name = algorithm_info[lookup.uuid_descriptor] + '_' +fs.get_filename(to_verify[lookup.INPUT_IMAGE_PATH], extension=False) + '.txt'
	file_path = join(file_dir, file_name)

	return file_path

def generate_result_file(algorithm_info, to_detect, file_type, temp=False):
	output_file_name = algorithm_info[lookup.uuid_descriptor]
	cmd = lookup.get_cmd(algorithm_info)
	
	if algorithm_info[lookup.COMMAND_TYPE] == lookup.DOCKER and lookup.PIPE_OUTPUT not in algorithm_info: #hacky fix for piping output
		output_directory = lookup.result_dir
	else:
		output_directory = abspath(lookup.get_algo_asset_dirs()[lookup.detector])

	if lookup.INPUT_IMAGE_PATH in cmd:
		output_file_name += '_' + fs.get_filename(to_detect[lookup.INPUT_IMAGE_PATH], extension=False)


	elif lookup.INPUT_IMAGE_DIRECTORY in cmd:
		output_file_name += '_' + fs.get_filename(to_detect[lookup.INPUT_IMAGE_DIRECTORY])

	if temp:
		output_file_name += '-temp'

	output_file_name += '.' + file_type
	return join(output_directory , output_file_name)

def generate_output_list(algorithm_info, output_directory:str, input_list:dict):
	target_directory = output_directory

	output_list = []
	for file in input_list:
		file_type = file[lookup.image_type]

		if lookup.OUTPUT_FILE in algorithm_info:
			replacements = {lookup.INPUT_IMAGE_NAME: fs.get_filename(abspath(file[lookup.file_path]), extension=False)}
			output_file_name = replace(algorithm_info[lookup.OUTPUT_FILE], replacements)
		else:
			output_file_name = fs.get_uuid()

		output_file = fs.create_name_from_uuid(output_file_name, file_type)
		output_file_path = join(target_directory, output_file)
		output_list.append(output_file_path)

	return output_list

