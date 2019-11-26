import imghdr
import collections
import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs
from jpeg2dct.numpy import load
from skimage.util import random_noise, img_as_ubyte, img_as_float
import numpy as np

from PIL import Image, ExifTags
Image.MAX_IMAGE_PIXELS = None

def convert_channels_to_int(channel:str):
	"""
		1 (1-bit pixels, black and white, stored with one pixel per byte)
		L (8-bit pixels, black and white)
		P (8-bit pixels, mapped to any other mode using a color palette)
		RGB (3x8-bit pixels, true color)
		RGBA (4x8-bit pixels, true color with transparency mask)
		CMYK (4x8-bit pixels, color separation)
		YCbCr (3x8-bit pixels, color video format)
		Note that this refers to the JPEG, and not the ITU-R BT.2020, standard
		LAB (3x8-bit pixels, the L*a*b color space)
		HSV (3x8-bit pixels, Hue, Saturation, Value color space)
		I (32-bit signed integer pixels)
		F (32-bit floating point pixels)
	"""
	return {
		'L': 1,
		'P': 1,
		'RGB': 3,
		'RGBA': 4,
		'CMYK': 4,
		'YCbCr': 3,
		'LAB': 3,
		'HSV': 3,
	}[channel]

def convert_to_png(path_to_input, path_to_output):
	img = Image.open(path_to_input)
	path_to_output = fs.change_extension(path_to_output, 'png')
	img.save(path_to_output, format='PNG')
	img.close()

	return path_to_output

def convert_to_jpeg(path_to_input, path_to_output, quality_level):
	assert(quality_level >= 1 and quality_level <= 95)
	img = Image.open(path_to_input)
	path_to_output = fs.change_extension(path_to_output, 'jpg')
	img.save(path_to_output, format='JPEG', quality=quality_level)
	img.close()

	return path_to_output

def add_noise_to_image(path_to_input, path_to_output, mean, var):
	"""adds noise to an image with additditive gaussian noise"""
	pix = np.array(Image.open(path_to_input))
	pix = img_as_ubyte(random_noise(img_as_float(pix), mode='gaussian', seed=None, clip=True, mean=mean, var=var))
	pix = np.array(pix)
	img = Image.fromarray(pix)
	img.save(path_to_output)
	img.close()
	return path_to_output

def center_crop(path_to_input, path_to_output, width, height):
	"""crops an image to specified dimensions"""
	img = Image.open(path_to_input)
	current_width, current_height = img.size
	if current_width < width:
		width = current_width
	if current_height < height:
		height = current_height

	cropped_img = img.crop(((current_width-width)//2, (current_height-height)//2, (current_width+width)//2, (current_height+height)//2))
	cropped_img.save(path_to_output)
	img.close()
	cropped_img.close()

	return path_to_output

def resize_image(path_to_input, path_to_output, width, height):
	"""resizes an image to the specified dimensions"""
	img = Image.open(path_to_input)

	cropped_img = img.resize((width, height))
	cropped_img.save(path_to_output)

	img.close()
	cropped_img.close()

	return path_to_output

def rgb2gray(path_to_input, path_to_output):
	# Here we use the good old standard ITU-R Recommendation BT.601 (rec601) for computing luminance: 
	img = Image.open(path_to_input).convert('L')
	img.save(path_to_output)
	img.close()
	return path_to_output

def rotate_image(path_to_input, path_to_output, degrees):
	"""rotates image by specified degrees"""
	img = Image.open(path_to_input)

	cropped_img = img.rotate(degrees)
	cropped_img.save(path_to_output)

	img.close()
	cropped_img.close()

	return path_to_output

def get_operation_args(operation):
	args = {
		lookup.add_noise: collections.OrderedDict({'mean': float, 'var': float}),
		lookup.center_crop: collections.OrderedDict({'width': int, 'height': int}),
		lookup.convert_to_jpeg: collections.OrderedDict({'quality_level': int}),
		lookup.convert_to_png: collections.OrderedDict(),
		lookup.resize: collections.OrderedDict({'width': int, 'height': int}),
		lookup.rotate: collections.OrderedDict({'degrees': float}),
		lookup.rgb2gray: collections.OrderedDict(),
	}[operation]

	return args

def apply_operation(operation, args, partition):
	function = {
		lookup.add_noise: add_noise_to_image,
		lookup.center_crop: center_crop,
		lookup.convert_to_png: convert_to_png,
		lookup.convert_to_jpeg: convert_to_jpeg,
		lookup.resize: resize_image,
		lookup.rgb2gray: rgb2gray,
		lookup.rotate: rotate_image,
	}[operation]

	path_to_output = function(partition[lookup.input_file_header], partition[lookup.output_file_header], *args)
	return path_to_output

def get_image_type(path_to_file):
	ext = fs.get_extension(path_to_file)[1:]
	return ext

def is_image_file(path_to_file):
	return get_image_type(path_to_file) in lookup.all_supported_types()

def process_coefficient(coefficients):
	y_nz = np.count_nonzero(coefficients[0])
	y_nz_dc = np.count_nonzero(coefficients[0][:,:,0])

	ac_dct_y = y_nz - y_nz_dc
	ac_dct_all = 0

	for coefficient in coefficients:
		ac_dct_all += np.count_nonzero(coefficient) - np.count_nonzero(coefficient[:,:,0])

	return ac_dct_y, ac_dct_all

def get_image_info(path_to_file):
	"""Returns image info as a dictionary with elements, type, width, height, channels"""
	assert(fs.file_exists(path_to_file))
	img_type = get_image_type(path_to_file)
	im = Image.open(path_to_file)
	width, height = im.size
	channels = im.mode

	info_dict = collections.OrderedDict()
	info_dict[lookup.file_path] = path_to_file 
	info_dict[lookup.image_type] = img_type 
	info_dict[lookup.image_width] = width
	info_dict[lookup.image_height] = height
	info_dict[lookup.image_channels] = channels

	if img_type in lookup.lossy_encoding_types():
		coefficients = np.array(load(path_to_file))

		ac_dct_y, ac_dct_all = process_coefficient(coefficients)
		info_dict[lookup.embedding_max] = ac_dct_y
	else:
		info_dict[lookup.embedding_max] = width*height*convert_channels_to_int(channels)

	return info_dict
