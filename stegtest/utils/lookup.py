import stegtest.utils.filesystem as fs
import uuid
import ast 
import os 

from os.path import join, abspath

#TODO consider moving strings to a separate json/python file

#DIRECTORY TYPES#
embeddor = 'embeddor'
detector = 'detector'
db = 'db'
tmp = 'tmp'
assets = 'assets'
datasets = 'datasets'

#IMAGE INFORMATION
file_path = 'file'
image_type = 'type'
image_width = 'width'
image_height = 'height'
image_channels = 'channels'

#HEADER NAMES
uuid_descriptor = 'UUID'
compatible_descriptor = 'Compatible Types'
filepath_descriptor = 'Filepath'
db_descriptor = 'DB Name'
db_image_count = 'Number of Images'

##FILE TYPES##
master_file = 'master.csv'
embeddor_header = [uuid_descriptor, compatible_descriptor, filepath_descriptor] 
detector_header = [uuid_descriptor, compatible_descriptor, filepath_descriptor]
db_header = [uuid_descriptor, db_descriptor, db_image_count, compatible_descriptor]

##ALGORITHM TYPES##
algorithm_name = 'name'
embed_function = 'embed'
detect_function = 'detect'
parameters = 'parameters'
compatibile_types_decorator = 'compatibile_types'
description = 'description'

def get_master_files():
	return {binding: join(binding, master_file) for binding in get_top_level_directories().values()}

def get_bindings_list(type):
	bindings = get_master_files()
	return bindings[type]

def get_types():
	return [embeddor, detector, db]

def get_parameter_type(type):
    return {
     'str': str,
     'int': int,
     'float': float,
     'bool': bool,
     'uuid': uuid.UUID
    }[type]

def all_supported_types():
	return ['bmp', 'gif', 'jpeg', 'jpg', 'pgm', 'png']

def get_compatible_types(steganographic_function):
	compatibile_types = getattr(steganographic_function, compatibile_types_decorator)
	compatibile_types = list(map(lambda ct: ct.__name__, compatibile_types))

	all_types = all_supported_types()
	compatibile_types = list(filter(lambda ct: ct in all_types, compatibile_types))

	return compatibile_types

def get_top_level_directories():
	return {embeddor: embeddor, detector: detector, db: db}

def get_tmp_directories():
	tld = get_top_level_directories()
	tmp_directories = {tl: join(tl, tmp) for tl in tld}

	return tmp_directories

def get_asset_directories():
	tld = get_top_level_directories()
	asset_directories = {tl: join(tl, assets) for tl in tld}

	return asset_directories

def get_master_header(type:str):
	assert(type == embeddor or type == detector or type == db)
	def get_header_for_type():
		return {
		 embeddor: embeddor_header,
		 detector: detector_header,
		 db: db_header
		}[type]

	return get_header_for_type()

def get_dataset_directory():
	return {db: join(db, datasets)}

def all_directories():
	tld = list(get_top_level_directories().values())
	tmp_directories = list(get_tmp_directories().values())
	asset_directories = list(get_asset_directories().values())
	dataset_directory = list(get_dataset_directory().values())

	return tld + tmp_directories + asset_directories + dataset_directory

def create_asset_file(type:str, content:str):
	"""creates a text asset for the specificied directory"""
	asset_directory = get_asset_directories()[type]
	file_name = fs.create_file_from_hash(fs.get_uuid(), 'txt')
	file_path = abspath(join(asset_directory, file_name))

	fs.write_to_text_file(file_path, [content])
	return file_path

def get_all_dbs():
	"""gets the dbs that are already processed"""
	db_master_file = get_master_files()[db]
	db_rows = fs.read_csv_file(db_master_file, return_as_dict=True)

	return db_rows

def get_db_info(db_identifier):
	"""gets db info for a specific db"""
	all_db_information = get_all_dbs()
	found_data = list(filter(lambda d: d[uuid_descriptor] == db_identifier or d[db_descriptor] == db_identifier, all_db_information))
	assert(len(found_data) == 1)

	found_data = found_data[0]
	assert(len(found_data) == len(db_header))

	found_data[compatible_descriptor] = ast.literal_eval(found_data[compatible_descriptor])

	return found_data

def get_image_info_variables():
	return [file_path, image_type, image_width, image_height, image_channels]

def get_image_list(db_descriptor):
	#get the master.csv file in the db/datasets folder
	dataset_directory = get_dataset_directory()[db]
	db_directory = join(dataset_directory, db_descriptor)
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

def initialize_filesystem(directory):
	"""Clears and adds needed directories for stegdetect to work"""
	print('initializing fs at ' + directory)
	try:
		os.chdir(directory)
	except:
		raise OSError('directory: ' + directory + ' is not a valid directory. Please initialize with a valid directory')

	print('cleaning fs...')
	
	top_level_directories = get_top_level_directories().values()
	fs.clean_filesystem(top_level_directories)

	print('initializing directories...')

	directories = all_directories()

	for directory in directories:
		fs.make_dir(directory)

	print('initializing files...')
	master_files = get_master_files()
	for file_type in master_files.keys():
		path_to_master_file = master_files[file_type]
		master_file_header = get_master_header(file_type)

		fs.write_to_csv_file(path_to_master_file, [master_file_header])

