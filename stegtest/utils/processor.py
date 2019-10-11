import stegtest.utils.filesystem as fs
import stegtest.utils.bindings as bd

"""IN GENERAL

we need to go over all the images to find specific information 
- size
- type
- other image info (find helpers online)
- exif data??
- ch

"""

def process_file(path_to_file):
	assert(fs.file_exists(path_to_file))

def process_directory(path_to_directory, db_name):
	# assert(fs.dir_exists(path_to_directory))
	# assert(fs.dir_exists(bd.db)) #have a correct working directory
	
	# target_db_directory = fs.dir_exists(bd.db)

	#TODO if already in the current place...just rename the directory
	print('processing directory at: ' + path_to_directory + ' with name: ' + db_name)