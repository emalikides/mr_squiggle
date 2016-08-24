# Emmanuel Malikides
# 29/4/2016
# Function to complete a partially drawn image based on history of images.
# Assumptions:
# - The partial image supplied defines the coordinates of the returned image. 
# 

import numpy as np
from PIL import Image, ImageDraw
from strokes import blackify

# Train a classifier

# Classify partial image.

# Get classified image from image bank, transform it to match the image.
# What kinds of geometric transforms are there?
# rotation - 360
# translation - crop to 
# skew
# scale

# solutions:
# Brute-force search.
# Downsample drawn image to search for transformation?


def find_transform(partial_image, recognised_image):
	p_im = Image.open(partial_image)
	r_im = Image.open(recognised_image)

	# randomly do a perspective transform until dot product is above a threshhold.
	a = 0 


# Recognise parts of the image, and match them?
def make_completion(partial_image, recognised_image):
	""" 
	Takes a partially drawn image, and an image matched to the partially drawn image.
	Returns an image with the lines to be drawn to complete the partial image.
	"""
	pass
	# Search over: translations, rotations, scale and skew transforms.

RECIM = 'dog.png'
IM = 'dog_fucked.png'

# testing

im = Image.open(RECIM)
print(im.size, im.format, im.mode)
new_size = im.size
newim = Image.new('RGBA',new_size, 'white')
draw = ImageDraw.Draw(newim)

find_transform(IM,RECIM)

# Return parts to be drawn to complete.
