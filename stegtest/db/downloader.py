import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs
import stegtest.db.processor as processor

import urllib.request as req
import shutil
import zipfile

from os.path import join

BOSS_URL = 'http://dde.binghamton.edu/download/ImageDB/BOSSbase_1.01.zip'
BOWS2_URL = 'http://bows2.ec-lille.fr/BOWS2OrigEp3.tgz'
COCO_URL = 'http://images.cocodataset.org/zips/test2017.zip'
DIV2K_URL = 'http://data.vision.ee.ethz.ch/cvl/DIV2K/DIV2K_valid_HR.zip'

def get_download_routines():
	return { 
		'BOSS': download_from_BOSS, 
		'BOWS2': download_from_BOWS2, 
		'BURST': download_from_BURST, 
		'COCO': download_from_COCO, 
		'DRESDEN': download_from_DRESDEN, 
		'DIV2K': download_from_DIV2K,
		'RAISE': download_from_RAISE, 
		'ImageNet': download_from_ImageNet
	}

def download_routine(name):
	"""downloads using a specified routing"""
	db_routines = get_download_routines() 
	assert(name in db_routines.keys())
	dataset_folder = lookup.get_db_dirs()[lookup.dataset]
	
	download_directory = db_routines[name](dataset_folder)
	return download_directory
	
def retrieve_file(url, path_to_file):
	"""retrieves a zip file from a specified url and saves it to path_to_zip_file"""
	print('Downloading from: ' + url + ' to: ' + path_to_file)
	with req.urlopen(url) as response, open(path_to_file, 'wb') as out_file:
		shutil.copyfileobj(response, out_file)
	print('Download complete...')

def unzip_file(path_to_zip_file, target_directory):
	"""unzips a file and saves it to the target directory. also removes the zip file once unzipped"""
	assert(path_to_zip_file.endswith('.zip'))
	print('Unzipping contents...')
	print(path_to_zip_file)
	with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
		zip_ref.extractall(target_directory)

	fs.remove_file(path_to_zip_file)

def download_from_BOSS(directory):
	zip_file_name = 'BOSS.zip'
	unzip_directory = 'BOSSbase_1.01'
	path_to_zip_file = join(directory, zip_file_name)
	path_to_unzip_directory = join(directory, unzip_directory)
	
	retrieve_file(BOSS_URL, path_to_zip_file)
	unzip_file(path_to_zip_file, directory)

	assert(fs.dir_exists(path_to_unzip_directory))

	return path_to_unzip_directory

def download_from_BOWS2(directory):
	zip_file_name = 'BOWS2.zip'
	unzip_directory = 'BOWS2OrigEp3'
	path_to_zip_file = join(directory, zip_file_name)
	path_to_unzip_directory = join(directory, unzip_directory)
	
	retrieve_file(BOWS2_URL, path_to_zip_file)
	unzip_file(path_to_zip_file, directory)

	assert(fs.dir_exists(path_to_unzip_directory))

	return path_to_unzip_directory

def download_from_BURST(directory):
	raise NotImplementedError

def download_from_COCO(directory):
	zip_file_name = 'test2017.zip'
	unzip_directory = 'test2017'
	path_to_zip_file = join(directory, zip_file_name)
	path_to_unzip_directory = join(directory, unzip_directory)
	
	retrieve_file(COCO_URL, path_to_zip_file)
	unzip_file(path_to_zip_file, directory)

	assert(fs.dir_exists(path_to_unzip_directory))

	return path_to_unzip_directory

def download_from_DRESDEN(directory):
	raise NotImplementedError

def download_from_DIV2K(directory):
	zip_file_name = 'DIV2K_valid_HR.zip'
	unzip_directory = 'DIV2K_valid_HR'

	path_to_zip_file = join(directory, zip_file_name)
	path_to_unzip_directory = join(directory, unzip_directory)
	
	retrieve_file(DIV2K_URL, path_to_zip_file)
	unzip_file(path_to_zip_file, directory)

	assert(fs.dir_exists(path_to_unzip_directory))

	return path_to_unzip_directory

def download_from_RAISE(directory):
	raise NotImplementedError

def download_from_ImageNet(directory):
	raise NotImplementedError
