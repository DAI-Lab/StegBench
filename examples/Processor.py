
import sys
from os import path
from os.path import abspath, join
import stegtest.utils.filesystem as fs

class Processor(object):
	"""docstring for Processor"""
	def process_csv_file(input_file, result_file):
		raise NotImplementedError

	def process_txt_file(input_file, result_file):
		raise NotImplementedError

	def process_file(input_file, result_file):
		file_extension = fs.get_extension(input_file)
		processing_function = {
			'csv': self.process_csv_file,
			'txt': self.process_txt_file,
		}[file_extension]

		assert(fs.file_exists(file))
		processing_function(input_file, result_file)

if __name__ == "__main__":
	args = sys.argv[1:]

	assert(len(args) == 2)
	input_file = args[0]
	result_file = args[1]

	processor = Processor()
	processor.process_file(input_file, result_file)




		