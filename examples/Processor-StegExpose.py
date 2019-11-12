
import sys
from os import path
from os.path import abspath, join
import stegtest.utils.filesystem as fs

class Processor(object):
	"""docstring for Processor"""
	def process_csv_file(self, input_file, result_file):
		data = fs.read_csv_file(input_file)

		data = data[2:]
		data_to_write = []
		for row in data:
			file_name = row[0]

			stego = row[1]

			if stego == 'true':
				result = True
			else:
				result = False

			data_to_write.append([file_name, result])

		fs.write_to_csv_file(result_file, data_to_write)

	def process_txt_file(self, input_file, result_file):
		raise NotImplementedError

	def process_file(self, input_file, result_file):
		file_extension = fs.get_extension(input_file)
		processing_function = {
			'.csv': self.process_csv_file,
			'.txt': self.process_txt_file,
		}[file_extension]

		assert(fs.file_exists(input_file))
		processing_function(input_file, result_file)

if __name__ == "__main__":
	args = sys.argv[1:]

	assert(len(args) == 2)
	input_file = args[0]
	result_file = args[1]

	processor = Processor()
	processor.process_file(input_file, result_file)


