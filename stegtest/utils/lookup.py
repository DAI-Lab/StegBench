import stegtest.utils.filesystem as fs
import uuid

#DIRECTORY TYPES#
embeddor = 'embeddor'
detector = 'detector'
db = 'db'
tmp = 'tmp'
assets = 'assets'
datasets = 'datasets'

##FILE TYPES##
master_file = 'master.csv'
embeddor_header = ['UUID', 'Compatible Types', 'Filepath'] 
detector_header = ['UUID', 'Compatible Types', 'Filepath']
db_header = ['UUID', 'Name', 'Number of Images']

##ALGORITHM TYPES##
algorithm_name = 'name'
embed_function = 'embed'
detect_function = 'detect'
parameters = 'parameters'
compatibile_types_decorator = 'compatibile_types'
description = 'description'

def get_master_files():
	return {binding: binding + '/' + master_file for binding in get_top_level_directories().values()}

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
	tmp_directories = {tl: (tl + '/' + tmp) for tl in tld}

	return tmp_directories

def get_asset_directories():
	tld = get_top_level_directories()
	asset_directories = {tl: (tl + '/' + assets) for tl in tld}

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
	return {db: db + '/' + datasets}

def all_directories():
	tld = list(get_top_level_directories().values())
	tmp_directories = list(get_tmp_directories().values())
	asset_directories = list(get_asset_directories().values())
	dataset_directory = list(get_dataset_directory().values())

	return tld + tmp_directories + asset_directories + dataset_directory

def create_asset_file(type:str, content:str):
	"""creates a text asset for the specificied directory"""
	asset_directory = lookup.get_asset_directories()[type]
	file_name = fs.create_file_from_hash(fs.get_uuid(), 'txt')
	file_path = abspath(asset_directory + '/' + file_name)
	
	fs.write_to_text_file(file_path, [content])
	return file_path

def get_db_names():
	"""gets the dbs that are already processed"""
	db_master_file = get_master_files()[db]
	db_rows = fs.read_csv_file(db_master_file)

	header = db_rows[0]
	db_data = db_rows[1:]

	data_to_dict = []
	for row in db_data:
		assert(len(row) == len(header)) #have to be the same to match properly
		
		row_dict = {}
		for i in range(len(row)):
			row_dict[header[i]] = row[i]

		data_to_dict.append(row_dict)

	return data_to_dict
