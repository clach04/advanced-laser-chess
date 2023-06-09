# uses PIL
# see http://www.pythonware.com/library/pil/handbook/introduction.htm

import os

import Image

outfile_type=".png"
outfile_type=".gif"
outfile_pattern="%d_%s%d"
outfile_pattern=outfile_pattern+outfile_type



infile="data/small_tiles.png"
## ALC tile dimensions for Original Amiga alc tiles in ILBM/IFF file
tile_xlen=17 # width
tile_hlen=19 # height
box_without_border = (1, 2, 16, 17) # the actual size of the extracted tile


## large tiles from X11 version? I got them from http://www.ljudmila.org/dat/Blender_Laser_Chess/
## NOTE I had to take the large xpm file and saves as gif
infile="data/alc_pieces_big.gif"
#tile_xlen=46 # width
tile_xlen=45 # width
tile_hlen=50 # height
box_without_border = (0, 1, tile_xlen, tile_hlen) # working....
box_without_border = (0, 2, tile_xlen, tile_hlen-1) # working....
box_without_border = (0, 3, tile_xlen, tile_hlen-2) # the actual size of the extracted tile

im = Image.open(infile)

print im.format, im.size, im.mode

# define crop coordinates, coordinates are (left, upper, right, lower)
# with (0,0) being top left hand corner

"""
Cheat, extract tile with border then extract image we want out of bordered tile
dirty but fast (with small numbers) and saves working out off-sets (tile x*1+.....)
"""




tile_width = box_without_border[2] - box_without_border[0] 
tile_height = box_without_border[3] - box_without_border[1] 
out_dirname = None
if out_dirname is None:
    out_dirname="data/extracted_pieces_%(tile_width)dx%(tile_height)d" % locals()
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
print 'using dir:', out_dirname
outfile_pattern = os.path.join(out_dirname, outfile_pattern)


def extract_tiles(tile_countx, tile_county, player_number, piece_name, num_tiles=1, rotation=0):
    """
    FIXME TODO check if rotation in source matches alc rotation!!
    may need to map rotation
    """
    if num_tiles != 1:
        raise NotImplemented('num_tiles != 1')
    
    if tile_xlen==17 and tile_hlen==19:
        # amiga small size
        startx=tile_countx * (tile_xlen-1)
        starty=tile_county * (tile_hlen-1)
        # not sure why my logic doesn't work for all cases :-(
        # simple hack to get image out
    else:
        startx=tile_countx * (tile_xlen)
        starty=tile_county * (tile_hlen+1)
        
    print (startx, starty)
    box_with_border = (startx, starty, startx+tile_xlen, starty+tile_hlen)
    region = im.crop(box_with_border)
    region = region.crop(box_without_border) ## test, useful for working out tile size
    outfile=outfile_pattern%(player_number, piece_name, rotation)
    region.save(outfile)


#extract_tiles(0, 0, 1, 'freezer', num_tiles=1, rotation=0)
extract_tiles(4, 0, 1, 'freezer', num_tiles=1, rotation=0)
extract_tiles(5, 0, 1, 'freezer', num_tiles=1, rotation=1)
extract_tiles(0, 0, 1, 'freezer', num_tiles=1, rotation=4) ## TEST - useful for working out tile size
extract_tiles(1, 0, 1, 'freezer', num_tiles=1, rotation=5) ## TEST - useful for working out tile size
extract_tiles(8, 0, 2, 'freezer', num_tiles=1, rotation=4) ## TEST - useful for working out tile size

extract_tiles(0, 1, 1, 'stomper', num_tiles=1, rotation=0)
extract_tiles(1, 1, 1, 'stomper', num_tiles=1, rotation=1)

extract_tiles(0, 2, 1, 'oneway_mirror', num_tiles=1, rotation=0)
extract_tiles(1, 2, 1, 'oneway_mirror', num_tiles=1, rotation=1)

extract_tiles(0, 3, 1, 'mirror', num_tiles=1, rotation=0)
extract_tiles(1, 3, 1, 'mirror', num_tiles=1, rotation=1)

extract_tiles(0, 4, 1, 'laser', num_tiles=1, rotation=0)
extract_tiles(1, 4, 1, 'laser', num_tiles=1, rotation=1)

extract_tiles(4, 5, 1, 'prism', num_tiles=1, rotation=0)
extract_tiles(5, 5, 1, 'prism', num_tiles=1, rotation=1)

if tile_xlen==17 and tile_hlen==19:
    # amiga small size
    extract_tiles(16, 0, 1, 'bomb', num_tiles=1, rotation=0)
    extract_tiles(16, 1, 1, 'bomb', num_tiles=1, rotation=1)
else:
    extract_tiles(16, 0, 1, 'bomb', num_tiles=1, rotation=0)
    extract_tiles(17, 0, 1, 'bomb', num_tiles=1, rotation=1)

extract_tiles(18, 1, 1, 'mirrorstomper', num_tiles=1, rotation=0)
extract_tiles(18, 1, 1, 'mirrorstomper', num_tiles=1, rotation=1)

extract_tiles(16, 2, 1, 'king', num_tiles=1, rotation=0)
extract_tiles(16, 2, 1, 'king', num_tiles=1, rotation=1)

extract_tiles(16, 3, 1, 'transporter', num_tiles=1, rotation=0)
extract_tiles(16, 3, 1, 'transporter', num_tiles=1, rotation=1)


if tile_xlen==17 and tile_hlen==19:
    # amiga small size
    extract_tiles(0, 7, 1, 'warp', num_tiles=1, rotation=0)
    extract_tiles(0, 7, 1, 'warp', num_tiles=1, rotation=1) # coords are not the same as pieces :-(
    #extract_tiles(3, 7, 1, 'warp', num_tiles=1, rotation=1)
else:
    extract_tiles(18, 2, 1, 'warp', num_tiles=1, rotation=0)
    extract_tiles(18, 2, 1, 'warp', num_tiles=1, rotation=1) # coords are not the same as pieces :-(

if tile_xlen==17 and tile_hlen==19:
    # amiga small size
    extract_tiles(0, 6, 1, 'hole_square', num_tiles=1, rotation=0)
    extract_tiles(0, 6, 1, 'hole_square', num_tiles=1, rotation=1) # coords are not the same as pieces :-(
    #extract_tiles(5, 6, 1, 'hole_square', num_tiles=1, rotation=1)
else:
    ## "hole" tile - create "by hand"
    blank_tile = Image.new(mode = 'RGB', size=(tile_width, tile_height), color=(125,125,125)) ## PIL manual says colour defaults to black
    blank_tile = blank_tile.convert(mode = 'P', palette = Image.ADAPTIVE, dither = Image.NONE)
    ## at some point want transparent?
    piece_name = 'hole_square'
    outfile=outfile_pattern%(1, piece_name, 0)
    blank_tile.save(outfile)
    outfile=outfile_pattern%(1, piece_name, 1)
    blank_tile.save(outfile)

## blank tile - create "by hand"
## TODO consider creating "hole" by hand too
#blank_tile = Image.new(mode = 'P', size=(tile_width, tile_height), color)
blank_tile = Image.new(mode = 'P', size=(tile_width, tile_height)) ## PIL manual says colour defaults to black
## at some point want transparent?
piece_name = 'blank'
outfile=outfile_pattern%(1, piece_name, 0)
blank_tile.save(outfile)
outfile=outfile_pattern%(1, piece_name, 1)
blank_tile.save(outfile)



#out = im.resize((128, 128))
#out = im.rotate(45) # degrees counter-clockwise

if tile_xlen==17 and tile_hlen==19:
    colour_template = '''
# EDITME!
# default colour mapping
p1colour = (176, 32, 0)
p1mirror_colour = (240, 48, 0)

p2colour = (72, 180, 72)
#p2colour = (72, 72, 180)# test blue
p2mirror_colour = (180, 255, 180)

frozen_colour = (180, 180, 180)

orig_background_colour = (96, 96, 96)
new_background_colour = (0, 0, 0)


# EDITME!
orig_to_p1_colours = {orig_background_colour:new_background_colour}
p1top2_colours = {p1mirror_colour : p2mirror_colour, p1colour : p2colour, orig_background_colour:new_background_colour}
p1tofrozen_colours = {p1mirror_colour : frozen_colour, p1colour : frozen_colour, orig_background_colour:new_background_colour}

'''
else:
    colour_template = '''
# EDITME!
# Keep alc colours
p1colour = (178, 32, 0)
p1mirror_colour = (243, 48, 0)

p2colour = (0, 162, 0)
p2mirror_colour = (146, 227, 0)

frozen_colour = (180, 180, 180)

orig_background_colour = (255, 255, 255)
new_background_colour = (0, 0, 0)

# New colours
new_p1colour = (180, 72, 72)
new_p1mirror_colour = (255, 180, 180)
p2colour = (72, 180, 72)
p2mirror_colour = (180, 255, 180)



# EDITME!
#orig_to_p1_colours = {orig_background_colour:new_background_colour}
orig_to_p1_colours = {p1colour:new_p1colour, p1mirror_colour:new_p1mirror_colour, orig_background_colour:new_background_colour}
p1top2_colours = {p1mirror_colour : p2mirror_colour, p1colour : p2colour, orig_background_colour:new_background_colour}
p1tofrozen_colours = {p1mirror_colour : frozen_colour, p1colour : frozen_colour, orig_background_colour:new_background_colour}

'''

temp_file = open(os.path.join(out_dirname, 'tile_colours.py'), 'w')
temp_file.write(colour_template)
temp_file.close()
