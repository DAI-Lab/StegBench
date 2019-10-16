import stegtest.utils.filesystem as fs
import stegtest.utils.lookup as lookup
import stegtest.utils.images as img

from os import listdir
from os.path import isfile, join, abspath

"""IN GENERAL

we need to go over all the images to find specific information 
- size
- type
- other image info (find helpers online)
- exif data??
- ch

"""
def process_image_file(path_to_image):
	"""processes an image file"""
	assert(fs.file_exists(path_to_image))
	info = img.get_image_info(path_to_image)
	return info

def process_image_directory(path_to_directory, db_name):
	"""processes an image directory"""
	db_master_file = lookup.get_master_files()[lookup.db]
	dataset_directory = lookup.get_dataset_directory()[lookup.db]
	target_directory = join(dataset_directory, db_name)

	assert(fs.dir_exists(path_to_directory))
	assert(fs.dir_exists(dataset_directory))
	assert(not fs.dir_exists(target_directory))

	absolute_path = abspath(path_to_directory)

	files = [join(absolute_path, f) for f in listdir(absolute_path) if img.is_image_file(join(absolute_path, f))]

	info_images = []
	for f in files:
		info_images.append(list(process_image_file(f).values()))

	variables = img.get_image_info_variables()
	rows = [variables] + info_images

	fs.make_dirs(target_directory)
	fs.write_to_csv_file(join(target_directory, lookup.master_file), rows)

	num_images = len(files)
	db_uuid = fs.get_uuid()
	dataset_info = [(db_uuid, db_name, num_images)]

	fs.write_to_csv_file(db_master_file, dataset_info)

def add_embeddor_to_file(algorithm, weight, path_to_file):
    """adds embeddor"""
    assert(file_exists(path_to_file))

    embeddor_info = lookup.lookup_embeddor(algorithm)
    embeddor_info.append(weight)

def add_detector_to_file(algorithm, path_to_file):
    """adds embeddor"""
    assert(file_exists(path_to_file))

    detector_info = lookup.lookup_detector(algorithm)
    fs.write_to_csv_file(path_to_file, detector_info)