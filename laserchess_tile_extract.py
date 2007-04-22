# uses PIL
# see http://www.pythonware.com/library/pil/handbook/introduction.htm

import os

import Image

outfile_type=".png"
outfile_type=".gif"
outfile_pattern="small_tiles_cropped%d.png"
outfile_pattern="small_tiles_cropped%02d.png"
outfile_pattern="small_tiles_cropped%02d.gif"
outfile_pattern="small_stomper%02d"
outfile_pattern="%d_stomper%d"
outfile_pattern="%d_%s%d"
outfile_pattern=outfile_pattern+outfile_type
infile="small_tiles.png"
infile="data/small_tiles.png"

im = Image.open(infile)

print im.format, im.size, im.mode

# define crop coordinates, coordinates are (left, upper, right, lower)
# with (0,0) being top left hand corner

"""
Cheat, extract tile with border then extract image we want out of bordered tile
dirty but fast (with small numbers) and saves working out off-sets (tile x*1+.....)
"""


#box = (1, 1, 16, 18) # (15,17) image -- top left hand corner image that we want
startx=1
starty=1
tile_xlen=15 # width
tile_hlen=17 # height
#box_without_border = (startx, starty, startx+tile_xlen, starty+tile_hlen)
box_without_border = (1, 1, 16, 18)



# box with border
#box = (0, 0, 17, 19) # (17,19) image includes 1 pixel border all round which we do not want, useful for testing!
startx=0
starty=0
tile_xlen=17 # width
tile_hlen=19 # height


tile_width = tile_xlen
tile_height = tile_hlen
out_dirname = None
if out_dirname is None:
    out_dirname="extracted_pieces_%(tile_width)dx%(tile_height)d" % locals()
else:
    # not sure about this bit...
    out_dirname=out_dirname+"_%(tile_width)dx%(tile_height)d" % locals()
try:
    os.mkdir(out_dirname)
except OSError, info:
    if info.errno==17:
        # already exists
        pass
    else:
        raise
outfile_pattern = os.path.join(out_dirname, outfile_pattern)


# 2nd row down
starty=1 * (tile_hlen-1)

for tile_count in range(8*2):
    piece_name = 'stomper'
    #piece_name = 'test'
    print 'tile_count ', tile_count ,
    startx=tile_count * (tile_xlen-1)
    #starty=tile_count * (tile_hlen-1) ## test 2nd row down, not quite working yet...
    print (startx, starty)
    box_with_border = (startx, starty, startx+tile_xlen, starty+tile_hlen)
    region = im.crop(box_with_border)
    region = region.crop(box_without_border)
    outfile=outfile_pattern%(1, piece_name, tile_count)
    if tile_count>=8:
        outfile=outfile_pattern%(2, piece_name, tile_count-8)
    region.save(outfile)

#out = im.resize((128, 128))
#out = im.rotate(45) # degrees counter-clockwise

colour_template = '''
# EDITME!
# default colour mapping
p1colour = (180, 72, 72)
p1mirror_colour = (255, 180, 180)

p2colour = (72, 180, 72)
#p2colour = (72, 72, 180)# test blue
p2mirror_colour = (180, 255, 180)

frozen_colour = (180, 180, 180)

# EDITME!
#p1top2_colours = {p1mirror_colour : p2mirror_colour, p1colour : p2colour}
#p1tofrozen_colours = {p1mirror_colour : frozen_colour, p1colour : frozen_colour}

'''

temp_file = open(os.path.join(out_dirname, 'tile_colours.py'), 'w')
temp_file.write(colour_template)
temp_file.close()
