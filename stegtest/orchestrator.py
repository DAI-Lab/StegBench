import os
import shutil
import random
import sys

import stegtest.utils.filesystem as fs
import stegtest.utils.lookup as lookup

import stegtest.algo.algorithm as algo
import stegtest.algo.cmd_generator as cmd_generator
import stegtest.algo.runner as runner

import stegtest.db.processor as processor

from stegtest.types.embeddor import Embeddor
from stegtest.types.detector import Detector 

from os.path import abspath, join
from pathos.multiprocessing import ThreadPool as Pool
from functools import partial

class DefaultEmbeddor(Embeddor):
	""""runs all the generation tasks"""
	def __init__(self, embeddor_set):
		self.embeddors = embeddor_set[lookup.embeddor]
		self.max_embedding_ratio = embeddor_set[lookup.embedding_descriptor]
		self.compatible_types = embeddor_set[lookup.compatible_descriptor]

	def embed(self, source_db:str, embedding_ratio:float):
		"""generates a test DB. if divided, embeddors are randomly distributed each of the db images. otherwise each image undergoes an operation by each embeddor"""
		db_information = lookup.get_source_db_info(source_db)
		db_compatible_states = set(db_information[lookup.compatible_descriptor])

		db_embed_compatible = db_compatible_states.intersection(self.compatible_types)
		
		if len(db_embed_compatible) <= 0:
			raise ValueError('The embeddor set and dataset are not compatible')

		if embedding_ratio > self.max_embedding_ratio:
			raise ValueError('The embeddor set cannot support this embedding ratio')

		image_dict = lookup.get_image_list(db_information[lookup.uuid_descriptor])
		image_dict = list(filter(lambda img_info: img_info[lookup.image_type] in db_embed_compatible, image_dict))
		random.shuffle(image_dict)

		num_images = len(image_dict)
		num_embeddors = len(self.embeddors)

		input_partition = []
		output_partition = []

		# embeddor_set_uuid = self.embeddor_set[lookup.uuid_descriptor]
		# embeddor_names = self.embeddor_set[lookup.embeddor]

		output_directory_name = fs.get_uuid()
		output_directory = abspath(join(lookup.get_db_dirs()[lookup.dataset], output_directory_name))
		
		assert(not fs.dir_exists(output_directory))
		fs.make_dir(output_directory)

		images_per_embeddor = int(num_images / num_embeddors)
		remainder = num_images - images_per_embeddor*num_embeddors #TODO randomly assign this
		for i in range(num_embeddors):
			start_idx = i*images_per_embeddor
			end_idx = (i+1)*images_per_embeddor
			input_list = image_dict[start_idx:end_idx].copy()

			input_partition.append(input_list)

		for idx in range(remainder):
			input_partition[idx].append(image_dict[idx + num_embeddors*images_per_embeddor].copy())

		output_partition = [lookup.generate_output_list(output_directory, input_list) for input_list in input_partition]
		embedding_ratio = [[embedding_ratio for i in range(len(input_list))] for input_list in input_partition]

		#using embedding ratio, calculate the secret message

		# print(input_partition)
		# print(output_partition)

		cmds = [cmd_generator.generate_command(embeddor, input_partition, output_partition) for embeddor in self.embeddors]
		print(cmds)
		runner.run_pool(cmds)

		# embed_bulk = partial(embed_external, bpp_partition, input_partition, output_partition, self.embeddors)
		# embeddor_idx = list(range(len(self.embeddors)))

		# input_partition = [list(map(lambda img_info: img_info[lookup.file_path], partition)) for partition in input_partition]
		# partition = [[(input_partition[idx][i], output_partition[idx][i], embeddor_names[idx][0]) for i in range(len(input_partition[idx]))] for idx in range(num_embeddors)]
		# db_uuid = processor.process_steganographic_directory(output_directory, partition, embeddor_set_uuid, source_db)

		return '1'

class DefaultDetector(Detector):
	""""runs all the analyzer tasks"""
	def __init__(self, detector_set):
		detector_names = detector_set[lookup.detector]

		self.detector_set = detector_set
		self.compatible_types = set(self.detector_set[lookup.compatibile_types_decorator])
		self.detectors = algo.instantiate_algorithm_set(lookup.detector, detector_set)

	def detect(self, testdb:str, output_file:str=None):
		print('preparing db for evaluation')
		db_information = lookup.get_steganographic_db_info(testdb)
		db_compatible_states = set(db_information[lookup.compatible_descriptor])

		db_embed_compatible = db_compatible_states.intersection(self.compatible_types)
		
		if len(db_embed_compatible) <= 0:
			raise ValueError('The embeddor set and dataset are not compatible')

		image_dict = lookup.get_image_list(testdb)

		cover_files = list(map(lambda img: img[lookup.source_image], image_dict))
		stego_files = list(map(lambda img: img[lookup.file_path], image_dict))

		analyze_cover = partial(analyze_detector, cover_files)
		analyze_stego = partial(analyze_detector, stego_files)

		pool = Pool().map
		print('processing cover results...')
		cover_results = pool(analyze_cover, self.detectors)
		print(cover_results)
		print('processing stego results...')
		stego_results = pool(analyze_stego, self.detectors)
		print('calcualating statistics...')
		detector_names = self.detector_set[lookup.detector]
		statistics = algo.calculate_statistics(detector_names, cover_results, stego_results)

		if output_file:
			output_directory = lookup.get_tmp_directories()[lookup.detector]
			output_file_name = fs.create_name_from_uuid(fs.get_uuid() , 'csv')

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
	def __init__(self, generator:Embeddor, analyzer:Detector):
		self.generator = generator
		self.analyzer = analyzer

	def initialize():
		lookup.initialize_filesystem()

	def run_pipeline(self, source_db):
		generated_db = self.generator.embed(source_db)
		path_to_output = self.analyzer.detect(generated_db)

		return path_to_output