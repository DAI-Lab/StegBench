from os import listdir
from os.path import isfile, join, abspath

import stegtest.utils.filesystem as fs
import stegtest.utils.lookup as lookup
import stegtest.utils.bash as bash

import configparser

#METADATA
ALGORITHM_TYPE = 'algorithm_type'
COMMAND_TYPE = 'command_type'
COMPATIBLE_TYPES  = 'compatible_types'
MAX_EMBEDDING_RATIO = 'max_embedding_ratio'

#APPLICATION_SPECIFIC
DOCKER_IMAGE = 'docker_image'

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
OUTPUT_FILE_NAME = 'OUTPUT_FILE_NAME'
OUTPUT_FILE_PATH = 'OUTPUT_FILE_PATH'

# #FLAGS
# FLAGS = 'FLAGS'
# BATCH_PROCESSING_FLAG = 'BATCH_PROCESSING_FLAG'
# SINGLE_PROCESSING_FLAG = 'SINGLE_PROCESSING_FLAG'

# #INSTALL
# INSTALL = 'INSTALL'
# DOWNLOAD_CMD = 'DOWNLOAD_CMD'
# INSTALL_CMD = 'INSTALL_CMD'

# #RUN
# RUN = 'RUN'
# SINGLE_PROCESSING_CMD = 'SINGLE_PROCESSING_CMD'
# BATCH_PROCESSING_CMD = 'BATCH_PROCESSING_CMD'

# #PARAMS
# PARAMS = 'PARAMS'
# RANGE = 'RANGE'

# #DEFAULT VALUES
# NONE = 'NONE'
# DOCKER_DEFAULT = 'DOCKER_DEFAULT'

# config_template = {
# 	METADATA: [NAME, TYPE, COMPATIBLE_TYPES, APPLICATION_TYPE],
# 	FLAGS: [BATCH_PROCESSING_FLAG, SINGLE_PROCESSING_FLAG],
# 	INSTALL: [DOWNLOAD_CMD, INSTALL_CMD],
# 	RUN: [SINGLE_PROCESSING_CMD, BATCH_PROCESSING_CMD],
# 	PARAMS: [PARAMS, RANGE]
# }


#META

#need a way to define the possible values 
#APPLICATION_TYPES = 'PYTHON', 'DOCKER', 'BASH'
#COMPATIBLE_TYPES = ''

def is_config_file(file):
	return fs.get_extension(file) == '.ini'

def process_embeddor(embeddors_dict, config_file_path):
	embeddor_file = lookup.get_all_files()[lookup.embeddors_file]
	data_to_write = []
	for name in embeddors_dict.keys():
		embeddor_data = embeddors_dict[name]
		data = [fs.get_uuid(), name, config_file_path]

		data_to_write.append(data)

	fs.write_to_csv_file(embeddor_file, data_to_write)

def process_detector(detectors_dict, config_file_path):
	detector_file = lookup.get_all_files()[lookup.detectors_file]
	data_to_write = []
	for name in detectors_dict.keys():
		detector_data = detectors_dict[name]
		data = [fs.get_uuid(), name, detector_data[COMPATIBLE_TYPES], config_file_path]

		data_to_write.append(data)

	fs.write_to_csv_file(detector_file, data_to_write)

def process_configs(stegtest_directory, config_dict, config_file_path):
	config_embeddors = {k:v for (k,v) in config_dict.items() if config_dict[k][ALGORITHM_TYPE] == lookup.embeddor}
	config_detectors = {k:v for (k,v) in config_dict.items() if config_dict[k][ALGORITHM_TYPE] == lookup.detector}

	process_embeddor(config_embeddors, config_file_path)
	process_detector(config_detectors, config_file_path)

def get_config_files(config_directory):
	assert(fs.dir_exists(config_directory))
	config_files = [abspath(join(config_directory, f)) for f in listdir(config_directory) if is_config_file(f)]
	return config_files

def initialize_configs(stegtest_directory, config_directory):
	config_files = get_config_files(config_directory)
	config_dict = [(fs.read_config_file(file_path), abspath(file_path)) for file_path in config_files]

	for file_path in config_files:
		config_dict = fs.read_config_file(file_path)
		abs_file_path = abspath(file_path)

		process_configs(stegtest_directory, config_dict, abs_file_path)

def build_configs(configs):
	for config in configs:
		build_config_file(config[INSTALL][0])

def get_metadata_vars():
	return [NAME, TYPE, COMPATIBLE_TYPES, APPLICATION_TYPE]

def get_flag_vars():
	return [BATCH_PROCESSING_FLAG, SINGLE_PROCESSING_FLAG]

def get_install_vars():
	return [DOWNLOAD_CMD, INSTALL_CMD]

def get_run_vars():
	return [BATCH_PROCESSING_CMD, SINGLE_PROCESSING_CMD]

def get_default_values():
	return [NONE, DOCKER_DEFAULT]

def get_all_vars():
	return get_metadata_vars + get_flag_vars + get_install_vars + get_run_vars

def check_config_info(config_details):
	assert(set(config_details[METADATA][0].keys()).difference(set(get_metadata_vars())) != 0)
	assert(set(config_details[FLAGS][0].keys()).difference(set(get_flag_vars())) != 0)
	assert(set(config_details[INSTALL][0].keys()).difference(set(get_install_vars())) != 0)
	assert(set(config_details[RUN][0].keys()).difference(set(get_run_vars())) != 0)

def translate_DOWNLOAD():
	DOCKER_DEFAULT_TRANSLATION = 'docker pull'
	replacements = { DOCKER_DEFAULT: DOCKER_DEFAULT_TRANSLATION }
	return replacements

def translate_INSTALL():
	DOCKER_DEFAULT_TRANSLATION = 'docker build -f'
	replacements = { DOCKER_DEFAULT: DOCKER_DEFAULT_TRANSLATION }
	return replacements

def translate_BATCHPROCESSING():
	DOCKER_DEFAULT_TRANSLATION = 'batch.sh'
	replacements = { DOCKER_DEFAULT: DOCKER_DEFAULT_TRANSLATION }
	return replacements

def translate_SINGLEPROCESSING():
	DOCKER_DEFAULT_TRANSLATION = 'single.sh'
	replacements = { DOCKER_DEFAULT: DOCKER_DEFAULT_TRANSLATION }
	return replacements

def translate_cmd(CMD_TYPE, cmd):
	replacements = {
		DOWNLOAD_CMD: translate_DOWNLOAD,
		INSTALL_CMD: translate_INSTALL,
		BATCH_PROCESSING_CMD: translate_BATCHPROCESSING,
		SINGLE_PROCESSING_CMD: translate_SINGLEPROCESSING, 
	}[CMD_TYPE]()

	return bash.replace_cmd(cmd, replacements)

def build_config_file(install_details):
	# print(install_details)
	download_cmd = install_details[DOWNLOAD_CMD]
	if download_cmd != NONE:
		bash.run_cmd(translate_cmd(DOWNLOAD_CMD, download_cmd))

	install_cmd = install_details[INSTALL_CMD]
	if install_cmd != NONE:
		bash.run_cmd(translate_cmd(INSTALL_CMD, install_cmd), print_cmd=True)