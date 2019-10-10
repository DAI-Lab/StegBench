# import * from stegtest as st


embeddor_dir = 'embeddor'
detector_dir = 'detector'
db_dir = 'db'

master_file = 'master.csv'

def get_master_files():
	return {binding: binding + '/' + master_file for binding in get_directories()}

def get_bindings_list(type):
	bindings = get_master_files()
	return bindings[type]

def get_directories():
	return [embeddor_dir, detector_dir, db_dir]

def lookup_embeddor(name_of_method):
	raise NotImplementedError

def lookup_detector(name_of_method):
	raise NotImplementedError


