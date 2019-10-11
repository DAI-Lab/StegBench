import stegtest.utils.bindings as bd
import stegtest.utils.helpers.download_helpers as dh

db_routines = { 'BOSS': dh.download_from_BOSS, 'BOWS2': dh.download_from_BOWS2, 'BURST': dh.download_from_BURST, 'COCO': dh.download_from_COCO, 'DRESDEN': dh.download_from_DRESDEN, 'RAISE': dh.download_from_RAISE, 'ImageNet': dh.download_from_ImageNet}

def get_download_routines():
	return db_routines

def download_routine(name, *args):
	#dispatch this to a helper
	#check if already present lol 
	db_routines = get_download_routines() 
	assert(name in db_routines.keys())
	temp_folders = bd.get_tmp_directories()
	
	tmp_directory = db_routines[name](temp_folders[bd.db], *args)
	process_directory(tmp_directory)

def download_from_file(file):
	#dipatch this to a helper routine or probably this
	tmp_directory = None
	process_directory(tmp_directory)