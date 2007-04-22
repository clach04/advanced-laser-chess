# uses PIL
# see http://www.pythonware.com/library/pil/handbook/introduction.htm

import Image

outfile_type=".png"
outfile_type=".gif"
outfile_pattern="small_tiles_cropped%d.png"
outfile_pattern="small_tiles_cropped%02d.png"
outfile_pattern="small_tiles_cropped%02d.gif"
outfile_pattern="small_stomper%02d"
outfile_pattern="small_stomper%d"
outfile_pattern=outfile_pattern+outfile_type
infile="small_tiles.png"

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


# 2nd row down
starty=1 * (tile_hlen-1)

for tile_count in range(8*2):
    print 'tile_count ', tile_count ,
    startx=tile_count * (tile_xlen-1)
    #starty=tile_count * (tile_hlen-1)
    print (startx, starty)
    box_with_border = (startx, starty, startx+tile_xlen, starty+tile_hlen)
    region = im.crop(box_with_border)
    region = region.crop(box_without_border)
    outfile=outfile_pattern%(tile_count)
    if tile_count>=8:
        #outfile='red_'+outfile_pattern%(tile_count-8)
        outfile='green_'+outfile_pattern%(tile_count-8)
    region.save(outfile)

#out = im.resize((128, 128))
#out = im.rotate(45) # degrees counter-clockwise

