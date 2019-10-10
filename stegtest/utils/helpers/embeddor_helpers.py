
# from stegtest.utils.bindings import get_embeddor_binding
import csv

def add_embeddor_to_file(file, options):
	assert(len(options) == 2)

	with open(file,'wb') as out:
	    csv_out=csv.writer(out)
	    for row in options:
	    	csv_out.writerow(row)