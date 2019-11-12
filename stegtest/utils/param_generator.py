import stegtest.utils.lookup as lookup
import random
import string

def generate_random_string(byte_length=20):
	return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(byte_length))

def generate_random_float(max_flt=100):
	return random.random()*max_flt

def generate_random_int(max_int=100):
	return int(generate_random_float(max_int))

def generate_param(type, *args):
	function = {
		lookup.SECRET_TXT_PLAINTEXT: generate_random_string, 
		lookup.SECRET_TXT_FILE: generate_random_string,
		lookup.PASSWORD: generate_password,
		lookup.BPP: generate_random_float,
		lookup.bpnzAC: generate_random_float
	}[type]
	return function(*args)

def secret_message_from_embedding(embedding_ratio, img_info):
	str_len_in_bits = float(img_info[lookup.embedding_max])*embedding_ratio
	strlen_in_bytes = int(str_len_in_bits/8)
	return generate_random_string(strlen_in_bytes)

def generate_password(byte_length=20):
	return generate_random_string(byte_length)
