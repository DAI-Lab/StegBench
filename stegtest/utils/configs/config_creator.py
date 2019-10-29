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
#COMPATIBLE_TYPES = 'JPEG, JPG, PNG, PMG, etc.'

def create_config_file(directory:str, config_details):
	check_config_info(config_details)

	file_path = abspath(join(fs.get_uuid(), directory))
	print('Creating a config file at ' + file_path)
	fs.write_to_json_file(file_path, config_details)

def create_config_file_default(directory:str, parameters=None):
	data = {}
	data[METADATA] = []
	data[METADATA].append({
		NAME: 'JSTEG',
		TYPE: lookup.embeddor,
		COMPATIBLE_TYPES: ['JPEG', 'JPG'],
		APPLICATION_TYPE: DOCKER_DEFAULT, #BASH, PYTHON, JAVA, (????)
	})
	data[FLAGS] = []
	data[FLAGS].append({
		BATCH_PROCESSING_FLAG: 1,
		SINGLE_PROCESSING_FLAG: 1,
	})
	data[INSTALL] = []
	data[INSTALL].append({
		DOWNLOAD_CMD: NONE,
		INSTALL_CMD: DOCKER_DEFAULT + ' docker_name'
	})
	data[RUN] = []
	data[RUN].append({
		BATCH_PROCESSING_FLAG: DOCKER_DEFAULT,
		SINGLE_PROCESSING_FLAG: DOCKER_DEFAULT,
	})
	data[PARAMS] = []
	data[PARAMS].append({
		NAME: 'PASSWORD',
		TYPE: 'STR',
		RANGE: 'DEFAULT'
	})
	data[PARAMS].append({
		NAME: 'BPP',
		TYPE: 'FLOAT',
		RANGE: [0.0, 1.0]
	})

	file_path = join(directory, 'test.json')

	fs.write_to_json_file(file_path, data)
