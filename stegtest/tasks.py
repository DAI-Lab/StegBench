import os
import shutil
import random

import stegtest.utils.filesystem as fs
import stegtest.utils.lookup as lookup
import stegtest.utils.algorithm as algo
import stegtest.utils.processor as processor

from stegtest.types.generator import Generator
from stegtest.types.analyzer import Analyzer 

from os.path import abspath, join
from multiprocessing import Pool
from functools import partial

def embed_external(input_partition, output_partition, embeddors, idx):
	"""multiprocessing funtion for embedding"""
	try:
		embeddors[idx].embed_bulk(input_partition[idx], output_partition[idx])
		return True
	except:
		return False

class DefaultGenerator(Generator):
	""""runs all the generation tasks"""
	def __init__(self, embeddor_set, params=None):
		embeddor_names = embeddor_set[lookup.embeddor]
		assert(params is None or len(params) == len(embeddor_names))

		self.embeddor_set = embeddor_set
		self.compatible_types = set(self.embeddor_set[lookup.compatibile_types_decorator])
		self.embeddors = algo.instantiate_algorithm_set(lookup.embeddor, embeddor_set, params)

	def generate(self, source_db:str, divided=True, random_parameters=False):
		"""generates a test DB. if divided, embeddors are randomly distributed each of the db images. otherwise each image undergoes an operation by each embeddor"""
		if random_parameters:
			#need to update parameters for each embedding process (need some sort of bypass using update_parameters here
			raise NotImplementedError
		
		db_information = lookup.get_source_db_info(source_db)
		db_compatible_states = set(db_information[lookup.compatible_descriptor])

		db_embed_compatible = db_compatible_states.intersection(self.compatible_types)
		
		if len(db_embed_compatible) <= 0:
			raise ValueError('The embeddor set and dataset are not compatible')

		image_dict = lookup.get_image_list(db_information[lookup.uuid_descriptor])
		image_dict = list(filter(lambda img_info: img_info[lookup.image_type] in db_embed_compatible, image_dict))
		random.shuffle(image_dict)

		num_images = len(image_dict)
		num_embeddors = len(self.embeddors)

		input_partition = []
		output_partition = []

		embeddor_set_uuid = self.embeddor_set[lookup.uuid_descriptor]
		embeddor_names = self.embeddor_set[lookup.embeddor]

		output_directory_name = fs.create_name_from_hash(fs.get_uuid())
		output_directory = abspath(join(lookup.get_tmp_directories()[lookup.db], output_directory_name))
		
		assert(not fs.dir_exists(output_directory))
		fs.make_dir(output_directory)

		if divided:
			images_per_embeddor = int(num_images / num_embeddors)
			remainder = num_images % num_embeddors #TODO randomly assign this
			for i in range(num_embeddors):
				start_idx = i*images_per_embeddor
				end_idx = (i+1)*images_per_embeddor
				input_list = image_dict[start_idx:end_idx].copy()

				input_partition.append(input_list)
		else:
			input_partition = [image_dict.copy() for i in range(num_embeddors)]

		output_partition = [lookup.generate_output_list(output_directory, input_list) for input_list in input_partition]
		input_partition = [list(map(lambda img_info: img_info[lookup.file_path], partition)) for partition in input_partition]

		embed_bulk = partial(embed_external, input_partition, output_partition, self.embeddors)
		embeddor_idx = list(range(len(self.embeddors)))

		pool = Pool()
		embed_results = pool.map(embed_bulk, embeddor_idx)
		pool.close()
		pool.join()

		partition = [[(input_partition[idx][i], output_partition[idx][i], embeddor_names[idx][0]) for i in range(len(input_partition[idx]))] for idx in range(num_embeddors)]
		db_uuid = processor.process_steganographic_directory(output_directory, partition, embeddor_set_uuid, source_db)

		return db_uuid

def analyze_detector(input_list, detector):
	"""analyzes a detector on a specific list"""
	results = detector.detect_bulk(input_list)
	return results


class DefaultAnalyzer(Analyzer):
	""""runs all the analyzer tasks"""
	def __init__(self, detector_set, params=None):
		detector_names = detector_set[lookup.detector]
		assert(params is None or len(params) == len(detector_names))

		self.detector_set = detector_set
		self.compatible_types = set(self.detector_set[lookup.compatibile_types_decorator])
		self.detectors = algo.instantiate_algorithm_set(lookup.detector, detector_set, params)

	def analyze(self, testdb_uuid:str, write_results=None):
		print('preparing db for evaluation')
		db_information = lookup.get_steganographic_db_info(testdb_uuid)
		db_compatible_states = set(db_information[lookup.compatible_descriptor])

		db_embed_compatible = db_compatible_states.intersection(self.compatible_types)
		
		if len(db_embed_compatible) <= 0:
			raise ValueError('The embeddor set and dataset are not compatible')

		image_dict = lookup.get_image_list(testdb_uuid)

		cover_files = list(map(lambda img: img[lookup.source_image], image_dict))
		stego_files = list(map(lambda img: img[lookup.file_path], image_dict))

		analyze_cover = partial(analyze_detector, cover_files)
		analyze_stego = partial(analyze_detector, stego_files)

		pool = Pool()
		print('processing cover results...')
		cover_results = pool.map(analyze_cover, self.detectors)
		print('processing stego results...')
		stego_results = pool.map(analyze_stego, self.detectors)
		pool.close()
		pool.join()

		print('calcualating statistics...')
		detector_names = self.detector_set[lookup.detector]
		statistics = algo.calculate_statistics(detector_names, cover_results, stego_results)

		if write_results:
			output_directory = lookup.get_tmp_directories()[lookup.detector]
			output_file_name = fs.create_file_from_hash(testdb_uuid + self.detector_set[lookup.uuid_descriptor], 'csv')

			output_file_path = abspath(join(output_directory, output_file_name))

			statistics_header = [lookup.get_statistics_header()]
			statistics_rows = [list(detector_statistic.values()) for detector_statistic in statistics]
			print('writing statistics to file...')

			statistics_data = statistics_header + statistics_rows

			fs.write_to_csv_file(output_file_path, statistics_data)

			return output_file_path

		return statistics

class Scheduler():
	"""schedules the generator and analyzer task"""
	def __init__(self, generator:Generator, analyzer:Analyzer):
		self.generator = generator
		self.analyzer = analyzer

	def initialize():
		lookup.initialize_filesystem()

	def run_pipeline(self, source_db):
		generated_db = self.generator.generate(source_db)
		path_to_output = self.analyzer.analyze(generated_db)

		return path_to_output