import inspect

import stegtest.embeddors as embeddors
import stegtest.detectors as detectors
import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs

from os.path import abspath

def lookup_algorithm_set(uuid:str, type:str):
	asset(type is not None)

	master_algorithm_file = None
	if type == embeddor:
		master_algorithm_file = lookup.get_master_files()[embeddor]
	else:
		master_algorithm_file = lookup.get_master_files()[detector]

	algorithm_sets = fs.read_csv_file(master_algorithm_file)

	#1st element is UUID as described by procedure. 
	#TODO need a better way to ensure this to avoid breaking everything.
	uuid_set = list(filter(lambda r: r[0] == uuid), algorithm_sets)
	assert(len(uuid_set) == 1)

	#TODO potentially some more filtering on this... returning class objects ready to be instantiated...
	return uuid_set[0]

def instantiate_algorithm(name_of_method:str, type:str, *args):
	"""returns an instantiated class with arguments args""" 
	assert(type is not None)

	algorithm_source = None
	if type == lookup.embeddor:
		algorithm_source = embeddors
	else:
		algorithm_source = detectors

	algorithm = getattr(algorithm_names, name_of_method)(*args)
	return algorithm

def get_algorithm_info(type:str):
	assert(type is not None)

	algorithm_source = None
	if type == lookup.embeddor:
		algorithm_source = embeddors
	else:
		algorithm_source = detectors

	algorithm_names = set(n for n in algorithm_source.__all__ if getattr(algorithm_source, n))
	algorithm_info = []

	for name in algorithm_names:
		info = {}
		info['name'] = name

		algorithm_class = getattr(algorithm_source, name)
		args = inspect.signature(algorithm_class.__init__)

		parameters = list((tuple(args.parameters.values())))
		parameters_without_self = list(filter(lambda p: p.name != 'self', parameters))

		for parameter in parameters_without_self:
			parameter_name = parameter.name
			parameter_type = parameter.annotation.__name__

			info[parameter_name] = parameter_type

		algorithm_info.append(info)

	return algorithm_info