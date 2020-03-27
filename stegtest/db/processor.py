import stegtest.utils.filesystem as fs
import stegtest.utils.lookup as lookup
import stegtest.db.images as img
import collections
import random

from os import listdir
from os.path import isfile, join, abspath

from multiprocessing import Pool
from functools import partial

def limit_images(path_to_directory, amount_of_images):
	input_directory = abspath(path_to_directory)
	file_names = [join(input_directory, f) for f in listdir(input_directory) if img.is_image_file(join(input_directory, f))]

	random.shuffle(file_names)

	db_directory = abspath(lookup.get_db_dirs()[lookup.dataset])
	shortened_directory = join(db_directory, fs.get_uuid())
	fs.make_dir(shortened_directory)

	copy_files = file_names[:amount_of_images]

	for file in copy_files:
		fs.copy_file(file, shortened_directory)

	return shortened_directory

def train_test_val_split(path_to_directory, train_split, test_split, val_split):
	assert((train_split + test_split + val_split <= 1.0))
	input_directory = abspath(path_to_directory)
	file_names = [join(input_directory, f) for f in listdir(input_directory) if img.is_image_file(join(input_directory, f))]

	random.shuffle(file_names)

	train_size = int(len(file_names)*train_split)
	test_size = int(len(file_names)*test_split)
	val_size = int(len(file_names)*val_split)

	train_files, test_files, val_files = file_names[0:train_size], file_names[train_size:(train_size + test_size)], file_names[(train_size + test_size):(train_size + test_size + val_size)]

	db_directory = abspath(lookup.get_db_dirs()[lookup.dataset])
	train_directory = join(db_directory, fs.get_uuid())
	test_directory = join(db_directory, fs.get_uuid())
	val_directory = join(db_directory, fs.get_uuid())

	fs.make_dir(train_directory)
	fs.make_dir(test_directory)
	fs.make_dir(val_directory)

	directory_pairs = [(train_directory, train_files), (test_directory, test_files), (val_directory, val_files)]

	for directory_pair in directory_pairs:
		copy_directory, copy_files = directory_pair
		for file in copy_files:
			fs.copy_file(file, copy_directory)

	return train_directory, test_directory, val_directory

def get_metadata_operation_args(operation):
	args = {
		lookup.stego: collections.OrderedDict({}),
		lookup.train_test_val_split: collections.OrderedDict({lookup.train: float, lookup.test: float, lookup.validation: float}),
		lookup.limit: collections.OrderedDict({lookup.amount_of_images: int})
	}[operation]

	return args

def process_image_file(path_to_image):
	"""processes an image file"""
	assert(fs.file_exists(path_to_image))
	info = img.get_image_info(path_to_image)
	return info

def process_cover_list(image_list):
	"""processes a list of image files"""
	info_images = []

	compatible_types = set()

	for file in image_list:
		info_image = process_image_file(file)
		compatible_types.add(info_image[lookup.image_type]) 

		info_image = list(info_image.values())
		info_image.append(lookup.cover)
		info_images.append(info_image)

	return info_images, compatible_types


def process_steganographic_list(partition, embeddors):
	"""processes a partition of steganographic images"""
	info_images = []

	compatible_types = set()
	directories = set()

	for idx, embeddor_generated_set in enumerate(partition):
		for file_set in embeddor_generated_set:
			input_file = file_set[lookup.INPUT_IMAGE_PATH]
			output_file = file_set[lookup.OUTPUT_IMAGE_PATH]
			secret_txt = file_set[lookup.SECRET_TXT_PLAINTEXT]
			password = file_set[lookup.PASSWORD]

			directories.add(fs.get_directory(abspath(output_file)))

			info_image = process_image_file(abspath(output_file))

			compatible_types.add(info_image[lookup.image_type])
			info_image = list(info_image.values())

			info_image.append(lookup.stego)
			info_image.append(input_file)
			info_image.append(embeddors[idx][lookup.uuid_descriptor])
			info_image.append(len(secret_txt))
			info_image.append(password)

			info_images.append(info_image)

	assert(len(directories) == 1) #code does not handle multiple output directories for now
	return info_images, compatible_types, list(directories)[0]

def modify_images(input_directory, output_directory, operation_dict):
	input_directory = abspath(input_directory)
	file_names = [f for f in listdir(input_directory) if img.is_image_file(join(input_directory, f))]

	partition = [{lookup.input_file_header: join(input_directory, f), lookup.output_file_header: join(output_directory, f)} for f in file_names]

	output_files = None
	for operation in operation_dict:
		print('applying operation: [' + str(operation) + '] with args -- ' + str(list(img.get_operation_args(operation).keys())) + ' : (' + str(operation_dict[operation]) + ')')
		operation_function = partial(img.apply_operation, operation, operation_dict[operation]) 
		pool = Pool()
		output_files = pool.map(operation_function, partition)
		pool.close()
		pool.join()

		partition = [{lookup.input_file_header: output_file, lookup.output_file_header: output_file} for output_file in output_files]

		print('completed operation.')

	return output_files

def process_image_directory(path_to_directory, db_name, operation_dict):
	"""processes an image directory"""
	source_master_file = lookup.get_all_files()[lookup.source_db_file]
	metadata_directory = lookup.get_db_dirs()[lookup.metadata]
	output_directory = path_to_directory

	db_uuid = fs.get_uuid()
	target_directory = join(metadata_directory, db_uuid)

	assert(fs.dir_exists(path_to_directory))
	assert(fs.dir_exists(metadata_directory))

	absolute_path = abspath(path_to_directory)

	files = [join(absolute_path, f) for f in listdir(absolute_path) if img.is_image_file(join(absolute_path, f))]

	if operation_dict:
		dataset_directory = lookup.get_db_dirs()[lookup.dataset]
		output_directory = abspath(join(dataset_directory, fs.get_uuid()))
		fs.make_dir(output_directory)

		files = modify_images(absolute_path, output_directory, operation_dict)

	else:
		files = [join(absolute_path, f) for f in listdir(absolute_path) if img.is_image_file(join(absolute_path, f))]

	info_images, compatible_types = process_cover_list(files)
	rows = [lookup.cover_image_header] + info_images

	fs.make_dir(target_directory)
	fs.write_to_csv_file(join(target_directory, lookup.db_file), rows)

	num_images = len(files)
	compatible_types = list(compatible_types)

	dataset_info = [(db_uuid, abspath(output_directory), db_name, num_images, compatible_types)]
	fs.write_to_csv_file(source_master_file, dataset_info)

	return db_uuid

def process_steganographic_directory(partition, db_name, embeddor_set, source_db_uuid, payload):
	"""processes a steganographic directory"""
	embedded_master_file = lookup.get_all_files()[lookup.embedded_db_file]
	metadata_directory = lookup.get_db_dirs()[lookup.metadata]

	db_uuid = fs.get_uuid()
	target_directory = join(metadata_directory, db_uuid)

	assert(fs.dir_exists(metadata_directory))

	embeddors = embeddor_set[lookup.embeddor]
	embeddor_set_uuid = embeddor_set[lookup.uuid_descriptor]

	info_images, compatible_types, directory, = process_steganographic_list(partition, embeddors)
	rows = [lookup.steganographic_image_header] + info_images

	fs.make_dir(target_directory)
	fs.write_to_csv_file(join(target_directory, lookup.db_file), rows)

	num_images = len(info_images)
	compatible_types = list(compatible_types)

	steganographic_dataset_info = [(db_uuid, abspath(directory), db_name, num_images, compatible_types, source_db_uuid, embeddor_set_uuid, payload, )]
	fs.write_to_csv_file(embedded_master_file, steganographic_dataset_info)

	return db_uuid

def process_directory(metadata, path_to_directory, db_name, operation_dict):
	print('applying following operations: ' + str(metadata.keys()))

	if lookup.limit in metadata:
		path_to_directory = limit_images(path_to_directory, *metadata[lookup.limit])

	if lookup.train_test_val_split in metadata:
		train_dir, test_dir, val_dir = train_test_val_split(path_to_directory, *metadata[lookup.train_test_val_split])
		train_uuid = process_image_directory(train_dir, db_name + '-train', operation_dict)
		test_uuid = process_image_directory(test_dir, db_name + '-test', operation_dict)
		val_uuid = process_image_directory(val_dir, db_name + '-val', operation_dict)
		
		return [train_uuid, test_uuid, val_uuid]
	else:
		return process_image_directory(path_to_directory, db_name, operation_dict)

def translate_label(label):
	if label == lookup.stego:
		return (0.0, 1.0)
	else:
		return (1.0, 0.0)

def load_data_as_array(db_uuid):
	db_information = lookup.get_db_info(db_uuid)
	image_dict = lookup.get_image_list(db_information[lookup.uuid_descriptor])

	image_info = [(img.get_image_array(img_dict[lookup.file_path]), translate_label(img_dict[lookup.label])) for img_dict in image_dict]
	return image_info

def convert_to_image(path_to_directory, db_name, img_pixel_values):
	for pixels in img_pixel_values:
		file_name = fs.get_uuid() + '.png'
		file_path = join(path_to_directory, file_name)
		img.convert_from_pixels(file_path, pixels)

	db_uuid = pr.process_directory({}, path_to_directory, db_name, {})
	return db_uuid
