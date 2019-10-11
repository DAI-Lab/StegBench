import urllib.request as req
import shutil
import zipfile
import stegtest.utils.filesystem as fs

BOSS_URL = 'http://dde.binghamton.edu/download/ImageDB/BOSSbase_1.01.zip'
BOWS2_URL = 'http://bows2.ec-lille.fr/BOWS2OrigEp3.tgz'


def retrieve_zip_file(url, path_to_zip_file):
	"""retrieves a zip file from a specified url and saves it to path_to_zip_file"""
	print('Downloading from: ' + url + ' to: ' + path_to_zip_file)
	with req.urlopen(url) as response, open(path_to_zip_file, 'wb') as out_file:
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

def download_from_BOSS(temp_directory):
	zip_file_name = 'BOSS.zip'
	unzip_directory = 'BOSSbase_1.01'
	path_to_zip_file = temp_directory + '/' + zip_file_name
	path_to_unzip_directory = temp_directory + '/' + unzip_directory
	
	retrieve_zip_file(BOSS_URL, path_to_zip_file)
	unzip_file(path_to_zip_file, temp_directory)

	assert(fs.dir_exists(path_to_unzip_directory))

	return path_to_unzip_directory

def download_from_BOWS2(dir):
	retrieve_zip_file

def download_from_BURST(dir):
	raise NotImplementedError

def download_from_COCO(dir, params):
	raise NotImplementedError

def download_from_DRESDEN(dir, params):
	raise NotImplementedError

def download_from_RAISE(dir):
	raise NotImplementedError

def download_from_ImageNet(dir, params):
	raise NotImplementedError
