import inspect
import ast
import collections
import random
import string

import stegtest.embeddors as embeddors
import stegtest.detectors as detectors
import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs

from os.path import abspath, join


###TODO 
#1. NEED TO INSTANTIATE RANDOMLY 
#2. NEED TO BE ABLE TO POINT AN ANALYZER TO AN ARBITRARY DIRECTORY
#3. NEED TO BE ABLE TO 

def generate_random_string():
	return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(50))

def generate_random_float():
	return random.random()*10000

def generate_random_int():
	return int(generate_random_float())

def generate_param(type):
	function = {
		'str': generate_random_string, 
		'float': generate_random_float,
		'int': generate_random_int,
	}[type]

	return function()

def create_algorithm_set(type:str, algorithm:str):
	"""creates a new algorithm set"""
	master_algorithm_file = lookup.get_master_files()[type] #master.csv to write to
	new_uuid = fs.get_uuid()

	#might have to write parameter values for instantiation and create file
	#might want to move file name procedure to filesystem.py
	file_directory = lookup.get_tmp_directories()[type]
	file_name = fs.create_file_from_hash(new_uuid, 'csv')
	file_path = abspath(join(file_directory, file_name))
	fs.make_file(file_path)

	algorithm_info = get_algorithm_info(type, algorithm)
	compatible_types = algorithm_info[lookup.compatibile_types_decorator]

	algorithm_data = [algorithm]
	fs.write_to_csv_file(file_path, [algorithm_data])

	row_data = [(new_uuid, compatible_types, file_path)]
	fs.write_to_csv_file(master_algorithm_file, row_data)

	return new_uuid

def add_to_algorithm_set(type: str, uuid:str, algorithm:str):
	"""adds to the current algorithm set"""
	master_algorithm_file = lookup.get_master_files()[type]
	master_file_data = fs.read_csv_file(master_algorithm_file)

	algorithm_sets = master_file_data[1:]

	uuid_set = list(filter(lambda r: r[0] == uuid, algorithm_sets))
	assert(len(uuid_set) == 1)

	algorithm_set = uuid_set[0] 
	(uuid, compatible_types_set, file_name) = algorithm_set
	compatible_types_set = ast.literal_eval(compatible_types_set)

	algorithm_info = get_algorithm_info(type, algorithm)
	compatible_types_algorithm = algorithm_info[lookup.compatibile_types_decorator]

	new_compatible_types = set(compatible_types_set).intersection(set(compatible_types_algorithm))
	new_compatible_types = list(new_compatible_types)

	if(len(new_compatible_types) == 0):
		raise ValueError('This algorithm cannot be added since it does not work on compatible file types')

	if len(new_compatible_types) != len(compatible_types_set):
		def update_function(row):
			(uuid_row, compatible_types_set, file_name) = row
			if uuid_row == uuid:
				compatible_types_set = new_compatible_types

			return (uuid_row, compatible_types_set, file_name)

		master_file_data_modified = list(map(update_function, master_file_data))
		fs.write_to_csv_file(master_algorithm_file, master_file_data_modified, override=True)

	algorithm_data = [algorithm]
	fs.write_to_csv_file(file_name, [algorithm_data])

	return uuid

def lookup_algorithm_set(type:str, uuid:str):
	all_algorithm_sets = get_all_algorithm_sets(type)
	if uuid not in all_algorithm_sets.keys():
		raise ValueError('uuid not found in algorithm sets of type: ' + type)

	found_set = all_algorithm_sets[uuid]
	found_set[lookup.compatibile_types_decorator] = ast.literal_eval(found_set[lookup.compatibile_types_decorator])
	found_set[lookup.uuid_descriptor] = uuid

	return found_set

def get_all_algorithm_sets(type:str):
	"""gets info on all the current sets of specified type that are in fs"""
	master_algorithm_file = lookup.get_master_files()[type]
	master_file_data = fs.read_csv_file(master_algorithm_file)
	row_data = master_file_data[1:]

	all_set_info = {}
	for algorithm_set in row_data:
		set_info_dict = {}

		(uuid, compatible_types_set, set_file_path) = algorithm_set
		set_info = fs.read_csv_file(set_file_path)

		set_info_dict[lookup.compatibile_types_decorator] = compatible_types_set
		set_info_dict[type] = set_info

		all_set_info[uuid] = set_info_dict

	return all_set_info

def instantiate_algorithm_random(type:str, name_of_method:str):
	"""returns an instantiated class with random arguments""" 
	algo_params = get_algorithm_info(type, name_of_method, params_only=True)

	random_parameters = []
	for param in algo_params.keys():
		param_type = algo_params[param]
		random_param_value = generate_param(param_type)

		random_parameters.append(random_param_value)


	return instantiate_algorithm(type, name_of_method, random_parameters)

def instantiate_algorithm(type:str, name_of_method:str, parameters:list):
	"""returns an instantiated class with arguments args""" 
	assert(type is not None)

	algorithm_source = None
	if type == lookup.embeddor:
		algorithm_source = embeddors
	else:
		algorithm_source = detectors

	if parameters:
		instance = getattr(algorithm_source, name_of_method)(*parameters)
	else:
		instance = getattr(algorithm_source, name_of_method)()

	return instance

def instantiate_algorithm_set(type:str, algorithm_set, params=None):
	algorithm_names = algorithm_set[type]
	algorithm_instances = []

	if params:
		for idx, name in enumerate(algorithm_names):
			algorithm_instances.append(instantiate_algorithm(type, name[0], params[idx]))
	else:
		for idx, name in enumerate(algorithm_names):
			algorithm_instances.append(instantiate_algorithm_random(type, name[0]))

	return algorithm_instances

def get_algorithm_info(type:str, name_of_method:str, params_only=False):
	info = get_all_algorithms(type)
	matching_algorithm = list(filter(lambda d: d[lookup.algorithm_name] == name_of_method, info))

	#TODO error handling#
	if not matching_algorithm:
		return {}
	else:
		matching_algorithm = matching_algorithm[0]

	if params_only:
		return matching_algorithm[lookup.parameters]

	return matching_algorithm

def get_algorithm_names(type:str):
	info = get_all_algorithms(type)
	return list(map(lambda d: d[lookup.algorithm_name], info))

def get_all_algorithms(type:str):
	assert(type is not None)

	algorithm_source = None
	func_name = None
	if type == lookup.embeddor:
		algorithm_source = embeddors
		func_name = lookup.embed_function
	else:
		algorithm_source = detectors
		func_name = lookup.detect_function

	algorithm_names = set(n for n in algorithm_source.__all__ if getattr(algorithm_source, n))
	algorithm_info = []

	for name in algorithm_names:
		info = {}
		info[lookup.algorithm_name] = name

		#get compatible image types 
		algorithm_class = getattr(algorithm_source, name)
		steganographic_function = getattr(algorithm_class, func_name)
		
		info[lookup.description] = algorithm_class.__doc__
		info[lookup.compatibile_types_decorator] = lookup.get_compatible_types(steganographic_function)

		#get required parameters for instantiation
		args = inspect.signature(algorithm_class.__init__)
		parameters = list((tuple(args.parameters.values())))
		parameters_dict = collections.OrderedDict()
		parameters_without_self = list(filter(lambda p: p.name != 'self', parameters))

		for parameter in parameters_without_self:
			parameter_name = parameter.name
			parameter_type = parameter.annotation.__name__

			parameters_dict[parameter_name] = parameter_type

		info[lookup.parameters]= parameters_dict

		algorithm_info.append(info)

	return algorithm_info

def calculate_statistics(cover_results, stego_results):
	"""calculates all the relevant analyzer statistics"""
	raise NotImplementedError

