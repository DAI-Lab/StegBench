import inspect
import collections

from collections import defaultdict

import stegtest.algo.algo_processor as algo_processor
import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs

import math

from os import listdir
from os.path import abspath, join

def get_set_files(algorithm_type:str):
	set_file_directory = lookup.get_algo_set_dirs()[algorithm_type]
	sets = [{lookup.uuid_descriptor: fs.get_filename(file, extension=False), lookup.filepath_descriptor: abspath(join(set_file_directory, file))} for file in listdir(set_file_directory)]

	return sets

def create_algorithm_set(algorithm_type:str, algorithms:[str]):
	"""creates a new algorithm set"""
	#create set file
	set_uuid = fs.get_uuid()
	set_file_directory = lookup.get_algo_set_dirs()[algorithm_type]
	individual_set_file_path = join(set_file_directory, fs.create_name_from_uuid(set_uuid, 'csv'))

	fs.make_file(individual_set_file_path)

	file_header = lookup.individual_set_header
	data_to_write = [file_header]
	for algorithm_uuid in algorithms:
		algorithm_info = get_algorithm_info(algorithm_type, algorithm_uuid)
		data_to_write.append([algorithm_info[lookup.uuid_descriptor]])

	fs.write_to_csv_file(individual_set_file_path, data_to_write)

	return set_uuid

def add_to_algorithm_set(algorithm_type: str, set_uuid:str, algorithms:[str]):
	"""adds to the current algorithm set"""
	algorithm_set = get_algorithm_set(algorithm_type, set_uuid)
	compatible_types_set = set(algorithm_set[lookup.compatible_descriptor])

	algorithm_data = []
	for algorithm_uuid in algorithms:
		algorithm_info = get_algorithm_info(algorithm_type, algorithm_uuid)
		compatible_types_algorithm = set(algorithm_info[lookup.compatible_descriptor])

		compatible_types_set = compatible_types_set.intersection(compatible_types_algorithm)
		algorithm_data.append([algorithm_info[lookup.uuid_descriptor]])

	if(len(compatible_types_set) == 0):
		raise ValueError('algorithm could not be added because it does not support compatible types')

	all_set_files = get_set_files(algorithm_type)
	specific_set_file = list(filter(lambda set_file: set_file[lookup.uuid_descriptor] == set_uuid, all_set_files))

	if len(specific_set_file) != 1:
		raise ValueError('uuid: ' + set_uuid + ' not found among algorithm sets of type: ' + algorithm_type)

	specific_set_info = specific_set_file[0]
	set_file_path = specific_set_info[lookup.filepath_descriptor]

	fs.write_to_csv_file(set_file_path, algorithm_data)

	return set_uuid

def get_algorithm_set(algorithm_type:str, set_uuid:str): #MAKE THIS FASTER by just reading relevant info
	all_algorithm_sets = get_all_algorithm_sets(algorithm_type)
	filtered_set = list(filter(lambda algo_set: algo_set[lookup.uuid_descriptor] == set_uuid, all_algorithm_sets))

	if len(filtered_set) != 1:
		raise ValueError('uuid: ' + set_uuid + ' not found among algorithm sets of type: ' + algorithm_type)

	return filtered_set[0]

def get_all_algorithm_sets(algorithm_type:str):
	"""gets info on all the current sets of specified type that are in fs"""
	set_files = get_set_files(algorithm_type)
	all_algorithm_info = get_all_algorithms(algorithm_type)
	set_file_data = []
	for set_info in set_files:
		algorithm_set = {}
		algorithm_set[lookup.uuid_descriptor] = set_info[lookup.uuid_descriptor]

		algorithm_uuid = fs.read_csv_file(set_info[lookup.filepath_descriptor], return_as_dict=True)
		algorithm_uuid = list(map(lambda uuid_info: uuid_info[lookup.uuid_descriptor], algorithm_uuid))
		filtered_algorithms = list(filter(lambda algo: algo[lookup.uuid_descriptor] in algorithm_uuid, all_algorithm_info))

		compatible_types_list = list(map(lambda algo: set(algo[lookup.compatible_descriptor]), filtered_algorithms))
		compatible_types = set.intersection(*compatible_types_list)
		algorithm_set[lookup.compatible_descriptor] = compatible_types

		if algorithm_type == lookup.embeddor:
			embedding_rate_list = list(map(lambda algo: algo[lookup.embedding_descriptor], filtered_algorithms))
			embedding_rate = min(embedding_rate_list)
			algorithm_set[lookup.embedding_descriptor] = embedding_rate

		algorithm_set[algorithm_type] = filtered_algorithms
		set_file_data.append(algorithm_set)

	return set_file_data

def get_algorithm_info(algorithm_type:str, algorithm_uuid:str): #MAKE this faster by just reading relevant info
	all_info = get_all_algorithms(algorithm_type)
	filtered_info = list(filter(lambda config: config[lookup.uuid_descriptor] == algorithm_uuid, all_info))

	if len(filtered_info) != 1:
		raise ValueError('uuid: ' + algorithm_uuid + ' not found among algorithms: ' + algorithm_type)

	return filtered_info[0]

def get_all_algorithms(algorithm_type:str):
	master_file_name = lookup.get_algo_master_files()[algorithm_type]
	master_file_path = lookup.get_all_files()[master_file_name]

	all_info = fs.read_csv_file(master_file_path, return_as_dict=True)

	#group all config files and batch read all the information properly... 
	sorted_by_config = defaultdict(list)
	for algorithm in all_info:
		sorted_by_config[algorithm[lookup.filepath_descriptor]].append(algorithm)

	all_info = []
	for config_file in sorted_by_config.keys():
		algo_info = sorted_by_config[config_file]
		config_info = algo_processor.get_config_from_file(config_file) #move this to config.py
		for algo_dict in algo_info:
			assert(algo_dict[lookup.name_descriptor] in config_info)
			algo_info = config_info[algo_dict[lookup.name_descriptor]]
			algo_dict.update(algo_info)
			all_info.append(algo_dict)

	return all_info

def calculate_statistics_threshold(all_results):
	""""TODO calculate accuracy scores - using thresholding..."""
	raise NotImplementedError

def calculate_statistics_classifier(all_cover_results, all_stego_results):
	"""calculates all the relevant analyzer statistics"""

	#TODO ONLY TAKE IN ONE LIST AND CORRECTLY MARK IT'S TRUE TYPE#
	assert(len(all_cover_results) == len(all_stego_results))
	all_results = {}

	for detector in all_cover_results:
		#TODO get rid of this sort of referencing
		cover_results = [1 if prediction[lookup.result] else 0 for prediction in all_cover_results[detector]]
		stego_results = [1 if prediction[lookup.result] else 0 for prediction in all_stego_results[detector]]

		total_stego = len(stego_results)
		total_cover = len(cover_results)
		total_results = total_stego + total_cover
		
		false_positive_total = sum(cover_results)
		true_negative_total = len(cover_results) - false_positive_total

		true_positive_total = sum(stego_results)
		false_negative_total = len(stego_results) - true_positive_total

		fpr = false_positive_total / total_results
		fnr = false_negative_total / total_results

		tpr = true_positive_total / total_stego
		tnr = true_negative_total / total_cover
		ppv = true_positive_total / (true_positive_total + false_positive_total)
		npv = true_negative_total / (true_negative_total + false_negative_total)
		fnr = 1 - tpr
		fpr = 1 - tnr
		fdr = 1 - ppv
		for_score = 1 - npv
		ts = true_positive_total / (true_positive_total + false_negative_total + false_positive_total)

		accuracy = (true_positive_total + true_negative_total) / (total_results)
		f1_score = 2 * ((ppv*tpr)/(ppv + tpr))
		mcc = (true_positive_total*true_negative_total - false_positive_total*false_negative_total)
		denominator = (true_positive_total + false_positive_total)*(true_positive_total + false_negative_total)*(true_negative_total + false_positive_total)*(true_negative_total + false_negative_total)
		denominator = math.sqrt(denominator)
		mcc /= denominator

		results = collections.OrderedDict()
		results[lookup.false_positive_rate] = fpr
		results[lookup.false_negative_rate] = fnr
		results[lookup.true_negative_rate] = tnr
		results[lookup.negative_predictive_value] = npv
		results[lookup.false_discovery_rate] = fdr
		results[lookup.true_positive_rate] = tpr
		results[lookup.positive_predictive_value] = ppv
		results[lookup.accuracy] = accuracy
		
		all_results[detector] = results

	return all_results



