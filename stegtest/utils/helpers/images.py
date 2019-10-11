import imghdr

from PIL import Image, ExifTags

def get_image_type(file):
	return imghdr.what(file)

def get_info(file, requested=None):
	##unclear if we need al this info for downloading...##
	#TODO also only probably works with certain image formats....
	img = Image.open(file)
	if requested is not None:
		exif = { ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS and k in requested}
	else:
		exif = { ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS and k in requested}

	return exif