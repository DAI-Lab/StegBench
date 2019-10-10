
from stegtest.types.pipeline import Pipeline 
from stegtest.utils.filesystem import generate_file_list
from stegtest.utils.bindings import lookup_embeddor, lookup_detector

class Scheduler(Pipeline):


	self.embeddors = []
	self.detectors = []

	def __init__(self, embeddors, detectors):
		for embeddor in embeddors:
		#	<gets you class> lookup_emnbeddor()

		for detector in detectors:
		#   <gets you info> lookup_detect()


	def _loadDB(self, db_hash):
		self.db_hash = db_hash
		#load the list of files from this hash

		self.file_list = generate_file_list(db_hash)

	def _generateTestDB(self, ):
		# uses embeddors to generate the test files
		# produces a db hash with a file list

	def _test(self, ):
		pass