# import * from stegtest as st


embeddor = 'embeddor'
detector = 'detector'
db = 'db'

master_file = 'master.csv'
db_names = ['BOSS', 'BOWS2', 'BURST', 'COCO', 'DRESDEN', 'RAISE', 'ImageNet']
embeddor_routines = ['BrokenArrows', 'CloakedPixel', 'F5', 'JpHide', 'JSteg', 'LSB', 'OpenStego', 'Outguess', 'Stegano', 'StegHide', 'StegPy']
detector_routines = ['StegDetect', 'StegExpose', 'YeNet']

def get_master_files():
	return {binding: binding + '/' + master_file for binding in get_directories()}

def get_bindings_list(type):
	bindings = get_master_files()
	return bindings[type]

def get_download_routines():
	return ['BOSS', 'BOWS2', 'BURST', 'COCO', 'DRESDEN', 'RAISE', 'ImageNet']

def get_embed_routines():
	return embeddor_routines

def get_detector_routines():
	return detector_routines

def get_directories():
	return [embeddor, detector, db]

def lookup_embeddor(name_of_method):
	raise NotImplementedError

def lookup_detector(name_of_method):
	raise NotImplementedError

def get_db_names():
	raise NotImplementedError
	#TODO need to get any additional db names 
