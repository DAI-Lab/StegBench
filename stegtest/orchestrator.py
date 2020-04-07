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
from typing import Union

class Embeddor():
	""""runs all the generation tasks"""
	def __init__(self, embeddor_set, cores=None):
		self.embeddors = embeddor_set[lookup.embeddor]
		self.max_embedding_ratio = embeddor_set[lookup.embedding_descriptor]
		self.compatible_types = embeddor_set[lookup.compatible_descriptor]
		
		self.embeddor_set = embeddor_set

		self.cores = cores

	def embed_db(self, db_name, partition, source_db_uuid, payload):
		all_pre_cmds = []
		all_cmds = []
		all_post_cmds = []
		all_termination_cmds = []

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
		runner.run_pool(all_pre_cmds, self.cores)
		print('completed.')
		print('embedding...')
		runner.run_pool(all_cmds, self.cores)
		print('completed.')
		print('processing embeding results...')
		runner.run_pool(all_post_cmds, self.cores)
		print('completed.')
		print('terminating processes...')
		runner.run_pool(all_termination_cmds, self.cores)
		print('completed.')

		db_uuid = processor.process_steganographic_directory(partition, db_name, self.embeddor_set, source_db_uuid, payload)

		return db_uuid

	def embed_ratio(self, db_name:str, source_db:str, embedding_ratio:float):
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
		remainder = num_images - images_per_embeddor*num_embeddors
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

		db_uuid = self.embed_db(db_name, partition, source_db, embedding_ratio)

		return db_uuid

class Verifier():
	""""runs all the generation tasks"""
	def __init__(self, cores=None):
		self.cores = cores

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
		runner.run_pool(all_pre_cmds, self.cores)
		print('completed.')
		print('running commands')
		runner.run_pool(all_cmds, self.cores)
		print('completed.')
		print('running post commands.')
		runner.run_pool(all_post_cmds, self.cores)
		verification_results = algo_processor.verify_embedding(db, all_embeddors)
		print('completed.')
		print('terminating processes...')
		runner.run_pool(all_termination_cmds, self.cores)
		print('completed.')
		
		return verification_results

class Detector():
	""""runs all the analyzer tasks"""
	def __init__(self, detector_set, cores=None):
		self.detector_set = detector_set
		self.detectors = detector_set[lookup.detector]
		self.compatible_types = detector_set[lookup.compatible_descriptor]
		self.cores = cores

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
		runner.run_pool(all_pre_cmds, self.cores)
		print('completed.')
		print('analyzing images...')
		runner.run_pool(all_cmds, self.cores)
		print('completed.')
		print('processing image results...')
		runner.run_pool(all_post_cmds, self.cores)
		results = {algorithm_info[lookup.uuid_descriptor]: algo_processor.compile_results(algorithm_info, db_uuid) for algorithm_info in self.detectors}
		print('completed.')
		print('terminating processes...')
		runner.run_pool(all_termination_cmds, self.cores)
		print('completed.')

		return results

	def detect(self, test_dbs:list):
		print('collecting results from following databases: ' + str(test_dbs))
		results = []
		for db in test_dbs:
			db_info = lookup.get_db_info(db)
			db_compatible = set(db_info[lookup.compatible_descriptor])
			db_detect_compatible = db_compatible.intersection(self.compatible_types)
			
			if len(db_detect_compatible) != len(db_compatible):
				raise ValueError('The detector set and dataset are not compatible')

			db_image_dict = lookup.get_image_list(db)
			db_image_list = list(map(lambda img: {lookup.INPUT_IMAGE_PATH: img[lookup.file_path]}, db_image_dict))
			db_results = self.detect_list(db_image_list, db)

			results.append(db_results)

		statistics = algo.calculate_statistics(*results)
		return statistics

class Scheduler():
	"""schedules the generator and analyzer task"""
	def __init__(self, metadata, embeddors:list, detectors:list):
			embeddor_set_uuid = algo.create_algorithm_set(lookup.embeddor, embeddors)
			detector_set_uuid = algo.create_algorithm_set(lookup.detector, detectors)
			embeddor_set = algo.get_algorithm_set(lookup.embeddor, embeddor_set_uuid)
			detector_set = algo.get_algorithm_set(lookup.detector, detector_set_uuid)
			self.metadata = metadata

			cores = None
			if lookup.cores in self.metadata:
				cores = int(self.metadata[lookup.cores])

			self.embeddor = Embeddor(embeddor_set, cores)
			self.verifier = Verifier(cores)
			self.detector = Detector(detector_set, cores)

	def format_results(self, results):
		write_results = []
		for detector_uuid in results:
			result = results[detector_uuid]

			metrics = result[lookup.result_metric]
			metrics[lookup.uuid_descriptor] = detector_uuid
			write_results.append(metrics.keys())
			write_results.append(metrics.values())

			if lookup.result_raw in result:
				raw = result[lookup.result_raw]
				raw[lookup.uuid_descriptor] = detector_uuid
				write_results.append(raw.keys())
				write_results.append(raw.values())

		return write_results

	def run(self, source_dbs:list):
		detect_dbs = list(source_dbs)
		for db in source_dbs:
			print('embedding source db: (' + db + ')')
			generated_db = self.embeddor.embed_ratio(db, float(self.metadata[lookup.payload]))
			verify = self.verifier.verify(generated_db)
			if verify:
				print('generated db is verfied steganographic: (' + generated_db + ')')
			else:
				raise ValueError('The db was not properly embedded')

			detect_dbs.append(generated_db)

		results = self.detector.detect(detect_dbs)

		if lookup.result_file in self.metadata:
			fs.write_to_csv_file(self.metadata[lookup.result_file], self.format_results(results), override=True)

		return results
