from os import listdir
from os.path import isfile, join, abspath

import stegtest.utils.filesystem as fs
import stegtest.utils.lookup as lookup
import stegtest.utils.bash as bash

#METADATA
METADATA = 'METADATA'
NAME = 'NAME'
TYPE = 'TYPE'
COMPATIBLE_TYPES  = 'COMPATIBLE_TYPES'
APPLICATION_TYPE = 'APPLICATION_TYPE'

#FLAGS
FLAGS = 'FLAGS'
BATCH_PROCESSING_FLAG = 'BATCH_PROCESSING_FLAG'
SINGLE_PROCESSING_FLAG = 'SINGLE_PROCESSING_FLAG'

#INSTALL
INSTALL = 'INSTALL'
DOWNLOAD_CMD = 'DOWNLOAD_CMD'
INSTALL_CMD = 'INSTALL_CMD'

#RUN
RUN = 'RUN'
SINGLE_PROCESSING_CMD = 'SINGLE_PROCESSING_CMD'
BATCH_PROCESSING_CMD = 'BATCH_PROCESSING_CMD'

#PARAMS
PARAMS = 'PARAMS'
RANGE = 'RANGE'

#DEFAULT VALUES
NONE = 'NONE'
DOCKER_DEFAULT = 'DOCKER_DEFAULT'

config_template = {
	METADATA: [NAME, TYPE, COMPATIBLE_TYPES, APPLICATION_TYPE],
	FLAGS: [BATCH_PROCESSING_FLAG, SINGLE_PROCESSING_FLAG],
	INSTALL: [DOWNLOAD_CMD, INSTALL_CMD],
	RUN: [SINGLE_PROCESSING_CMD, BATCH_PROCESSING_CMD],
	PARAMS: [PARAMS, RANGE]
}

#need a way to define the possible values 
#APPLICATION_TYPES = 'PYTHON', 'DOCKER', 'BASH'
#COMPATIBLE_TYPES = ''

def is_config_file(file):
	return fs.get_extension(file) == '.json'

def process_embeddor(embeddors_json):
	print('embeddors', embeddors_json)
	raise NotImplementedError

def process_detector(detectors_json):
	print('detectors', detectors_json)
	raise NotImplementedError

def process_configs(stegtest_directory, configs_json):
	embeddors_json = list(filter(lambda config: config[METADATA][0][TYPE] == lookup.embeddor, configs_json))
	detectors_json = list(filter(lambda config: config[METADATA][0][TYPE] == lookup.detector, configs_json))

	process_embeddor(embeddors_json)
	process_detector(detectors_json)

def get_config_files(config_directory):
	assert(fs.dir_exists(config_directory))
	config_files = [abspath(join(config_directory, f)) for f in listdir(config_directory) if is_config_file(f)]
	return config_files

def initialize_configs(stegtest_directory, config_directory):
	config_files = get_config_files(config_directory)
	configs_json = [fs.read_json_file(file_path) for file_path in config_files]

	process_configs(stegtest_directory, configs_json)

	return configs_json

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