# -*- coding: utf-8 -*-

"""Console script for StegTest."""
import collections
import os
from os.path import abspath, join, relpath

import stegbench.algo.algo_info as algo
import stegbench.algo.algo_processor as algo_processor
import stegbench.algo.robust as robust
import stegbench.db.downloader as dl
import stegbench.db.processor as pr
import stegbench.utils.filesystem as fs
import stegbench.utils.lookup as lookup
from stegbench.orchestrator import Detector, Embeddor, Scheduler, Verifier


def add_config(config=[], directory=[]):
    """adds stegbench configuration"""
    for c in config:
        algo_processor.process_config_file(c)
    for d in directory:
        algo_processor.process_config_directory(d)


def initialize():
    """initializes stegbench configurations"""
    directory = os.getcwd()
    lookup.initialize_filesystem(directory)


def download(routine, name, operation_dict={}, metadata_dict={}):
    """downloads a specified database"""
    assert(routine in dl.get_download_routines().keys())
    operation_dict = collections.OrderedDict({})
    metadata_dict = collections.OrderedDict({})

    download_directory = dl.download_routine(routine)
    db_uuid = pr.process_directory(metadata_dict, download_directory, name, operation_dict)
    print('The UUID of the dataset(s) you have processed is: ' + str(db_uuid))
    return db_uuid


def process(directory, name, operation_dict={}, metadata_dict={}):
    """processes a specified database"""
    db_uuid = pr.process_directory(metadata_dict, directory, name, operation_dict)
    print('The UUID of the dataset(s) you have processed is: ' + str(db_uuid))
    return db_uuid


def add_embeddor(embeddor_uuids, set_uuid=None):
    """adds to or creates a new embeddor set"""
    print('Adding embeddors: ' + str(embeddor_uuids))
    if set_uuid:
        uuid = algo.add_to_algorithm_set(lookup.embeddor, set_uuid, embeddor_uuids)
        message = 'The UUID of the set you have added to is: '
    else:
        uuid = algo.create_algorithm_set(lookup.embeddor, embeddor_uuids)
        message = 'The new UUID of the set you have created is: '

    print('Added embeddor successfully')
    print(message + uuid)

    return uuid


def add_detector(detector_uuids, set_uuid=None):
    """adds to or creates a new detector set"""
    print('Adding detectors: ' + str(detector_uuids))
    if set_uuid:
        uuid = algo.add_to_algorithm_set(lookup.detector, set_uuid, detector_uuids)
        message = 'The UUID of the set you have added to is: '
    else:
        uuid = algo.create_algorithm_set(lookup.detector, detector_uuids)
        message = 'The new UUID of the set you have created is: '

    print('Added detector successfully')
    print(message + uuid)

    return uuid


def info(all=False, database=False, embeddor=False, detector=False):
    """provides system info"""
    breaker = ['-' for i in range(100)]
    breaker = ''.join(breaker)
    print('Listing all requested information....')
    print(breaker)

    if all or database:
        print(breaker)
        print('All database information')
        print(breaker)
        print(breaker)

        db_info = lookup.get_all_dbs()
        source_db = list(filter(lambda d: len(d.keys()) == len(lookup.db_header), db_info))
        steganographic_db = list(
            filter(
                lambda d: len(
                    d.keys()) == len(
                    lookup.steganographic_header),
                db_info))

        print('Source Databases processed: (' + str(len(source_db)) + ')')
        for db in source_db:
            print('\t' + str(db[lookup.db_descriptor]))
            print('\t\t' + 'UUID: ' + str(db[lookup.uuid_descriptor]))
            print('\t\t' + 'Directory path: ' + str(db[lookup.path_descriptor]))
            print('\t\t' + 'Image Count: ' + str(db[lookup.db_image_count]))
            print('\t\t' + 'Image Types: ' + str(db[lookup.compatible_descriptor]))
        print(breaker)

        print('Steganographic Databases processed: (' + str(len(steganographic_db)) + ')')
        for db in steganographic_db:
            print('\t' + str(db[lookup.db_descriptor]))
            print('\t\t' + 'UUID: ' + str(db[lookup.uuid_descriptor]))
            print('\t\t' + 'Directory path: ' + str(db[lookup.path_descriptor]))
            print('\t\t' + 'Image Count: ' + str(db[lookup.db_image_count]))
            print('\t\t' + 'Image Types: ' + str(db[lookup.compatible_descriptor]))
            print('\t\t' + 'Source DB: ' + str(db[lookup.source_db]))
            print('\t\t' + 'Source Embeddor Set: ' + str(db[lookup.source_embeddor_set]))
            print('\t\t' + 'Payload: ' + str(db[lookup.embedding_ratio]))
        print(breaker)

    if all or embeddor:
        print(breaker)
        print('All embeddor information')
        print(breaker)
        print(breaker)
        embeddor_info = algo.get_all_algorithms(lookup.embeddor)
        print('Embeddors available: (' + str(len(embeddor_info)) + ')')
        for embeddor in embeddor_info:
            print('\t' + str(embeddor[lookup.name_descriptor]))
            print('\t\t' + 'UUID: ' + str(embeddor[lookup.uuid_descriptor]))
            print('\t\t' + 'Compatible Types: ' + str(embeddor[lookup.compatible_descriptor]))
            print('\t\t' + 'Maximum Embedding Ratio: ' +
                  str(embeddor[lookup.embedding_descriptor]))
            print('\t\t' + 'Command Type: ' + str(embeddor[lookup.COMMAND_TYPE]))
        print(breaker)

        embeddor_set_info = algo.get_all_algorithm_sets(lookup.embeddor)
        print('Embeddor sets available: (' + str(len(embeddor_set_info)) + ')')
        for embeddor_set in embeddor_set_info:
            print('\tUUID: ' + embeddor_set[lookup.uuid_descriptor])
            print('\t\t' + 'Compatible Types: ' + str(embeddor_set[lookup.compatible_descriptor]))
            print('\t\t' + 'Maximum Embedding Ratio: ' +
                  str(embeddor_set[lookup.embedding_descriptor]))
            print('\t\t' + 'Embeddors: ' + str(len(embeddor_set[lookup.embeddor])))
            for embeddor in embeddor_set[lookup.embeddor]:
                print('\t\t\t' +
                      '(' +
                      embeddor[lookup.name_descriptor] +
                      ', ' +
                      embeddor[lookup.uuid_descriptor] +
                      ')')
        print(breaker)

    if all or detector:
        print(breaker)
        print('All detector information')
        print(breaker)
        print(breaker)
        detector_info = algo.get_all_algorithms(lookup.detector)
        binary_detectors = list(
            filter(lambda d: d[lookup.DETECTOR_TYPE] == lookup.binary_detector, detector_info))
        probability_detectors = list(
            filter(lambda d: d[lookup.DETECTOR_TYPE] == lookup.probability_detector, detector_info))

        print('Binary Detectors available: (' + str(len(binary_detectors)) + ')')
        for detector in binary_detectors:
            print('\t' + str(detector[lookup.name_descriptor]))
            print('\t\t' + 'UUID: ' + str(detector[lookup.uuid_descriptor]))
            print('\t\t' + 'Compatible Types: ' + str(detector[lookup.compatible_descriptor]))
            print('\t\t' + 'Command Type: ' + str(detector[lookup.COMMAND_TYPE]))
        print(breaker)

        print('Probability Detectors available: (' + str(len(probability_detectors)) + ')')
        for detector in probability_detectors:
            print('\t' + str(detector[lookup.name_descriptor]))
            print('\t\t' + 'UUID: ' + str(detector[lookup.uuid_descriptor]))
            print('\t\t' + 'Compatible Types: ' + str(detector[lookup.compatible_descriptor]))
            print('\t\t' + 'Command Type: ' + str(detector[lookup.COMMAND_TYPE]))
        print(breaker)

        detector_set_info = algo.get_all_algorithm_sets(lookup.detector)
        print('Detector sets available: (' + str(len(detector_set_info)) + ')')
        for detector_set in detector_set_info:
            print('\tUUID: ' + detector_set[lookup.uuid_descriptor])
            print('\t\t' + 'Compatible Types: ' + str(detector_set[lookup.compatible_descriptor]))
            print('\t\t' + 'Detectors: ' + str(len(detector_set[lookup.detector])))
            for detector in detector_set[lookup.detector]:
                print('\t\t\t' +
                      '(' +
                      detector[lookup.name_descriptor] +
                      ', ' +
                      detector[lookup.uuid_descriptor] +
                      ')')
        print(breaker)

    print(breaker)
    print('All information printed.')


def embed(embeddor_set_uuid, database_uuid, ratio, name):
    """Embeds a db using embeddors and db images"""
    embeddor_set = algo.get_algorithm_set(lookup.embeddor, embeddor_set_uuid)
    generator = Embeddor(embeddor_set)
    db_uuid = generator.embed_ratio(name, database_uuid, ratio)
    print('The UUID of the dataset you have created is: ' + db_uuid)
    return db_uuid


def detect(detector_set_uuid, database_uuids):
    """analyzes a set detectors using a pre-processed database"""
    detector_set = algo.get_algorithm_set(lookup.detector, detector_set_uuid)
    analyzer = Detector(detector_set)
    results = analyzer.detect(database_uuids)

    breaker = ['-' for i in range(100)]
    breaker = ''.join(breaker)
    small_breaker = ['-' for i in range(75)]
    small_breaker = ''.join(breaker)

    print('Experiment information')
    print(breaker)
    print(breaker)
    for db in database_uuids:
        db_info = lookup.get_db_info(db)

        if db_info[lookup.stego]:
            print('Database Information')
            print('\t' + 'UUID: ' + str(db_info[lookup.uuid_descriptor]))
            print('\t\t' + 'Source DB: ' + str(db_info[lookup.source_db]))
            print('\t\t' + 'Source Embeddor Set: ' + str(db_info[lookup.source_embeddor_set]))
            print('\t\t' + 'Image Types: ' + str(db_info[lookup.compatible_descriptor]))
            print('\t\t' + 'Payload: ' + str(db_info[lookup.embedding_ratio]))
            print(breaker)

            print('Embeddor Set Information')
            embeddor_set = algo.get_algorithm_set(
                lookup.embeddor, str(db_info[lookup.source_embeddor_set]))
            print('\tUUID: ' + embeddor_set[lookup.uuid_descriptor])
            print('\t\t' + 'Compatible Types: ' + str(embeddor_set[lookup.compatible_descriptor]))
            print('\t\t' + 'Embeddors: ' + str(len(embeddor_set[lookup.embeddor])))
            for embeddor in embeddor_set[lookup.embeddor]:
                print('\t\t\t' +
                      '(' +
                      embeddor[lookup.name_descriptor] +
                      ', ' +
                      embeddor[lookup.uuid_descriptor] +
                      ')')
            print(breaker)
        else:
            print('Database Information')
            print('\t' + 'UUID: ' + str(db_info[lookup.uuid_descriptor]))
            print('\t\t' + 'Image Types: ' + str(db_info[lookup.compatible_descriptor]))
            print(breaker)

    print(breaker)
    print('Listing all results...')
    print(breaker)

    for detector_uuid in results:
        detector_info = algo.get_algorithm_info(lookup.detector, detector_uuid)
        print('\tName: ' + detector_info[lookup.name_descriptor])
        print('\tDetector Type: ' + detector_info[lookup.DETECTOR_TYPE])
        print('\tUUID: ' + detector_uuid)
        detector_result = results[detector_uuid]

        if detector_info[lookup.DETECTOR_TYPE] == lookup.binary_detector:
            raw_results = detector_result[lookup.result_raw]
            true_positive = raw_results[lookup.true_positive_raw]
            true_negative = raw_results[lookup.true_negative_raw]
            total_stego = raw_results[lookup.total_stego_raw]
            total_cover = raw_results[lookup.total_cover_raw]

            print('\tRaw Results:')
            print(
                '\t\t(' +
                str(true_positive) +
                '/' +
                str(total_stego) +
                ') stego images identified correctly')
            print(
                '\t\t(' +
                str(true_negative) +
                '/' +
                str(total_cover) +
                ') cover images identified correctly')
            print('\t\t(' + str(true_positive + true_negative) + '/' +
                  str(total_stego + total_cover) + ') total images identified correctly')

        print('\tMetrics:')

        metric_results = detector_result[lookup.result_metric]
        for metric in metric_results:
            print('\t\t' + metric + ': ' + str(metric_results[metric]))

        print(small_breaker)

    print(breaker)
    print('All results printed.')


def verify(stego_database_uuid):
    """verifies a steganographic database"""
    verifier = Verifier()
    results = verifier.verify(stego_database_uuid)

    verified_total = 0
    error_total = 0

    breaker = ['-' for i in range(100)]
    breaker = ''.join(breaker)
    print('Listing all verification results...')
    print(breaker)
    print('Specific Embeddor Results')
    for embeddor_uuid in results:
        embeddor_result = results[embeddor_uuid]
        embeddor_info = algo.get_algorithm_info(lookup.embeddor, embeddor_uuid)
        print('\tName: ' + embeddor_info[lookup.name_descriptor])
        print('\tUUID: ' + embeddor_uuid)

        verified = len(list(filter(lambda r: r[lookup.result], embeddor_result)))
        errors = len(list(filter(lambda r: not r[lookup.result], embeddor_result)))

        print('\t\tCorrectly Embedded (%): ' + str(100 * (float(verified) / float(verified + errors))))
        print('\t\tIncorrect Embedding (%): ' + str(100 * (float(errors) / float(verified + errors))))

        verified_total += verified
        error_total += errors

    print(breaker)
    print('Total Results')
    print('\tCorrectly Embedded (%): ' +
          str(100 * (float(verified_total) / float(verified_total + error_total))))
    print('\tIncorrect Embedding (%): ' +
          str(100 * (float(error_total) / float(verified_total + error_total))))


def run_experiment(path, database):
    """runs pipelines specified in experiment configuration file"""
    metadata, embeddor_set_uuid, detector_set_uuid = algo_processor.process_experiment_file(path)
    scheduler = Scheduler(metadata, embeddor_set_uuid, detector_set_uuid)
    results = scheduler.run(database)
    print(results)


def adv_attack(model, database, configurations):
    """performs an adversarial attack on a predefined model with specific configuration details"""
    assert(fs.file_exists(model))
    data = [pr.load_data_as_array(db) for db in database]
    x, y = [], []
    for db in data:
        for (x_t, y_t) in db:
            x.append(x_t)
            y.append(y_t)

    dataset = (x, y)
    db_uuid = robust.apply_attack(model, dataset, configurations)
    print('The UUID of the dataset you have created is: ' + db_uuid)


def generate_labels(database_uuids, output_csv_file, relative=False):
    """generates labels.csv file for a set of databases"""
    db_image_list = [('cover', 'steganographic')]
    label_file_directory = abspath(lookup.get_top_level_dirs()[lookup.db])
    path_to_label_file = join(label_file_directory, output_csv_file)
    for db in database_uuids:
        db_image_dict = lookup.get_image_list(db)
        if relative:
            db_image_list = db_image_list + list(map(lambda img: (relpath(img[lookup.source_image], label_file_directory), relpath(
                img[lookup.file_path], label_file_directory)), db_image_dict))
        else:
            db_image_list = db_image_list + \
                list(map(lambda img: (img[lookup.source_image],
                     img[lookup.file_path]), db_image_dict))

    fs.write_to_csv_file(path_to_label_file, db_image_list)
    print('The labels file can be found here: ' + path_to_label_file)
