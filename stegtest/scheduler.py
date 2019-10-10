import os
import shutil

import stegtest.utils.filesystem as fs
import stegtest.utils.bindings as bd

from stegtest.types.pipeline import Pipeline 
# from stegtest.utils.filesystem import generate_file_list, makedirs
# from stegtest.utils.bindings import lookup_embeddor, lookup_detector

#code way to do it.

class Scheduler(Pipeline):

	def __init__(self, embeddors, detectors):
		self.embeddors = []
		self.detectors = []
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
		fs.clean_filesystem()

		directories = bd.get_directories()
		print('initializing directories...')

		for directory in directories:
			fs.makedirs(directory)

		print('initializing files...')
		master_files = bd.get_master_files().values()
		for file in master_files:
			fs.makefile(file)

	def _loadDB(self, db_hash):
		self.db_hash = db_hash
		#load the list of files from this hash

		# self.file_list = generate_file_list(db_hash)

	def _generateTestDB(self, noice):
		pass
		# uses embeddors to generate the test files
		# produces a db hash with a file list

	def _test(self, noice):
		pass

