import os
import shutil
import random

import stegtest.utils.filesystem as fs
import stegtest.utils.lookup as lookup
import stegtest.utils.algorithm as algo

from stegtest.types.generator import Generator
from stegtest.types.analyzer import Analyzer 

NUMBER_PROCESSES = 10

class DefaultGenerator(Generator):
	""""runs all the generation tasks"""
	def __init__(self, embeddor_set, params=[['1'], ['1']]):
		embeddor_names = embeddor_set[lookup.embeddor]
		assert(params is None or len(params) == len(embeddor_names))
		
		self.embeddor_set = embeddor_set
		self.compatible_types = set(embeddor_set[lookup.compatibile_types_decorator])
		self.embeddors = []

		if params:
			for idx, name in enumerate(embeddor_names):
				self.embeddors.append(algo.instantiate_algorithm(lookup.embeddor, name[0], params[idx]))
		else:
			for idx, name in enumerate(embeddor_names):
				self.embeddors.append(algo.instantiate_algorithm_random(lookup.embeddor, name[0]))

		print(self.embeddors)

	def generate(self, source_db, divided=True, random_parameters=False): #returns a db_uuid
		if random_parameters:
			#need to update parameters for each embedding process (need some sort of bypass using update_parameters here
			raise NotImplementedError
		
		db_information = lookup.get_db_info(source_db)
		db_compatible_states = set(db_information[lookup.compatible_descriptor])

		db_embed_compatible = db_compatible_states.intersection(self.compatible_types)
		
		if len(db_embed_compatible) <= 0:
			raise ValueError('The embeddor set and dataset are not compatible')

		image_dict = lookup.get_image_list(db_information[lookup.db_descriptor])
		image_dict = list(filter(lambda img_info: img_info[lookup.image_type] in db_embed_compatible, image_dict))
		random.shuffle(image_dict)

		num_images = len(image_dict)
		num_embeddors = len(self.embeddors)

		input_partition = []
		output_partition = []

		output_directory = lookup.get_tmp_directories()[lookup.db]

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

		for idx, embeddor in enumerate(self.embeddors):
			embeddor.embed_bulk(input_partition[idx], output_partition[idx])

		##NEED TO WRITE METADATA##

		return fs.get_uuid()

class DefaultAnalyzer(Analyzer):
	""""runs all the analyzer tasks"""
	def __init__(self, detectors):
		pass

	def analyze(self, db_uuid): #returns a csv file with results
		pass

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