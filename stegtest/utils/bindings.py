# import * from stegtest as st


# def get_binding(name_of_method, type):
# 	
def lookup_table(type):
     return {
        'embeddor': 'embeddor/master.csv'
        'detector': 'detector/detector.csv',
        'db': None,
    }[type]

def lookup_embeddor(name_of_method):
	raise NotImplementedError

def lookup_detector(name_of_method):
	raise NotImplementedError