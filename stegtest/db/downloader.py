import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs
import stegtest.db.processor as processor

import urllib.request as req
import shutil
import zipfile

from os.path import join

BOSS_URL = 'http://dde.binghamton.edu/download/ImageDB/BOSSbase_1.01.zip'
BOWS2_URL = 'http://bows2.ec-lille.fr/BOWS2OrigEp3.tgz'
COCO_TEST_URL = 'http://images.cocodataset.org/zips/test2017.zip'
COCO_TRAIN_URL = 'http://images.cocodataset.org/zips/train2017.zip'
DIV2K_VALID_URL = 'http://data.vision.ee.ethz.ch/cvl/DIV2K/DIV2K_valid_HR.zip'
DIV2K_TRAIN_URL = 'http://data.vision.ee.ethz.ch/cvl/DIV2K/DIV2K_train_HR.zip'
BURST_URL = 'http://dde.binghamton.edu/download/ImageDB/BURST_sorted.zip'
ALASKA_URL = 'http://alaska.utt.fr/alaska1ALASKA_training_set_jpg1_cover.zip'

def get_download_routines():
	return { 
		'ALASKA': download_from_ALASKA,
		'BOSS': download_from_BOSS, 
		'BOWS2': download_from_BOWS2, 
		'COCO_Test': download_from_COCO_TEST, 
		'COCO_Train': download_from_COCO_TRAIN, 
		'DRESDEN': download_from_DRESDEN, 
		'DIV2K_VALID': download_from_DIV2K_VALID,
		'DIV2K_TRAIN': download_from_DIV2K_TRAIN,
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

def download_from_ALASKA(directory):
	zip_file_name = 'ALASKA_training_set_jpg1_cover.zip'
	unzip_directory = 'alaska1ALASKA_training_set_jpg1_cover.zip'
	path_to_zip_file = join(directory, zip_file_name)
	path_to_unzip_directory = join(directory, unzip_directory)
	
	retrieve_file(ALASKA_URL, path_to_zip_file)
	unzip_file(path_to_zip_file, directory)

	assert(fs.dir_exists(path_to_unzip_directory))

	return path_to_unzip_directory

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

def download_from_COCO_TEST(directory):
	zip_file_name = 'test2017.zip'
	unzip_directory = 'test2017'
	path_to_zip_file = join(directory, zip_file_name)
	path_to_unzip_directory = join(directory, unzip_directory)
	
	retrieve_file(COCO_TEST_URL, path_to_zip_file)
	unzip_file(path_to_zip_file, directory)

	assert(fs.dir_exists(path_to_unzip_directory))

	return path_to_unzip_directory

def download_from_COCO_TRAIN(directory):
	zip_file_name = 'train2017.zip'
	unzip_directory = 'train2017'
	path_to_zip_file = join(directory, zip_file_name)
	path_to_unzip_directory = join(directory, unzip_directory)
	
	retrieve_file(COCO_TRAIN_URL, path_to_zip_file)
	unzip_file(path_to_zip_file, directory)

	assert(fs.dir_exists(path_to_unzip_directory))

	return path_to_unzip_directory

def download_from_DRESDEN(directory):
	#does not exist at the moment and would need to read a txt file to get the files 
	raise NotImplementedError

def download_from_DIV2K_VALID(directory):
	zip_file_name = 'DIV2K_valid_HR.zip'
	unzip_directory = 'DIV2K_valid_HR'

	path_to_zip_file = join(directory, zip_file_name)
	path_to_unzip_directory = join(directory, unzip_directory)
	
	retrieve_file(DIV2K_VALID_URL, path_to_zip_file)
	unzip_file(path_to_zip_file, directory)

	assert(fs.dir_exists(path_to_unzip_directory))

	return path_to_unzip_directory

def download_from_DIV2K_TRAIN(directory):
	zip_file_name = 'DIV2K_train_HR.zip'
	unzip_directory = 'DIV2K_train_HR'

	path_to_zip_file = join(directory, zip_file_name)
	path_to_unzip_directory = join(directory, unzip_directory)
	
	retrieve_file(DIV2K_TRAIN_URL, path_to_zip_file)
	unzip_file(path_to_zip_file, directory)

	assert(fs.dir_exists(path_to_unzip_directory))

	return path_to_unzip_directory

def download_from_RAISE(directory):
	#does not exist and would need to read a csv file to get the files
	raise NotImplementedError

def download_from_ImageNet(directory):
	#need to use some sort of utility to get this running
	raise NotImplementedError
