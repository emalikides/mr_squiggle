# Emmanuel Malikides
# 2/5/16
#
# Script to find ordered sets of points for robot arm to draw given black and white image
# assumed to be mainly comprised of lines.
# Useage:
# python find_strokes <image_filename> <scale> <comp_factor> [<image_output_filename>]
# <image_filename>
# <scale> floating point number to scale pixel coordinates to real-world.
# <comp_factor> compression factor (an integer, higher means fewer points sampled)
# [<image_output_filename>] optional argument. if included an image will be written to the output filename 
# in png format and the output will be visualised.
# 
# EG: python find_strokes.py fish.png 1 10 image.png
#     python find_strokes.py fish.png 3 10 

from PIL import Image, ImageDraw
import time
import sys
import os

# Edit constants below here if necessary
#----------------------#----------------------#----------------------#----------------------#
# Code string.
CODE = \
"""
x:= {x_pt};
y:= {y_pt};
z:= {z_pt};
position.trans := [1600+x,y,z+100];
position.rot := OrientZYX(0,180,0);
MoveJ position,v1000,z20,tool0;
"""
# Scale factor from pixels -> real world coords.
Z_UP = 385
Z_DOWN = 375

# filename of output 
OUT = "code.txt"

#--------#--------#--------#--------#--------#--------#--------#--------#--------#--------#

def blackify(im):
	# A list of True / False indicating the black/white pixels.
	my_im = []
	for i in im.getdata():
		my_im.append(i[3] != 0)
	return my_im

# returns whether a pixel is not in the list of grouped pixels.
def not_in(l_sets, n):
	return all(not (n in s) for s in l_sets)

# searches the adjacent pixels to pixel i of image im.
def search_adjacent(i, s, strokes, im, comp_f):

	stack = [(i,len(s))]
	l = []

	while stack:
		(i, prev_d) = stack.pop()
		assert (not (i in s)), "i:%d"%i
		s.append(i)
		nbrs = {'L':i-1, 'R':i+1, 'U':i-WIDTH, 'D':i+WIDTH}
		ns = [nbrs['L'], nbrs['D'], nbrs['R'], nbrs['U']]

		curr_d = len(s)
		if (curr_d-prev_d)>1:
			strokes.append(l)
			l = []
		if len(s) % comp_f == 0:
			l.append(j)	

		for j in ns:
			try:
				im[j]
			except IndexError:
				pass
			else:
				if im[j] and not j in s and j not in [pt[0] for pt in stack]:				
					stack.append((j, curr_d))

def find_groups(image, comp_factor):
	# number of black pixels. 
	NBLACK = sum(image)
	# list of sets of adjacent black pixels
	groups = []
	sgroups = []

	i = 0
	counted = 0
	# group together the black parts of the image
	while counted < NBLACK:
		# if the element is black and we haven't explored it, explore it.
		if image[i] and not_in(groups,i):
			templist = []
			# search for connected components 
			search_adjacent(i, templist, sgroups, image, comp_factor)
			groups.append(templist)

		counted = sum([len(s) for s in groups])
		assert(counted<=NBLACK)
		i += 1

	return (groups, sgroups)


def to_coord(width, height, coord):
	""" returns the coordinate for a pixel in a list of pixels """
	x = coord % width
	y = coord // width
	assert (y < height)
	return (coord % width, coord // width)

def naive_get_points(component, fcomp):
	""" Turn a connected component into points."""
	return(component[::fcomp])

def write_points(outfile, code, point_groups, up, down, scale = 1.0):

	fp = open(outfile,'w')

	for points in point_groups:
		fp.write(code.format(x_pt = int(round(scale*points[0][0])), 
						     y_pt = int(round(scale*float(points[0][1]))),
						     z_pt = int(round(scale*float(up)))))
		for point in points:
			fp.write(code.format(x_pt = int(round(scale*point[0])), 
								 y_pt = int(round(scale*float(point[1]))),
								 z_pt = int(round(scale*float(down)))))
		fp.write(code.format(x_pt = int(round(scale*points[-1][0])), 
						     y_pt = int(round(scale*float(points[-1][1]))),
						     z_pt = int(round(scale*float(up)))))

	fp.close()


def dumb_filter(stroke_coords, comp_factor):
	# filter large jumps.
	new_stroke_coords = []
	for stroke in stroke_coords:
		if stroke:
			p1 = stroke[0]
			tstroke = [p1]

			for p2 in stroke[1:]:
				d = (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2
				if d > 2*(comp_factor-1)**2:
					new_stroke_coords.append(tstroke)
					tstroke=[]
				tstroke.append(p2)
				p1 = p2

			new_stroke_coords.append(tstroke)

	return new_stroke_coords

if __name__ == "__main__":

	if len(sys.argv) not in (4,5):
	    sys.stderr.write("*** USAGE ***\n"
	                     "python %s <image_filename> <scale> <comp_factor>\n\n"
	                     % sys.argv[0])
	    sys.exit(1)

	(IMAGE, SCALE, comp_factor) = (sys.argv[1], \
		float(sys.argv[2]), int(sys.argv[3]))

	im = Image.open(IMAGE)
	if (im.mode!="RGBA"):
		sys.stderr.write("Image might not be .png"
                 % sys.argv[0])

	newim = Image.new('RGBA',im.size, 'white')
	draw = ImageDraw.Draw(newim)

	WIDTH = im.size[0]
	HEIGHT = im.size[1]

	my_im = blackify(im)

	# find the groups of black pixels
	(ind_groups, stroke_groups) = find_groups(my_im, comp_factor)

	# get points for each group
	# stroke_groups = [naive_get_points(group, comp_factor) for group in ind_groups]

	# convert to coordinates
	coord_stroke_groups = [[to_coord(WIDTH, HEIGHT, x) for x in group] for group in stroke_groups]

	coord_stroke_groups = dumb_filter(coord_stroke_groups, comp_factor)

	# write to file.
	write_points(OUT, CODE, coord_stroke_groups, Z_UP, Z_DOWN, SCALE)
	print("Written {} points to draw to {}.".format(sum([len(group) for group in coord_stroke_groups]),\
													OUT))

	# draw the groups
	#-----------------##-----------------##-----------------##-----------------#
	if len(sys.argv)==5:
			
		for group in coord_stroke_groups:
			draw.line(group,fill=(255,0,0,255))	

		newim.save(sys.argv[4],'PNG')
		
		for group in ind_groups:
			draw.point([to_coord(WIDTH, HEIGHT, x) for x in group],fill=(0,0,0,255))	
		newim.show()
		# # testing: recreate the image from the sequence of coordinates. 

		print("Simulation of output written to image.png.")
