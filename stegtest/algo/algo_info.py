import inspect
import collections
import numpy as np

from collections import defaultdict
from sklearn.metrics import roc_auc_score, average_precision_score
import scikitplot as skplt
import matplotlib.pyplot as plt

import stegtest.algo.algo_processor as algo_processor
import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs

import math
import scipy

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

def calculate_statistics_threshold(detector_results):
	"""calculates all the relevant analyzer statistics"""
	metrics = collections.OrderedDict()
	labels = np.array(list(map(lambda d: 1 if d[lookup.label] == lookup.stego else 0, detector_results)))
	prediction_single_classes = np.array(list(map(lambda d: float(d[lookup.result]), detector_results)))
	prediction_both_classes = np.array(list(map(lambda d: (float(d[lookup.result]), 1.0 - float(d[lookup.result])), detector_results)))

	if len(set(labels)) == 1:
		print('roc values require at least 2 labels in the test dataset')
		return {lookup.result_metric: metrics}

	auc_score = roc_auc_score(labels, prediction_single_classes)
	ap_score = average_precision_score(labels, prediction_single_classes)
	
	skplt.metrics.plot_roc(labels, prediction_both_classes)

	detector_result_dir = lookup.get_algo_asset_dirs()[lookup.detector]
	roc_curve_name = fs.get_uuid() + '-roc.png'
	roc_curve_path = abspath(join(detector_result_dir, roc_curve_name))
	plt.savefig(roc_curve_path, bbox_inches='tight')

	metrics[lookup.roc_auc] = auc_score
	metrics[lookup.ap_score] = ap_score
	metrics[lookup.roc_curve] = roc_curve_path

	return {lookup.result_metric: metrics}

def calculate_statistics_classifier(detector_results):
	"""calculates all the relevant analyzer statistics"""
	metrics = collections.OrderedDict()
	raw_results = collections.OrderedDict()

	result_true_cover = list(filter(lambda d: d[lookup.label] == lookup.cover, detector_results))
	result_true_stego = list(filter(lambda d: d[lookup.label] == lookup.stego, detector_results))

	result_correct_cover = list(filter(lambda d: d[lookup.result] == lookup.cover, result_true_cover))
	result_correct_stego = list(filter(lambda d: d[lookup.result] == lookup.stego, result_true_stego))

	total_cover = len(result_true_cover)
	total_stego = len(result_true_stego)
	total_results = total_stego + total_cover

	assert(total_results > 0)

	true_negative_total = len(result_correct_cover)
	true_positive_total = len(result_correct_stego)
	false_positive_total = total_cover - true_negative_total
	false_negative_total = total_stego - true_positive_total

	raw_results[lookup.true_positive_raw] = true_positive_total
	raw_results[lookup.true_negative_raw] = true_negative_total
	raw_results[lookup.total_stego_raw] = total_stego
	raw_results[lookup.total_cover_raw] = total_cover

	if total_cover == 0:
		metrics[lookup.accuracy] = true_positive_total / total_results
		return {lookup.result_metric: metrics, lookup.result_raw: raw_results}
	elif total_stego == 0:
		metrics[lookup.accuracy] = true_negative_total / total_results
		return {lookup.result_metric: metrics, lookup.result_raw: raw_results}

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

	metrics[lookup.false_positive_rate] = fpr
	metrics[lookup.false_negative_rate] = fnr
	metrics[lookup.true_negative_rate] = tnr
	metrics[lookup.negative_predictive_value] = npv
	metrics[lookup.false_discovery_rate] = fdr
	metrics[lookup.true_positive_rate] = tpr
	metrics[lookup.positive_predictive_value] = ppv
	metrics[lookup.accuracy] = accuracy

	return {lookup.result_metric: metrics, lookup.result_raw: raw_results}

def calculate_statistics(*results):
	all_results = defaultdict(list)
	for result in results:
		for key,value in result.items():
			all_results[key].extend(value)

	statistics = {}
	for detector in all_results:
		detector_info = get_algorithm_info(lookup.detector, detector)

		if detector_info[lookup.DETECTOR_TYPE] == lookup.binary_detector:
			statistics[detector] = calculate_statistics_classifier(all_results[detector])
		else:
			statistics[detector] = calculate_statistics_threshold(all_results[detector])

	return statistics



