import stegtest.utils.filesystem as fs
import stegtest.utils.lookup as lookup
import stegtest.db.images as img
import collections

from os import listdir
from os.path import isfile, join, abspath

from multiprocessing import Pool
from functools import partial

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

def process_steganographic_list(partition, embeddor_uuid):
	"""processes a partition of steganographic images"""
	info_images = []

	compatible_types = set()

	for embeddor_generated_set in partition:
		for file_set in embeddor_generated_set:
			input_file = file_set[lookup.INPUT_IMAGE_PATH]
			output_file = file_set[lookup.OUTPUT_IMAGE_PATH]
			
			info_image = process_image_file(abspath(output_file))

			compatible_types.add(info_image[lookup.image_type])
			info_image = list(info_image.values())

			info_image.append(input_file)
			info_image.append(embeddor_uuid)
			info_images.append(info_image)

	return info_images, compatible_types

def modify_images(input_directory, operation, args):
	input_directory = abspath(input_directory)
	file_names = [f for f in listdir(input_directory) if img.is_image_file(join(input_directory, f))]

	dataset_directory = lookup.get_db_dirs()[lookup.dataset]

	output_directory_name = fs.get_uuid()
	output_directory = join(dataset_directory, output_directory_name)
	output_directory = abspath(output_directory)
	fs.make_dir(output_directory)

	input_files = [join(input_directory, f) for f in file_names]
	output_files = [join(output_directory, f) for f in file_names]

	partition = [{lookup.input_file_header: input_files[idx], lookup.output_file_header: output_files[idx]} for idx in range(len(file_names))]
	operation_function = partial(img.apply_operation, operation, args) 

	pool = Pool()
	operation_results = pool.map(operation_function, partition)
	pool.close()
	pool.join()

	return output_files

def process_image_directory(path_to_directory, db_name, operation=None, args=None):
	"""processes an image directory"""
	source_master_file = lookup.get_all_files()[lookup.source_db_file]
	metadata_directory = lookup.get_db_dirs()[lookup.metadata]

	db_uuid = fs.get_uuid()
	target_directory = join(metadata_directory, db_uuid)

	assert(fs.dir_exists(path_to_directory))
	assert(fs.dir_exists(metadata_directory))

	absolute_path = abspath(path_to_directory)

	files = [join(absolute_path, f) for f in listdir(absolute_path) if img.is_image_file(join(absolute_path, f))]

	if operation:
		if args is None:
			args = lookup.get_default_image_operation_values()[operation]
		files = modify_images(absolute_path, operation, args)
	else:
		files = [join(absolute_path, f) for f in listdir(absolute_path) if img.is_image_file(join(absolute_path, f))]

	info_images, compatible_types = process_image_list(files)

	variables = lookup.get_image_info_variables()
	rows = [variables] + info_images

	fs.make_dir(target_directory)
	fs.write_to_csv_file(join(target_directory, lookup.db_file), rows)

	num_images = len(files)
	compatible_types = list(compatible_types)

	dataset_info = [(db_uuid, db_name, num_images, compatible_types)]
	fs.write_to_csv_file(source_master_file, dataset_info)

	return db_uuid

def process_steganographic_directory(partition, embeddor_set, source_db_uuid):
	"""processes a steganographic directory"""
	embedded_master_file = lookup.get_all_files()[lookup.embedded_db_file]
	metadata_directory = lookup.get_db_dirs()[lookup.metadata]

	db_uuid = fs.get_uuid()
	target_directory = join(metadata_directory, db_uuid)

	assert(fs.dir_exists(metadata_directory))

	embeddor_names = [embeddor[lookup.name_descriptor] for embeddor in embeddor_set[lookup.embeddor]]
	embeddor_set_uuid = embeddor_set[lookup.uuid_descriptor]

	info_images, compatible_types = process_steganographic_list(partition, embeddor_names)
	variables = lookup.get_steganographic_info_variables()
	rows = [variables] + info_images

	fs.make_dir(target_directory)
	fs.write_to_csv_file(join(target_directory, lookup.db_file), rows)

	num_images = len(info_images)
	compatible_types = list(compatible_types)

	steganographic_dataset_info = [(db_uuid, source_db_uuid, embeddor_set_uuid, num_images, compatible_types)]
	fs.write_to_csv_file(embedded_master_file, steganographic_dataset_info)

	return db_uuid