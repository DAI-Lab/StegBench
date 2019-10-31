import imghdr
import collections
import stegtest.utils.lookup as lookup
import stegtest.utils.filesystem as fs

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

def add_noise_to_image(path_to_input, path_to_output, noise_level):
	"""adds noise to an image at specified noise level"""
	raise NotImplementedError

def crop_image(path_to_input, path_to_output, width, height):
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

def resize_image(path_to_input, path_to_output, width, height):
	"""resizes an image to the specified dimensions"""
	img = Image.open(path_to_input)

	cropped_img = img.resize((width, height))
	cropped_img.save(path_to_output)

	img.close()
	cropped_img.close()

def rotate_image(path_to_input, path_to_output, degrees):
	"""rotates image by specified degrees"""
	img = Image.open(path_to_input)

	cropped_img = img.rotate(degrees)
	cropped_img.save(path_to_output)

	img.close()
	cropped_img.close()

def apply_operation(operation, args, partition):
	function = {
		lookup.add_noise: add_noise_to_image,
		lookup.crop: crop_image,
		lookup.resize: resize_image,
		lookup.rotate: rotate_image,
	}[operation]

	function(partition[lookup.input_file_header], partition[lookup.output_file_header], *args)

def get_image_type(path_to_file):
	#return imghdr.what(path_to_file)
	ext = fs.get_extension(path_to_file)[1:]
	return ext

def is_image_file(path_to_file):
	return get_image_type(path_to_file) in lookup.all_supported_types()

def get_image_info(path_to_file):
	"""Returns image info as a dictionary with elements, type, width, height, channels"""
	#assert(file_exists()) TODO
	img_type = get_image_type(path_to_file)
	im = Image.open(path_to_file)
	width, height = im.size
	channels = im.mode


	##TODO Need to get im.quantization information possibly at different quantization levels (0, 25, 50, 75, 100)
	##need to calculat the nonzero AC DCT coefficients (each 8x8 block has 63 of these coefficients)
	# print(im.quantization)

	info_dict = collections.OrderedDict()
	info_dict[lookup.file_path] = path_to_file 
	info_dict[lookup.image_type] = img_type 
	info_dict[lookup.image_width] = width
	info_dict[lookup.image_height] = height
	info_dict[lookup.image_channels] = channels

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
