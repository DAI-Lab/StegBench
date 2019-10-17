import stegtest.utils.filesystem as fs
import stegtest.utils.lookup as lookup
import stegtest.utils.images as img

from os import listdir
from os.path import isfile, join, abspath

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

	compatible_types = set()

	for f in files:
		info_image = process_image_file(f)
		compatible_types.add(info_image[lookup.image_type]) 

		info_images.append(list(info_image.values()))

	variables = lookup.get_image_info_variables()
	rows = [variables] + info_images

	fs.make_dir(target_directory)
	fs.write_to_csv_file(join(target_directory, lookup.master_file), rows)

	db_uuid = fs.get_uuid()
	num_images = len(files)
	compatible_types = list(compatible_types)

	dataset_info = [(db_uuid, db_name, num_images, compatible_types)]
	fs.write_to_csv_file(db_master_file, dataset_info)

def process_steganographic_directory(path_to_directory, db_name):
	"""processes an image directory"""
	raise NotImplementedError

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