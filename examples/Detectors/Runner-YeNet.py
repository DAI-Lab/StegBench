import sys
from os import path
from os.path import abspath, join
import stegtest.utils.filesystem as fs
from stegdetect import StegDetect

class Runner(object):
	"""docstring for Runner"""
	def detect(self, input_file, output_file):
		stegdetect = StegDetect.load()
		result = stegdetect.detect(input_file, probability=True)
		fs.write_to_text_file(output_file, [result[1]], override=True)

if __name__ == "__main__":
	args = sys.argv[1:]

	assert(len(args) == 2)
	input_file = args[0]
	output_file = args[1]

	runner = Runner()
	runner.detect(input_file, output_file)