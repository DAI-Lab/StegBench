import stegtest.utils.filesystem as fs
import uuid
import ast 
import os 
import random
import string
import subprocess

from os.path import join, abspath

#TODO consider moving strings to a separate json/python file

#TODELETE
tmp = 'tmp'

#TOP DIRECTORY
stegtest_tld = 'stegtest_asssets'
directories_file = 'directories.csv'

#SUB-DIRECTORY TYPES#
embeddor = join(stegtest_tld, 'embeddor')
detector = join(stegtest_tld, 'detector')
db = join(stegtest_tld, 'db')
config = 'config'

#DB DIRECTORIES AND FILES
dataset = 'datasets'
metadata = 'metadata'
source = 'source_info' #TO DELETE
embedded = 'embedded_info' #TO DELETE
source_db_file = 'source.csv'
embedded_db_file = 'embedded.csv'

#ALGORITHM DIRECTORIES AND FILES
assets = 'assets'
sets = 'sets'
sets_master_file = 'sets.csv'
embeddors_file = 'embeddors.csv'
detectors_file = 'detectors.csv'

#IMAGE INFORMATION
file_path = 'file'
image_type = 'type'
image_width = 'width'
image_height = 'height'
image_channels = 'channels'

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
compatible_descriptor = 'Compatible Types'
filepath_descriptor = 'Filepath'
db_descriptor = 'DB Name'
db_image_count = 'Number of Images'

#FILE HEADERS
directories_header = [name_descriptor, path_descriptor]
embeddor_header = [uuid_descriptor, compatible_descriptor, filepath_descriptor] 
detector_header = [uuid_descriptor, compatible_descriptor, filepath_descriptor]
db_header = [uuid_descriptor, db_descriptor, db_image_count, compatible_descriptor]
steganographic_header = [uuid_descriptor, source_db, source_embeddor_set, db_image_count, compatible_descriptor]
algo_header = [uuid_descriptor, name_descriptor, compatible_descriptor, filepath_descriptor]

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

#TO DELETE
# def get_master_files():
# 	master_files = {binding: join(binding, master_file) for binding in get_top_level_directories().values()}

# 	db_directories = get_db_directories()
# 	dataset_master_files = {binding: join(db_directories[binding], master_file) for binding in db_directories}

# 	master_files.update(dataset_master_files)
# 	return master_files

# def get_db_directories():
# 	return {
# 	dataset: join(db, dataset), 
# 	source: join(db, source), 
# 	embedded: join(db, embedded),
# 	}

# def get_tmp_directories():
# 	tld = get_top_level_directories()
# 	tmp_directories = {tl: join(tl, tmp) for tl in tld}

# 	return tmp_directories

# def get_asset_directories():
# 	tld = get_top_level_directories()
# 	asset_directories = {tl: join(tl, assets) for tl in tld}

# 	return asset_directories


####TODO FIX HEADER NAMING CONVENTION. reorg the structure here for better naming

def get_stegtest_dir_files():
	return {directories_file: join(stegtest_tld, directories_file)}

def get_top_level_dirs():
	return {embeddor: embeddor, db: db, detector:detector}

def get_db_dirs():
	return {dataset: join(db, dataset), metadata: join(db, metadata)}

def get_db_files():
	return {source_db_file: join(db, source_db_file), embedded_db_file: join(db, embedded_db_file)}

def get_algo_asset_dirs():
	return {embeddor: join(embeddor, assets), detector: join(detector, assets)}

def get_algo_set_dirs():
	return {embeddor: join(embeddor, sets), detector: join(detector, sets)}

def get_algo_set_files():
	return {embeddor: join(embeddor, sets_master_file), detector: join(detector, sets_master_file)}

def get_algo_master_files():
	return {embeddors_file: join(embeddor, embeddors_file), detectors_file: join(detector, detectors_file)}

def get_all_dirs():
	top_level_dirs = list(get_top_level_dirs().values())
	algo_asset_dirs = list(get_algo_asset_dirs().values())
	algo_set_dirs = list(get_algo_set_dirs().values())
	db_dirs = list(get_db_dirs().values())

	return top_level_dirs + algo_asset_dirs + algo_set_dirs + db_dirs 

def get_master_header(type:str):
	return {
		 embeddor: embeddor_header,
		 detector: detector_header,
		 embeddors_file: algo_header,
		 detectors_file: algo_header,
		 source_db_file: db_header,
		 embedded_db_file: steganographic_header,
		 directories_file: directories_header,

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

def all_supported_types():
	return ['bmp', 'gif', 'jpeg', 'jpg', 'pgm', 'png']

def get_statistics_header():
	return [false_positive_rate, false_negative_rate, true_negative_rate, negative_predictive_value,
	false_discovery_rate, true_positive_rate, positive_predictive_value, accuracy, detector]

def get_metric_variables():
	return [false_positive_rate, false_negative_rate, true_negative_rate, negative_predictive_value,
	false_discovery_rate, true_positive_rate, positive_predictive_value, accuracy, roc_auc]

def get_compatible_types(steganographic_function):
	compatibile_types = getattr(steganographic_function, compatibile_types_decorator)
	compatibile_types = list(map(lambda ct: ct.__name__, compatibile_types))

	all_types = all_supported_types()
	compatibile_types = list(filter(lambda ct: ct in all_types, compatibile_types))

	return compatibile_types

def create_asset_file(type:str, content:str, shortened:bool=False):
	"""creates a text asset for the specificied directory"""
	asset_directory = get_asset_directories()[type]
	file_name = fs.create_file_from_hash(fs.get_uuid(), 'txt')

	if shortened:
		file_name = file_name[:10] + '.txt'

	file_path = abspath(join(asset_directory, file_name))

	fs.write_to_text_file(file_path, [content])
	return file_path

def get_all_source_dbs():
	source_master_file = get_master_files()[source]
	source_rows = fs.read_csv_file(source_master_file, return_as_dict=True)

	return source_rows

def get_all_embedded_dbs():
	embedded_master_file = get_master_files()[embedded]
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
	return [file_path, image_type, image_width, image_height, image_channels]

def get_steganographic_info_variables():
	return [file_path, image_type, image_width, image_height, image_channels, source_image, steganographic_function]

def get_image_list(db_descriptor):
	#get the master.csv file in the db/datasets folder
	dir_name = fs.create_name_from_hash(db_descriptor)
	dataset_directory = get_db_directories()[dataset]
	db_directory = join(dataset_directory, dir_name)
	db_master_file = join(db_directory, master_file)

	assert(fs.dir_exists(db_directory))
	assert(fs.file_exists(db_master_file))

	image_info = fs.read_csv_file(db_master_file, return_as_dict=True)
	return image_info

def generate_output_list(output_directory:str, input_list:dict):
	target_directory = output_directory

	output_list = []
	for file in input_list:
		file_name = file[file_path]
		file_type = file[image_type]

		output_file = fs.create_file_from_hash(file_name, file_type)
		output_file_path = join(target_directory, output_file)
		output_list.append(output_file_path)

	return output_list

def run_cmd(cmd:list):
	print(' '.join(cmd))
	subprocess.run(' '.join(cmd), shell=True)#, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def generate_random_string(byte_length=20):
	return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(byte_length))

def generate_random_float():
	return random.random()*10000

def generate_random_int():
	return int(generate_random_float())

def generate_param(type, *args):
	function = {
		'str': generate_random_string, 
		'float': generate_random_float,
		'int': generate_random_int,
	}[type]
	return function(*args)

def generate_password(byte_length):
	return generate_random_string(byte_length)

def convert_channels_to_int(channel:str):
	return {
		'L': 1,
		'P': 1,
		'RGB': 3,
		'RGBA': 4,
		'CMYK': 4,
		'YCbCr': 3,
		'LAB': 3,
		'HSV': 3,
	}[channel]

def generate_secret_text(file_info, bpp):
	width = int(file_info[image_width])
	height = int(file_info[image_height])
	channels = convert_channels_to_int(file_info[image_channels])

	pixels = width*height*channels
	strlen_in_bits = pixels*bpp
	strlen_in_bytes = int(strlen_in_bits/8)

	return generate_random_string(strlen_in_bytes)

def initialize_filesystem(directory, config_directory=None): #TODO need to remove the None part
	"""Clears and adds needed directories for stegdetect to work"""
	if config_directory is not None:
		config_directory = abspath(config_directory)
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

	print('initializing directory file...')
	directory_files = get_stegtest_dir_files()
	for file_type in directory_files.keys():
		path_to_master_file = directory_files[file_type]
		master_file_header = get_master_header(file_type)

		data = [master_file_header]
		if config_directory:
			data.append([config, config_directory])

		fs.write_to_csv_file(path_to_master_file, data)

	print('initializing algo set files...')
	algo_files = get_algo_set_files()
	for file_type in algo_files.keys():
		path_to_master_file = algo_files[file_type]
		master_file_header = get_master_header(file_type)

		fs.write_to_csv_file(path_to_master_file, [master_file_header])

	print('initializing algo master files...')
	algo_files = get_algo_master_files()
	for file_type in algo_files.keys():
		path_to_master_file = algo_files[file_type]
		master_file_header = get_master_header(file_type)

		fs.write_to_csv_file(path_to_master_file, [master_file_header])

	print('initializing db master files...')
	db_files = get_db_files()
	for file_type in db_files.keys():
		path_to_master_file = db_files[file_type]
		master_file_header = get_master_header(file_type)

		fs.write_to_csv_file(path_to_master_file, [master_file_header])
