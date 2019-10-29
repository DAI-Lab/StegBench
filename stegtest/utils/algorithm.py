import inspect
import ast
import collections

from collections import defaultdict
import stegtest.embeddors as embeddors
import stegtest.detectors as detectors
import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs

import math

from os import listdir
from os.path import abspath, join

def get_set_files(algorithm_type:str):
	set_file_directory = lookup.get_algo_set_dirs()[algorithm_type]
	sets = [{lookup.uuid_descriptor: fs.get_filename(file), lookup.filepath_descriptor: abspath(join(set_file_directory, file))} for file in listdir(set_file_directory)]

	return sets

def create_algorithm_set(algorithm_type:str, algorithm_uuid:str):
	"""creates a new algorithm set"""
	#create set file
	set_uuid = fs.get_uuid()
	set_file_directory = lookup.get_algo_set_dirs()[algorithm_type]
	individual_set_file_path = join(set_file_directory, fs.create_name_from_uuid(set_uuid, 'csv'))

	fs.make_file(individual_set_file_path)

	#gets the data to write to the individual set file
	file_header = lookup.individual_set_header
	algorithm_info = get_algorithm_info(algorithm_type, algorithm_uuid)
	data_to_write = [file_header, [algorithm_info[lookup.uuid_descriptor]]]
	fs.write_to_csv_file(individual_set_file_path, data_to_write)

	return set_uuid

def add_to_algorithm_set(algorithm_type: str, set_uuid:str, algorithm_uuid:str):
	"""adds to the current algorithm set"""
	algorithm_set = get_algorithm_set(algorithm_type, set_uuid)
	algorithm_info = get_algorithm_info(algorithm_type, algorithm_uuid)
	
	compatible_types_set = set(algorithm_set[lookup.compatible_descriptor])
	compatible_types_algorithm = set(algorithm_info[lookup.compatible_descriptor])
	new_compatible_types = list(compatible_types_set.intersection(compatible_types_algorithm))

	all_set_files = get_set_files(algorithm_type)
	specific_set_file = list(filter(lambda set_file: set_file[lookup.uuid_descriptor] == set_uuid, all_set_files))

	if len(specific_set_file) != 1:
		raise ValueError('uuid: ' + set_uuid + ' not found among algorithm sets of type: ' + algorithm_type)

	specific_set_info = specific_set_file[0]
	set_file_path = specific_set_info[lookup.filepath_descriptor]

	algorithm_data = [[algorithm_info[lookup.uuid_descriptor]]]
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
		config_info = fs.read_config_file(config_file) #move this to config.py
		for algo_dict in algo_info:
			assert(algo_dict[lookup.name_descriptor] in config_info)
			algo_info = config_info[algo_dict[lookup.name_descriptor]]

			algo_info[lookup.compatible_descriptor] = ast.literal_eval(algo_info[lookup.compatible_descriptor])
			if lookup.embedding_descriptor in algo_info.keys():
				algo_info[lookup.embedding_descriptor] = float(algo_info[lookup.embedding_descriptor])

			algo_dict.update(algo_info)
			all_info.append(algo_dict)

	return all_info

""""TODO calculate accuracy scores"""

def calculate_statistics(detector_names, all_cover_results, all_stego_results, paired=True):
	"""calculates all the relevant analyzer statistics"""
	assert(len(all_cover_results) == len(all_stego_results) and len(all_cover_results) == len(detector_names))
	# print(all_cover_results)
	# print(all_stego_results)
	all_results = []

	for idx, detector_info in enumerate(detector_names):
		#TODO get rid of this sort of referencing
		detector_name = detector_info[0]
		cover_results = [1 if result else 0 for result in all_cover_results[idx]]
		stego_results = [1 if result else 0 for result in all_stego_results[idx]]

		# print(cover_results)
		# print(stego_results)

		# if paired:
		# 	assert(len(cover_results) == len(stego_results))

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
		results[lookup.detector] = detector_name

		all_results.append(results)

	return all_results




