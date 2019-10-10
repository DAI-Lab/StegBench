
# from stegtest.utils.bindings import get_embeddor_binding
import csv

def add_embeddor_to_file(file, options):
	assert(len(options) == 2)

	with open(file,'wb') as out:
	    csv_out=csv.writer(out)
	    csv_out.writerow(['embeddor','weight'])
	    csv_out.writerow(options)
