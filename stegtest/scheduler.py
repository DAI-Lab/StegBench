import os
import shutil

import stegtest.utils.filesystem as fs
import stegtest.utils.lookup as lookup

from stegtest.types.pipeline import Pipeline 

#code way to do it.

class Scheduler(Pipeline):

	def __init__(self, embeddors, detectors):
		self.embeddors = embeddors
		self.detectors = detectors
		for embeddor in embeddors:
			continue
		#	<gets you class> lookup_emnbeddor()

		for detector in detectors:
			continue
		#   <gets you info> lookup_detect()

	@staticmethod
	def _initializeFS(directory):
		"""Clears and adds needed directories for stegdetect to work"""
		print('initializing fs at ' + directory)
		try:
			os.chdir(directory)
		except:
			raise OSError('directory: ' + directory + ' is not a valid directory. Please initialize with a valid directory')

		print('cleaning fs...')
		
		top_level_directories = lookup.get_top_level_directories().values()
		fs.clean_filesystem(top_level_directories)

		print('initializing directories...')

		directories = lookup.all_directories()

		for directory in directories:
			fs.make_dirs(directory)

		print('initializing files...')
		master_files = lookup.get_master_files()
		for file_type in master_files.keys():
			path_to_master_file = master_files[file_type]
			master_file_header = lookup.get_master_header(file_type)

			fs.write_to_csv_file(path_to_master_file, [master_file_header])

	def _loadDB(self, ):
		raise NotImplementedError
		#load the list of files from this hash

		# self.file_list = generate_file_list(db_hash)

	def _generateTestDB(self, ): #Scheduler initialized with embeddors
		raise NotImplementedError
		# uses embeddors to generate the test files
		# produces a db hash with a file list

	def _test(self, ):
		raise NotImplementedError

	def _train(self, ):
		raise NotImplementedError
