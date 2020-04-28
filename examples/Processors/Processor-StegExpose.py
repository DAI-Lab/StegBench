
import sys
from os import path
from os.path import abspath, join
import stegbench.utils.filesystem as fs

class Processor(object):
	"""docstring for Processor"""
	def process_csv_file(self, input_file, result_file, probability=False):
		data = fs.read_csv_file(input_file)

		data = data[2:]
		data_to_write = []
		for row in data:
			file_name = row[0]

			if probability:
				result = float(row[len(row) - 1])
			else:
				stego = row[1]
				if stego == 'true':
					result = True
				else:
					result = False

			data_to_write.append([file_name, result])

		fs.write_to_csv_file(result_file, data_to_write)

if __name__ == "__main__":
	args = sys.argv[1:]

	processor = Processor()
	input_file = args[0]
	result_file = args[1]
	if len(args) > 2:
		processor.process_csv_file(input_file, result_file, True)
	else:
		processor.process_csv_file(input_file, result_file)


