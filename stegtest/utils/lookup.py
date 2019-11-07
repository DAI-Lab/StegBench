import stegtest.utils.filesystem as fs
import uuid
import ast 
import os 
import random
import string
import subprocess

from os.path import join, abspath

#TOP DIRECTORY
stegtest_tld = 'stegtest_asssets'

#SUB-DIRECTORY TYPES#
embeddor = 'embeddor'
detector = 'detector'
db = 'db'
config = 'config'

embeddor_dir = join(stegtest_tld, embeddor)
detector_dir = join(stegtest_tld, detector)
db_dir = join(stegtest_tld, db)

#DB DIRECTORIES AND FILES
dataset = 'datasets'
metadata = 'metadata'
source_db_file = 'source.csv'
embedded_db_file = 'embedded.csv'
db_file = 'db.csv'

#ALGORITHM DIRECTORIES AND FILES
assets = 'assets'
sets_dir = 'sets'
embeddors_set_dir = 'embeddors_sets'
detectors_set_dir = 'detectors_sets'
embeddors_file = 'embeddors.csv'
detectors_file = 'detectors.csv'

#IMAGE INFORMATION
file_path = 'file'
image_type = 'type'
image_width = 'width'
image_height = 'height'
image_channels = 'channels'
embedding_max = 'embedding_max'

#STEGANOGRAPHIC INFORMATION FILE INFORMATION
steganographic_function = 'Generating Algorithm'
source_image = 'Source Image'

#STEGANOGRAPHIC METADATA
source_db = 'Source Database'
source_embeddor_set = 'Source Embeddor Set'

#HEADER VARIABLES
name_descriptor = 'Name'
path_descriptor = 'Path'
uuid_descriptor = 'UUID'
compatible_descriptor = 'compatible_types'
embedding_descriptor = 'max_embedding_ratio'

filepath_descriptor = 'Filepath'
db_descriptor = 'DB Name'
db_image_count = 'Number of Images'

#FILE HEADERS

master_algo_header = [uuid_descriptor, name_descriptor, filepath_descriptor] #points to a config file
individual_set_header = [uuid_descriptor] #points to a master algo
master_set_header = [uuid_descriptor, filepath_descriptor] #points to an individual set


db_header = [uuid_descriptor, db_descriptor, db_image_count, compatible_descriptor]
steganographic_header = [uuid_descriptor, source_db, source_embeddor_set, db_image_count, compatible_descriptor]

#ALGORITHM TYPES
algorithm_name = 'name'
embed_function = 'embed'
detect_function = 'detect'
parameters = 'parameters'
compatibile_types_decorator = 'compatibile_types'
description = 'description'

#BINARY CLASSIFIER STATISTICS
false_positive_rate = 'fpr'
false_negative_rate = 'fnr'
true_negative_rate = 'tnr'
negative_predictive_value = 'npv'
false_discovery_rate = 'fdr'
true_positive_rate = 'tpr'
positive_predictive_value = 'ppv'
accuracy = 'acc'
roc_auc = 'roc_auc'
result = 'result'

#file identifiers
input_file_header = 'input'
output_file_header = 'output'

#IMAGE OPERATIONS
add_noise = 'noise'
crop = 'crop'
resize = 'resize'
rotate = 'rotate'

#METADATA
ALGORITHM_TYPE = 'algorithm_type'
COMMAND_TYPE = 'command_type'
COMPATIBLE_TYPES  = 'compatible_types'
MAX_EMBEDDING_RATIO = 'max_embedding_ratio'

#COMMAND_TYPE OPTIONS
DOCKER = 'docker'
NATIVE = 'native'
CLASS = 'class'
END_DOCKER = 'end_docker'

#COMMAND ATTRIBUTE
BATCH = 'batch'
SINGLE = 'single'
WORKING_DIR = 'working_dir'

#APPLICATION_SPECIFIC - DOCKER
DOCKER_IMAGE = 'docker_image'
container_id = 'container_id'
input_dir = '/data-input'
output_dir = '/data-output'
asset_dir = '/data-asset'
result_dir = '/data-result'

#COMMAND
COMMAND = 'run'
POST_COMMAND = 'post_run'
PIPE_OUTPUT = 'pipe_output'

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




def get_top_level_dirs():
	return {embeddor: embeddor_dir, db: db_dir, detector:detector_dir}

def get_db_dirs():
	return {dataset: join(db_dir, dataset), metadata: join(db_dir, metadata)}

def get_db_files():
	return {source_db_file: join(db_dir, source_db_file), embedded_db_file: join(db_dir, embedded_db_file)}

def get_algo_asset_dirs():
	return {embeddor: join(embeddor_dir, assets), detector: join(detector_dir, assets)}

def get_algo_set_dirs():
	return {embeddor: join(embeddor_dir, sets_dir), detector: join(detector_dir, sets_dir)}

def get_algo_master_files():
	return {embeddor: embeddors_file, detector: detectors_file}

def get_all_files():
	return {
		embeddors_file: join(embeddor_dir, embeddors_file),
		detectors_file: join(detector_dir, detectors_file),
		source_db_file: join(db_dir, source_db_file),
		embedded_db_file: join(db_dir, embedded_db_file),
	}

def get_all_dirs():
	top_level_dirs = list(get_top_level_dirs().values())
	algo_asset_dirs = list(get_algo_asset_dirs().values())
	algo_set_dirs = list(get_algo_set_dirs().values())
	db_dirs = list(get_db_dirs().values())

	return top_level_dirs + algo_asset_dirs + algo_set_dirs + db_dirs 

def get_master_header(type:str):
	return {
		 embeddors_file: master_algo_header,
		 detectors_file: master_algo_header,
		 source_db_file: db_header,
		 embedded_db_file: steganographic_header,
	}[type]

def get_parameter_type(type):
    return {
     'str': str,
     'int': int,
     'float': float,
     'bool': bool,
     'uuid': uuid.UUID
    }[type]

def get_image_operations():
	return [add_noise, crop, resize, rotate]

def get_default_image_operation_values():
	return {
		add_noise: 1.0,
		crop: (512, 512),
		resize: (512, 512),
		rotate: (180),
	}

def lossy_encoding_types():
	return ['jpeg', 'jpg']

def lossless_encoding_types():
	return ['bmp', 'pgm', 'png']

def all_supported_types():
	return lossy_encoding_types() + lossless_encoding_types()

def get_statistics_header():
	return [false_positive_rate, false_negative_rate, true_negative_rate, negative_predictive_value,
	false_discovery_rate, true_positive_rate, positive_predictive_value, accuracy, detector]

def get_metric_variables():
	return [false_positive_rate, false_negative_rate, true_negative_rate, negative_predictive_value,
	false_discovery_rate, true_positive_rate, positive_predictive_value, accuracy, roc_auc]

def create_asset_file(type:str, content:str):
	"""creates a text asset for the specificied directory"""
	asset_directory = get_algo_asset_dirs()[type]
	file_name = fs.create_name_from_uuid(fs.get_uuid()[:10], 'txt')
	file_path = abspath(join(asset_directory, file_name))

	fs.write_to_text_file(file_path, [content])
	return file_path

def get_all_source_dbs():
	source_master_file = get_db_files()[source_db_file]
	source_rows = fs.read_csv_file(source_master_file, return_as_dict=True)

	return source_rows

def get_all_embedded_dbs():
	embedded_master_file = get_db_files()[embedded_db_file]
	embedded_rows = fs.read_csv_file(embedded_master_file, return_as_dict=True)

	return embedded_rows

def get_all_dbs():
	"""gets the dbs that are already processed"""
	return get_all_source_dbs() + get_all_embedded_dbs()

def get_steganographic_db_info(db_identifier):
	"""gets db info for a specific db"""
	all_db_information = get_all_embedded_dbs()
	found_data = list(filter(lambda d: d[uuid_descriptor] == db_identifier, all_db_information))
	assert(len(found_data) == 1)

	found_data = found_data[0]
	assert(len(found_data) == len(steganographic_header))

	found_data[compatible_descriptor] = ast.literal_eval(found_data[compatible_descriptor])

	return found_data

def get_source_db_info(db_identifier):
	"""gets db info for a specific db"""
	all_db_information = get_all_source_dbs()
	found_data = list(filter(lambda d: d[uuid_descriptor] == db_identifier or d[db_descriptor] == db_identifier, all_db_information))
	assert(len(found_data) == 1)

	found_data = found_data[0]
	assert(len(found_data) == len(db_header))

	found_data[compatible_descriptor] = ast.literal_eval(found_data[compatible_descriptor])

	return found_data

def get_image_info_variables():
	return [file_path, image_type, image_width, image_height, image_channels, embedding_max]

def get_steganographic_info_variables():
	return [file_path, image_type, image_width, image_height, image_channels, embedding_max, source_image, uuid_descriptor]

def get_image_list(db_descriptor):
	metadata_directory = get_db_dirs()[metadata]
	db_directory = join(metadata_directory, db_descriptor)
	db_master_file = join(db_directory, db_file)

	assert(fs.dir_exists(db_directory))
	assert(fs.file_exists(db_master_file))

	image_info = fs.read_csv_file(db_master_file, return_as_dict=True)
	return image_info

def get_cmd(algorithm_info):
	return algorithm_info[COMMAND]

def get_post_cmd(algorithm_info):
	if POST_COMMAND in algorithm_info:
		return algorithm_info[POST_COMMAND]

	return None

####TO MOVE THESE -- SINCE THESE ARE NOT LOOKUP BUT GENERATION####

def generate_output_list(output_directory:str, input_list:dict):
	target_directory = output_directory

	output_list = []
	for file in input_list:
		file_name = file[file_path]
		file_type = file[image_type]

		output_file = fs.create_name_from_uuid(fs.get_uuid(), file_type)
		output_file_path = join(target_directory, output_file)
		output_list.append(output_file_path)

	return output_list

def initialize_filesystem(directory): #TODO need to remove the None part
	"""Clears and adds needed directories for stegdetect to work"""
	print('initializing fs at ' + directory)
	try:
		os.chdir(directory)
	except:
		raise OSError('directory: ' + directory + ' is not a valid directory. Please initialize with a valid directory')

	print('cleaning fs...')
	fs.clean_filesystem([stegtest_tld])

	fs.make_dir(stegtest_tld)

	print('initializing directories...')

	directories = get_all_dirs()

	for directory in directories:
		fs.make_dir(directory)

	print('initializing all files...')
	algo_files = get_all_files()
	for file_type in algo_files.keys():
		path_to_master_file = algo_files[file_type]
		master_file_header = get_master_header(file_type)

		fs.write_to_csv_file(path_to_master_file, [master_file_header])
