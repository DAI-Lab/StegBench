import stegbench.utils.filesystem as fs
import uuid
import ast 
import os 
import random
import string
import subprocess

from os.path import join, abspath

#TOP DIRECTORY
stegbench_tld = 'stegbench_asssets'

#SUB-DIRECTORY TYPES#
embeddor = 'embeddor'
detector = 'detector'
db = 'db'

embeddor_dir = join(stegbench_tld, embeddor)
detector_dir = join(stegbench_tld, detector)
db_dir = join(stegbench_tld, db)

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

#METADATA
ALGORITHM_TYPE = 'algorithm_type'
DETECTOR_TYPE = 'detector_type'
COMMAND_TYPE = 'command_type'
COMPATIBLE_TYPES  = 'compatible_types'
MAX_EMBEDDING_RATIO = 'max_embedding_ratio'

#DETECTOR TYPE OPTIONS
binary_detector = 'binary'
probability_detector = 'probability'

#COMMAND_TYPE OPTIONS
DOCKER = 'docker'
NATIVE = 'native'
CLASS = 'class'
END_DOCKER = 'end_docker'

#APPLICATION_SPECIFIC - DOCKER
DOCKER_IMAGE = 'docker_image'
WORKING_DIR = 'working_dir'

container_id = 'container_id'
input_dir = '/data-input'
output_dir = '/data-output'
asset_dir = '/data-asset'
result_dir = '/data-result'

#COMMAND
PRE_COMMAND = 'pre_run'
COMMAND = 'run'
POST_COMMAND = 'post_run'
VERIFY_COMMAND = 'verify'
PIPE_OUTPUT = 'pipe_output'
OUTPUT_FILE = 'output_file'

#COMMAND SPECIFIC - COVER
INPUT_IMAGE_DIRECTORY = 'INPUT_IMAGE_DIRECTORY'
INPUT_IMAGE_NAME = 'INPUT_IMAGE_NAME'
INPUT_IMAGE_PATH = 'INPUT_IMAGE_PATH'

#COMMAND SPECIFIC - SECRET MESSAGE
SECRET_TXT_PLAINTEXT = 'SECRET_TXT_PLAINTEXT'
SECRET_TXT_FILE = 'SECRET_TXT_FILE'
VERIFY_TXT_FILE = 'VERIFY_TXT_FILE'

#COMMAND-SPECIFIC - SUPPORTED INPUT PARAMETERS
PASSWORD = 'PASSWORD'
PAYLOAD = 'PAYLOAD'

#METDATA OPTIONS
payload = 'payload'
cores = 'cores'
result_file = 'result_file'

#COMMAND-SPECIFIC - OUTPUT
OUTPUT_IMAGE_DIRECTORY = 'OUTPUT_IMAGE_DIRECTORY'
OUTPUT_IMAGE_NAME = 'OUTPUT_IMAGE_NAME'
OUTPUT_IMAGE_PATH = 'OUTPUT_IMAGE_PATH'

#COMMAND-SPECIFIC - OUTPUT
RESULT_CSV_FILE = 'RESULT_CSV_FILE'
RESULT_TXT_FILE = 'RESULT_TXT_FILE'
TEMP_CSV_FILE = 'TEMP_CSV_FILE'
TEMP_TXT_FILE = 'TEMP_TXT_FILE'

#FILTER SPECIFIC
regex_filter_yes = 'regex_filter_yes'
regex_filter_no = 'regex_filter_no'

#IMAGE INFORMATION
label = 'label'
file_path = 'file'
image_type = 'type'
image_width = 'width'
image_height = 'height'
image_channels = 'channels'
embedding_max = 'embedding_max'
embedding_bpp = 'embedding_bpp'
embedding_nzbAC = 'embedding_nzbAC'
embedding_nzbAC3 = 'embedding_nzbAC3'

#LABEL TYPES
stego = 'stego'
cover = 'cover'

#STEGANOGRAPHIC INFORMATION FILE INFORMATION
steganographic_function = 'Generating Algorithm'
source_image = 'Source Image'
secret_txt_length = 'Secret Text Length'

#STEGANOGRAPHIC METADATA
source_db = 'Source Database'
source_embeddor_set = 'Source Embeddor Set'
embedding_ratio = 'Embedding Ratio'

#HEADER VARIABLES
name_descriptor = 'name'
path_descriptor = 'path'
uuid_descriptor = 'uuid'
compatible_descriptor = 'compatible_types'
embedding_descriptor = 'max_embedding_ratio'

filepath_descriptor = 'Filepath'
db_descriptor = 'DB Name'
db_image_count = 'Number of Images'

#FILE HEADERS
cover_image_header = [file_path, image_type, image_width, image_height, image_channels, embedding_max, label]
steganographic_image_header = cover_image_header + [source_image, uuid_descriptor, secret_txt_length, PASSWORD]

master_algo_header = [uuid_descriptor, name_descriptor, filepath_descriptor] #points to a config file
individual_set_header = [uuid_descriptor] #points to a master algo
master_set_header = [uuid_descriptor, filepath_descriptor] #points to an individual set

db_header = [uuid_descriptor, path_descriptor, db_descriptor, db_image_count, compatible_descriptor]
steganographic_header = db_header + [source_db, source_embeddor_set, embedding_ratio]

#ALGORITHM TYPES
algorithm_name = 'name'
embed_function = 'embed'
detect_function = 'detect'
parameters = 'parameters'
compatibile_types_decorator = 'compatibile_types'
description = 'description'

#BINARY CLASSIFIER STATISTICS
result = 'result'

result_metric = 'metrics'
false_positive_rate = 'false positive rate'
false_negative_rate = 'false negative rate'
true_negative_rate = 'true negative rate'
negative_predictive_value = 'negative predictive value'
false_discovery_rate = 'false discovery rate'
true_positive_rate = 'true positive rate'
positive_predictive_value = 'positive predictive value'
accuracy = 'accuracy'
roc_auc = 'area under ROC curve'
roc_curve = 'roc curve'
ap_score = 'average precision score'

result_raw = 'raw'
true_positive_raw = 'True Positive'
true_negative_raw = 'True Negative'
total_stego_raw = 'Total Stego'
total_cover_raw = 'Total Cover'

#file identifiers
input_file_header = 'input'
output_file_header = 'output'

#IMAGE OPERATIONS
add_noise = 'noise'
crop = 'crop'
center_crop = 'center_crop'
resize = 'resize'
rgb2gray = 'rgb2gray'
rotate = 'rotate'
convert_to_png = 'conv_to_png'
convert_to_jpeg = 'conv_to_jpeg'

train = 'train'
test = 'test'
validation = 'validation'
train_test_val_split = 'ttv_split'
limit = 'limit'
amount_of_images = 'amount_of_images'

removal_prefix = 'rm'
removal_directory_prefix = 'rm -rf'
docker_exec_prefix = 'docker exec'

attack_FGM = 'FGSM'
attack_EAD = 'EAD'
attack_BIM = 'BIM'
attack_PGD = 'PGD'
attack_JSMA = 'JSMA'
attack_PIXEL = 'PIXEL'

pytorch = 'pytorch'
tensorflow = 'tensorflow'

input_shape = 'input shape'
criterion = 'criterion'
optimizer = 'optimizer'
nb_classes = 'number classes'
attack_method = 'attack method'
robust_db_name = 'robust database name'

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
	return [add_noise, resize, rotate, convert_to_jpeg, convert_to_png, center_crop, rgb2gray]

def get_directory_operations():
	return [stego, train_test_val_split, limit]

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
	found_data[stego] = True

	return found_data

def get_source_db_info(db_identifier):
	"""gets db info for a specific db"""
	all_db_information = get_all_source_dbs()
	found_data = list(filter(lambda d: d[uuid_descriptor] == db_identifier or d[db_descriptor] == db_identifier, all_db_information))
	assert(len(found_data) == 1)

	found_data = found_data[0]
	assert(len(found_data) == len(db_header))

	found_data[compatible_descriptor] = ast.literal_eval(found_data[compatible_descriptor])
	found_data[stego] = False

	return found_data

def get_db_info(db_identifier):
	db_info = None
	try: 
		db_info = get_source_db_info(db_identifier)
	except:
		db_info = get_steganographic_db_info(db_identifier)

	return db_info

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

def get_pre_cmd(algorithm_info):
	if PRE_COMMAND in algorithm_info:
		return algorithm_info[PRE_COMMAND]
	return None

def get_cmd(algorithm_info):
	return algorithm_info[COMMAND]

def get_post_cmd(algorithm_info):
	if POST_COMMAND in algorithm_info:
		return algorithm_info[POST_COMMAND]
	return None

def get_verify_cmd(algorithm_info):
	return algorithm_info[VERIFY_COMMAND]

def get_attack_methods():
	return [attack_FGM, attack_EAD, attack_BIM, attack_PGD, attack_JSMA]

def initialize_filesystem(directory):
	"""Clears and adds needed directories for stegdetect to work"""
	print('initializing fs at ' + directory)
	try:
		os.chdir(directory)
	except:
		raise OSError('directory: ' + directory + ' is not a valid directory. Please initialize with a valid directory')

	print('cleaning fs...')
	fs.clean_filesystem([stegbench_tld])

	fs.make_dir(stegbench_tld)

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
