from os import listdir
from os.path import isfile, join, abspath
from collections import defaultdict

import ast
import stegtest.utils.filesystem as fs
import stegtest.utils.lookup as lookup
import stegtest.utils.generator as generator

import configparser
import re

def is_config_file(file):
	return fs.get_extension(file) == '.ini'

def validate_native():
	return True

def validate_docker(config):
	#TODO assert facts about the image and the command
	assert(config[lookup.DOCKER_IMAGE])
	assert(config[lookup.COMMAND])

def validate_native(config):
	assert(config[lookup.COMMAND])

def validate_class(config):
	raise NotImplementedError

def validate_config(config):
	compatible_types = config[lookup.compatible_descriptor]
	allowed_types = lookup.all_supported_types()
	for img_type in compatible_types:
		assert(img_type in allowed_types)

	validate_function = {
		lookup.DOCKER: validate_docker,
		lookup.NATIVE: validate_native,
		lookup.CLASS: validate_class
	}[config[lookup.COMMAND_TYPE]]

	validate_function(config)

def process_algorithm(algorithm_type, algorithm_dict, config_file_path):
	master_file = lookup.get_algo_master_files()[algorithm_type]
	master_file_path = lookup.get_all_files()[master_file]

	data_to_write = [[fs.get_uuid(), name, config_file_path] for name in algorithm_dict.keys()]
	fs.write_to_csv_file(master_file_path, data_to_write)

def process_configs(config_dict, config_file_path):
	config_embeddors = {k:v for (k,v) in config_dict.items() if config_dict[k][lookup.ALGORITHM_TYPE] == lookup.embeddor}
	config_detectors = {k:v for (k,v) in config_dict.items() if config_dict[k][lookup.ALGORITHM_TYPE] == lookup.detector}

	process_algorithm(lookup.embeddor, config_embeddors, config_file_path)
	process_algorithm(lookup.detector, config_detectors, config_file_path)

def get_config_from_file(config_file_path):
	config_dict = fs.read_config_file(config_file_path)
	for config_name in config_dict:
		config = config_dict[config_name]
		if lookup.compatible_descriptor in config:
			config[lookup.compatible_descriptor] = ast.literal_eval(config[lookup.compatible_descriptor])

		if lookup.embedding_descriptor in config:
			config[lookup.embedding_descriptor] = float(config[lookup.embedding_descriptor])

		validate_config(config)

	return config_dict

def get_config_files(config_directory): #TODO push this to filesystem
	assert(fs.dir_exists(config_directory))
	config_files = [abspath(join(config_directory, f)) for f in listdir(config_directory) if is_config_file(f)]
	return config_files

def process_config_file(config_file_path):
	config_file_path = abspath(config_file_path)
	config_dict = get_config_from_file(config_file_path)

	print('starting processing of config file: ' + config_file_path)
	process_configs(config_dict, config_file_path)
	print('processing of file complete')

def process_config_directory(config_directory):
	config_files = get_config_files(config_directory)
	print('processing config directory: ' + config_directory)
	for config_file_path in config_files:
		process_config_file(config_file_path)

	print('processing of directory complete')

def build_configs(configs):
	for config in configs:
		build_config_file(config[INSTALL][0])

def compile_csv_directory(algorithm_info, source_db):
	algorithm_uuid = algorithm_info[lookup.uuid_descriptor]
	asset_dir = abspath(lookup.get_algo_asset_dirs()[lookup.detector])

	directory = list(set([fs.get_directory(image[lookup.file_path]) for image in lookup.get_image_list(source_db)]))
	assert(len(directory) == 1)
	directory = directory[0]
	result_csv_file = algorithm_uuid + '_' + fs.get_filename(directory) + '.csv'
	result_csv_file = join(asset_dir, result_csv_file)

	data = fs.read_csv_file(result_csv_file)
	results = []

	for result in data:
		file_name = result[0]
		file_result = result[1]

		if file_result == 'True':
			results.append({lookup.file_path: file_name, lookup.result: True})
		else:
			results.append({lookup.file_path: file_name, lookup.result: False})

	return results

def compile_csv_results(algorithm_info, source_db):
	algorithm_uuid = algorithm_info[lookup.uuid_descriptor]
	asset_dir = abspath(lookup.get_algo_asset_dirs()[lookup.detector])

	image_files = lookup.get_image_list(source_db)
	image_filepath = [abspath(file[lookup.file_path]) for file in image_files]

	result_files = [algorithm_uuid + '_' + fs.get_filename(file[lookup.file_path], extension=False) + '.csv' for file in image_files]
	result_files = [join(asset_dir, result_file) for result_file in result_files]

	raise NotImplementedError

def compile_txt_results(algorithm_info, source_db):
	#TODO THIS IS NOT TESTED AND IS HACKY -- NEED TO VALIDATE THIS PIPELINE
	algorithm_uuid = algorithm_info[lookup.uuid_descriptor]
	asset_dir = abspath(lookup.get_algo_asset_dirs()[lookup.detector])
	
	image_files = lookup.get_image_list(source_db)
	image_filepath = [abspath(file[lookup.file_path]) for file in image_files]

	result_files = [algorithm_uuid + '_' + fs.get_filename(file[lookup.file_path], extension=False) + '.txt' for file in image_files]
	result_files = [join(asset_dir, result_file) for result_file in result_files]

	yes_filter = algorithm_info[lookup.regex_filter_yes]
	no_filter = algorithm_info[lookup.regex_filter_no]

	results = []

	for idx, file in enumerate(result_files):
		file_result = fs.read_txt_file(file)
		file_result = ' '.join(file_result)

		print(file_result)

		stego = re.search(yes_filter, file_result)
		cover = re.search(no_filter, file_result)
		assert (stego or cover and not (stego and cover))

		if stego:
			results.append({lookup.file_path: image_filepath[idx], lookup.result: True})
		else:
			results.append({lookup.file_path: image_filepath[idx], lookup.result: False})

	return results

def compile_results(algorithm_info, source_db):
	cmd = lookup.get_cmd(algorithm_info)
	if lookup.PIPE_OUTPUT in algorithm_info and lookup.INPUT_IMAGE_PATH in cmd:
		return compile_txt_results(algorithm_info, source_db)
	elif lookup.RESULT_CSV_FILE in algorithm_info and lookup.INPUT_IMAGE_PATH in cmd:
		return compile_csv_results(algorithm_info, source_db)
	elif lookup.INPUT_IMAGE_DIRECTORY in cmd:
		return compile_csv_directory(algorithm_info, source_db)

	raise NotImplementedError

def verify_embedding(verify_db, embeddors):
	embeddor_results = defaultdict(list)
	image_files = lookup.get_image_list(verify_db)

	for image_file in image_files:
		image_file[lookup.INPUT_IMAGE_PATH] = image_file[lookup.file_path]
		embeddor_uuid = image_file[lookup.uuid_descriptor]
		verify_txt_file = generator.generate_verify_file(embeddors[embeddor_uuid], image_file)

		asset_file_name = fs.get_filename(verify_txt_file)
		asset_directory = lookup.get_algo_asset_dirs()[lookup.embeddor]
		verify_file_path = abspath(join(asset_directory, asset_file_name))

		data = fs.read_txt_file(verify_file_path)

		if (len(data[0])) == int(image_file[lookup.secret_txt_length]):
			verification_result = True
		else:
			verification_result = False

		embeddor_results[embeddor_uuid].append({lookup.INPUT_IMAGE_PATH: image_file[lookup.INPUT_IMAGE_PATH], lookup.result: verification_result})

	return embeddor_results


