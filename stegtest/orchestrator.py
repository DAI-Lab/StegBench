import os
import shutil
import random
import sys
import copy

import stegtest.utils.filesystem as fs
import stegtest.utils.lookup as lookup
import stegtest.utils.param_generator as param_generator

import stegtest.algo.algorithm as algo
import stegtest.algo.embeddor_cmds as embeddor_cmds
import stegtest.algo.detector_cmds as detector_cmds
import stegtest.algo.runner as runner

import stegtest.db.processor as processor

from os.path import abspath, join
from pathos.multiprocessing import ThreadPool as Pool
from functools import partial

class Embeddor():
	""""runs all the generation tasks"""
	def __init__(self, embeddor_set):
		self.embeddors = embeddor_set[lookup.embeddor]
		self.max_embedding_ratio = embeddor_set[lookup.embedding_descriptor]
		self.compatible_types = embeddor_set[lookup.compatible_descriptor]
		
		self.embeddor_set = embeddor_set

	def embed_db(self, partition, source_db_uuid):
		all_pre_cmds = []
		all_cmds = []
		all_post_cmds = []
		all_termination_cmds = []

		for idx, embeddor in enumerate(self.embeddors):
			embeddor_params = copy.deepcopy(partition[idx])
			pre_cmds, cmds, post_cmds, termination_cmds = embeddor_cmds.generate_commands(embeddor, embeddor_params)
			all_pre_cmds += pre_cmds
			all_cmds += cmds
			all_post_cmds += post_cmds 
			all_termination_cmds += termination_cmds

		runner.run_pool(all_pre_cmds)
		runner.run_pool(all_cmds)
		runner.run_pool(all_post_cmds)
		runner.run_pool(all_termination_cmds)

		db_uuid = processor.process_steganographic_directory(partition, self.embeddor_set, source_db_uuid)

		return db_uuid

	def embed_ratio(self, source_db:str, embedding_ratio:float):
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

		ratio_embeddor = partial(param_generator.secret_message_from_embedding, embedding_ratio) 
		secret_message = [list(map(ratio_embeddor, input_list)) for input_list in input_partition]
		output_partition = [lookup.generate_output_list(output_directory, input_list) for input_list in input_partition]

		#using embedding ratio, calculate the secret message
		partition = [[{
						lookup.INPUT_IMAGE_PATH: input_partition[i][j][lookup.file_path], 
						lookup.OUTPUT_IMAGE_PATH: output_partition[i][j],
						lookup.SECRET_TXT_PLAINTEXT: secret_message[i][j],
						}
		 			for j in range(len(input_partition[i]))] for i in range(num_embeddors)]

		db_uuid = self.embed_db(partition, source_db)

		return db_uuid

class Detector():
	""""runs all the analyzer tasks"""
	def __init__(self, detector_set):
		self.detector_set = detector_set
		self.detectors = detector_set[lookup.detector]
		self.compatible_types = detector_set[lookup.compatible_descriptor]

	def detect_list(self, image_list:str):
		all_pre_cmds = []
		all_cmds = []
		all_post_cmds = []
		all_termination_cmds = []

		for idx, detector in enumerate(self.detectors):
			pre_cmds, cmds, post_cmds, termination_cmds = detector_cmds.generate_commands(detector, copy.deepcopy(image_list))
			all_pre_cmds += pre_cmds
			all_cmds += cmds
			all_post_cmds += post_cmds 
			all_termination_cmds += termination_cmds

		runner.run_pool(all_pre_cmds)
		runner.run_pool(all_cmds)
		runner.run_pool(all_post_cmds)
		runner.run_pool(all_termination_cmds)

		# cover_files = list(map(lambda img: img[lookup.source_image], image_dict))
		# stego_files = list(map(lambda img: img[lookup.file_path], image_dict))

		# algorithm.process_evaluation_results()
		return []

		#something to do with output file processing lmao


	def detect(self, testdb:str):
		print('preparing db for evaluation')
		stego_db_info = lookup.get_steganographic_db_info(testdb)
		sourcedb = stego_db_info[lookup.source_db]
		source_db_info = lookup.get_source_db_info(sourcedb)

		source_compatible_states = set(source_db_info[lookup.compatible_descriptor])
		embedded_compatible_states = set(stego_db_info[lookup.compatible_descriptor])

		db_embed_compatible = embedded_compatible_states.intersection(source_compatible_states).intersection(self.compatible_types)
		
		if len(db_embed_compatible) != len(embedded_compatible_states):
			raise ValueError('The embeddor set and dataset are not compatible')

		source_image_dict = lookup.get_image_list(sourcedb)
		stego_image_dict = lookup.get_image_list(testdb)

		results_file_name = fs.get_uuid()


		source_image_list = list(map(lambda cover: {lookup.INPUT_IMAGE_PATH: cover[lookup.file_path]}, source_image_dict))
		stego_image_list = list(map(lambda cover: {lookup.INPUT_IMAGE_PATH: cover[lookup.file_path]}, stego_image_dict))


		source_results = self.detect_list(source_image_list)
		stego_results = self.detect_list(stego_image_list)

		statistics = algo.calculate_statistics(self.detectors, source_results, stego_results)
		return statistics
		# if output_file:
		# 	output_directory = lookup.get_tmp_directories()[lookup.detector]
		# 	output_file_name = fs.create_name_from_uuid(fs.get_uuid() , 'csv')

		# 	output_file_path = abspath(join(output_directory, output_file_name))

		# 	statistics_header = [lookup.get_statistics_header()]
		# 	statistics_rows = [list(detector_statistic.values()) for detector_statistic in statistics]
		# 	print('writing statistics to file...')

		# 	statistics_data = statistics_header + statistics_rows

		# 	fs.write_to_csv_file(output_file_path, statistics_data)

		# 	return output_file_path

		# return statistics

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