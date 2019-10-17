import imghdr
import collections
import stegtest.utils.lookup as lookup

from PIL import Image, ExifTags
Image.MAX_IMAGE_PIXELS = None

# 1 (1-bit pixels, black and white, stored with one pixel per byte)
# L (8-bit pixels, black and white)
# P (8-bit pixels, mapped to any other mode using a color palette)
# RGB (3x8-bit pixels, true color)
# RGBA (4x8-bit pixels, true color with transparency mask)
# CMYK (4x8-bit pixels, color separation)
# YCbCr (3x8-bit pixels, color video format)
# Note that this refers to the JPEG, and not the ITU-R BT.2020, standard
# LAB (3x8-bit pixels, the L*a*b color space)
# HSV (3x8-bit pixels, Hue, Saturation, Value color space)
# I (32-bit signed integer pixels)
# F (32-bit floating point pixels)


def get_image_type(path_to_file):
	return imghdr.what(path_to_file)

def is_image_file(path_to_file):
	return get_image_type(path_to_file) is not None

def get_image_info(path_to_file):
	"""Returns image info as a dictionary with elements, type, width, height, channels"""
	#assert(file_exists()) TODO
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

	print(info_dict)

	return info_dict

def get_exif_info(path_to_file, requested=None):
	##TODO if we need exif info -- broken method##
	img = Image.open(path_to_file)
	if requested is not None:
		exif = { ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS and k in requested}
	else:
		exif = { ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS and k in requested}

	return exif

# print(get_image_type('../../../data/test_images/_ORIGINAL.png'))
# print(get_image_size('../../../data/test_images/lena512.pgm'))

