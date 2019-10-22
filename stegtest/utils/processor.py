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

def process_image_list(image_list):
	"""processes a list of image files"""
	info_images = []

	compatible_types = set()

	for file in image_list:
		info_image = process_image_file(file)
		compatible_types.add(info_image[lookup.image_type]) 

		info_images.append(list(info_image.values()))

	return info_images, compatible_types

def process_steganographic_list(partition):
	"""processes a partition of steganographic images"""
	info_images = []

	compatible_types = set()

	for embeddor_generated_set in partition:
		for file_set in embeddor_generated_set:
			input_file, output_file, algorithm = file_set
			
			info_image = process_image_file(abspath(output_file))

			compatible_types.add(info_image[lookup.image_type])
			info_image = list(info_image.values())

			info_image.append(input_file)
			info_image.append(algorithm)
			info_images.append(info_image)

	return info_images, compatible_types

def process_image_directory(path_to_directory, db_name):
	"""processes an image directory"""
	db_master_file = lookup.get_master_files()[lookup.source]
	dataset_directory = lookup.get_db_directories()[lookup.dataset]

	db_uuid = fs.get_uuid()

	target_directory_name = fs.create_name_from_hash(db_uuid)
	target_directory = join(dataset_directory, target_directory_name)

	assert(fs.dir_exists(path_to_directory))
	assert(fs.dir_exists(dataset_directory))

	absolute_path = abspath(path_to_directory)

	files = [join(absolute_path, f) for f in listdir(absolute_path) if img.is_image_file(join(absolute_path, f))]

	info_images, compatible_types = process_image_list(files)

	variables = lookup.get_image_info_variables()
	rows = [variables] + info_images

	fs.make_dir(target_directory)
	fs.write_to_csv_file(join(target_directory, lookup.master_file), rows)

	num_images = len(files)
	compatible_types = list(compatible_types)

	dataset_info = [(db_uuid, db_name, num_images, compatible_types)]
	fs.write_to_csv_file(db_master_file, dataset_info)

def process_steganographic_directory(output_directory, partition, embeddor_set_uuid, db_source):
	"""processes a steganographic directory"""
	db_master_file = lookup.get_master_files()[lookup.embedded] #TODO fix the master file that we are writing to, TODO fix how we are pulling information
	dataset_directory = lookup.get_db_directories()[lookup.dataset]

	db_uuid = fs.get_uuid()

	target_directory_name = fs.create_name_from_hash(db_uuid)
	target_directory = join(dataset_directory, target_directory_name)

	assert(fs.dir_exists(output_directory))
	assert(fs.dir_exists(dataset_directory))

	info_images, compatible_types = process_steganographic_list(partition)
	variables = lookup.get_steganographic_info_variables()
	rows = [variables] + info_images

	fs.make_dir(target_directory)
	fs.write_to_csv_file(join(target_directory, lookup.master_file), rows)

	num_images = len(info_images)
	compatible_types = list(compatible_types)

	steganographic_dataset_info = [(db_uuid, db_source, embeddor_set_uuid, num_images, compatible_types)]
	fs.write_to_csv_file(db_master_file, steganographic_dataset_info)

	return db_uuid

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