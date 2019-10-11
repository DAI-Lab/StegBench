embeddor = 'embeddor'
detector = 'detector'
db = 'db'
tmp = 'tmp'
datasets = 'datasets'

master_file = 'master.csv'
embeddor_routines = ['BrokenArrows', 'CloakedPixel', 'F5', 'JpHide', 'JSteg', 'LSB', 'OpenStego', 'Outguess', 'Stegano', 'StegHide', 'StegPy']
detector_routines = ['StegDetect', 'StegExpose', 'YeNet']

def get_master_files():
	return {binding: binding + '/' + master_file for binding in get_top_level_directories().values()}

def get_bindings_list(type):
	bindings = get_master_files()
	return bindings[type]

def get_embed_routines():
	return embeddor_routines

def get_detector_routines():
	return detector_routines

def get_top_level_directories():
	return {embeddor: embeddor, detector: detector, db: db}

def get_tmp_directories():
	tld = get_top_level_directories()
	tmp_directories = {tl: (tl + '/' + tmp) for tl in tld}

	return tmp_directories

def get_dataset_directory():
	return {db: db + '/' + datasets}

def all_directories():
	tld = list(get_top_level_directories().values())
	tmp_directories = list(get_tmp_directories().values())
	dataset_directory = list(get_dataset_directory().values())

	return tld + tmp_directories + dataset_directory

def lookup_embeddor(name_of_method):
	raise NotImplementedError

def lookup_detector(name_of_method):
	raise NotImplementedError

def get_db_names():
	#TODO need to get any additional db names 
	#reads the db file in master.txt to get the list of dbs that we can use
	raise NotImplementedError