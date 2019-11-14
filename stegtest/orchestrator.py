import os
import shutil
import random
import sys
import copy

import stegtest.utils.filesystem as fs
import stegtest.utils.lookup as lookup
import stegtest.utils.generator as generator

import stegtest.algo.algo_info as algo
import stegtest.algo.algo_processor as algo_processor

import stegtest.executor.embeddor_cmds as embeddor_cmds
import stegtest.executor.detector_cmds as detector_cmds
import stegtest.executor.verify_cmds as verify_cmds
import stegtest.executor.runner as runner

import stegtest.db.processor as processor

from os.path import abspath, join
from pathos.multiprocessing import ThreadPool as Pool
from functools import partial
from collections import defaultdict

class Embeddor():
	""""runs all the generation tasks"""
	def __init__(self, embeddor_set):
		self.embeddors = embeddor_set[lookup.embeddor]
		self.max_embedding_ratio = embeddor_set[lookup.embedding_descriptor]
		self.compatible_types = embeddor_set[lookup.compatible_descriptor]
		
		self.embeddor_set = embeddor_set

	def embed_db(self, partition, source_db_uuid, payload):
		all_pre_cmds = []
		all_cmds = []
		all_post_cmds = []
		all_termination_cmds = []

		#TODO VALIDATE THE PARTITION...
		print('generating commands...')

		for idx, embeddor in enumerate(self.embeddors):
			embeddor_params = copy.deepcopy(partition[idx])
			pre_cmds, cmds, post_cmds, termination_cmds = embeddor_cmds.generate_commands(embeddor, embeddor_params)
			all_pre_cmds += pre_cmds
			all_cmds += cmds
			all_post_cmds += post_cmds 
			all_termination_cmds += termination_cmds

		print('commands generated...')

		print('setting up embeddors...')
		runner.run_pool(all_pre_cmds)
		print('completed.')
		print('embedding...')
		runner.run_pool(all_cmds)
		print('completed.')
		print('processing embeding results...')
		runner.run_pool(all_post_cmds)
		print('completed.')
		print('terminating processes...')
		runner.run_pool(all_termination_cmds)
		print('completed.')

		db_uuid = processor.process_steganographic_directory(partition, self.embeddor_set, source_db_uuid, payload)

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

		ratio_embeddor = partial(generator.secret_message_from_embedding, embedding_ratio) 
		secret_message = [list(map(ratio_embeddor, input_list)) for input_list in input_partition]
		output_partition = [generator.generate_output_list(embeddor, output_directory, input_partition[idx]) for idx, embeddor in enumerate(self.embeddors)]

		partition = [[{
						lookup.INPUT_IMAGE_PATH: input_partition[i][j][lookup.file_path], 
						lookup.OUTPUT_IMAGE_PATH: output_partition[i][j],
						lookup.PAYLOAD: embedding_ratio,
						lookup.SECRET_TXT_PLAINTEXT: secret_message[i][j],
						lookup.PASSWORD: generator.generate_password(),
						}
		 			for j in range(len(input_partition[i]))] for i in range(num_embeddors)]

		db_uuid = self.embed_db(partition, source_db, embedding_ratio)

		return db_uuid

class Verifier():
	""""runs all the generation tasks"""
	def verify(self, db:str):
		db_info = lookup.get_steganographic_db_info(db)
		db_images = lookup.get_image_list(db_info[lookup.uuid_descriptor])

		#need to group properly....
		#need to read parameter assets	#group all config files and batch read all the information properly... 
		sorted_by_embeddor = defaultdict(list)
		for image_info in db_images:
			image_info[lookup.INPUT_IMAGE_PATH] = image_info[lookup.file_path]
			sorted_by_embeddor[image_info[lookup.uuid_descriptor]].append(image_info)

		all_pre_cmds = []
		all_cmds = []
		all_post_cmds = []
		all_termination_cmds = []

		all_embeddors = {}

		for embeddor_uuid in sorted_by_embeddor:
			embeddor = algo.get_algorithm_info(lookup.embeddor, embeddor_uuid)
			all_embeddors[embeddor_uuid] = embeddor
			verify_params = copy.deepcopy(sorted_by_embeddor[embeddor_uuid])
			
			pre_cmds, cmds, post_cmds, termination_cmds = verify_cmds.generate_commands(embeddor, verify_params)
			all_pre_cmds += pre_cmds
			all_cmds += cmds
			all_post_cmds += post_cmds 
			all_termination_cmds += termination_cmds

		print('running pre commands')
		runner.run_pool(all_pre_cmds)
		print('completed.')
		print('running commands')
		runner.run_pool(all_cmds)
		print('completed.')
		print('running post commands.')
		runner.run_pool(all_post_cmds)
		verification_results = algo_processor.verify_embedding(db, all_embeddors)
		print('completed.')
		print('terminating processes...')
		runner.run_pool(all_termination_cmds)
		print('completed.')
		
		return verification_results

class Detector():
	""""runs all the analyzer tasks"""
	def __init__(self, detector_set):
		self.detector_set = detector_set
		self.detectors = detector_set[lookup.detector]
		self.compatible_types = detector_set[lookup.compatible_descriptor]

	def detect_list(self, image_list:str, db_uuid:str):
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

		print('setting up detectors...')
		runner.run_pool(all_pre_cmds)
		print('completed.')
		print('analyzing images...')
		runner.run_pool(all_cmds)
		print('completed.')
		print('processing image results...')
		runner.run_pool(all_post_cmds)
		results = {algorithm_info[lookup.uuid_descriptor]: algo_processor.compile_results(algorithm_info, db_uuid) for algorithm_info in self.detectors}
		print('completed.')
		print('terminating processes...')
		runner.run_pool(all_termination_cmds)
		print('completed.')

		return results

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
		source_image_list = list(map(lambda cover: {lookup.INPUT_IMAGE_PATH: cover[lookup.file_path]}, source_image_dict))
		stego_image_list = list(map(lambda cover: {lookup.INPUT_IMAGE_PATH: cover[lookup.file_path]}, stego_image_dict))
		

		cover_results = self.detect_list(source_image_list, sourcedb)
		stego_results = self.detect_list(stego_image_list, testdb)


		statistics = algo.calculate_statistics_classifier(cover_results, stego_results)
		return statistics


class Scheduler():
	"""schedules the generator and analyzer task"""
	def __init__(self, generator:Embeddor, verifier:Verifier, analyzer:Detector):
		self.generator = generator
		self.verifier = verifier
		self.analyzer = analyzer

	def initialize(self, config_directories=None, config_files=None):
		lookup.initialize_filesystem(os.getcwd())
		if config_directories:
			[algo_processor.process_config_directory(directory) for directory in config_directories]
		if config_files:
			[algo_processor.process_config_file(file) for file in config_files]

	def run_pipeline(self, source_db):
		generated_db = self.generator.embed(source_db)
		verify = self.verifier.verify(verify)

		if not verify:
			raise ValueError('The db was not properly embedded')

		results = self.analyzer.detect(generated_db)

		return {lookup.uuid_descriptor: generated_db, lookup.result: results}
