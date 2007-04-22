# uses PIL
# see http://www.pythonware.com/library/pil/handbook/introduction.htm

# rotates 2 input files to make 8 output files
# changes colour(s) (slow!, does not make use of PIL image filters)
# dumps a text file called size.txt with dimensions
# TODO transparency support (keep transparency, replace black with transparency)

import os
import sys

import Image

outfile_type=".png" ## creates 24bit images if pixesl change, orginal depth if only rotated - unless make explict pallete/conversion
outfile_type=".gif" ## creates images with web safe colours, so often get dithered colours :-( unless perform make explict pallete/conversion with no dither
piece_name='stomper'
piece_name='laser'

# mappings from filenames in laserchess.org to alc names
laserchess_org_2alc_name_mapping ={
    'bomb' : 'bomb', 
    'diagonal' : 'mirror', 
    'stunner' : 'freezer', 
    'king' : 'king', 
    'laser' : 'laser', 
    'stomper' : 'stomper', 
    'mirrorstomper' : 'mirrorstomper', 
    'onewaymirror' : 'oneway_mirror', 
    'splitter' : 'prism', 
    'hyper' : 'transporter',
    'hole' : 'hole_square',
    'hyperhole' : 'warp',
    'blank' : 'blank'
    }

# no mapping dict
alc_names ={
    'bomb' : 'bomb', 
    'mirror' : 'mirror', 
    'freezer' : 'freezer', 
    'king' : 'king', 
    'laser' : 'laser', 
    'stomper' : 'stomper', 
    'mirrorstomper' : 'mirrorstomper', 
    'oneway_mirror' : 'oneway_mirror', 
    'prism' : 'prism', 
    'transporter' : 'transporter',
    'hole_square' : 'hole_square',
    'warp' : 'warp',
    'blank' : 'blank'
    }



def change_colours(input_colour_map):
    def private_filter(in_image):
        """poor colour filter/converter
        """
        out_image = in_image.copy()
        out_image = out_image.convert() # convert to rgb
        
        colour_map = input_colour_map
        
        width, height = out_image.size
        colour_counts={}
        pixels_across = range(width)
        for y in range(height):
            for x in pixels_across:
                pixel_info = out_image.getpixel((x, y))
                #print pixel_info
                try:
                    new_colour = colour_map[pixel_info]
                    out_image.putpixel((x, y), new_colour)
                except KeyError, info:
                    #print pixel_info
                    pass
        
        return out_image
    return private_filter


def dumb_filter_and_save(input_image, dumb_filter_func, new_filename):
    #dumb_filter_func(input_image).save(new_filename)
    dumb_filter_func(input_image).convert(mode = 'P', palette = Image.ADAPTIVE, dither = Image.NONE).save(new_filename)

def create_piece_bitmaps(infile_pattern, in_piece_name, out_piece_name, outfile_type, out_dirname=None):
    outfile_pattern="%dx%d_%s%d"
    outfile_pattern="%dx%d_%d_%s%d"
    outfile_pattern="%(player_number)d_%(out_piece_name)s%(tile_count)d"
    #outfile_pattern="F:\\documents\\drive_f_share\\python\\laserchess\\data\\sharpalc\\%dx%d_%s%d"
    #outfile_pattern="out_"+outfile_pattern
    outfile_pattern=outfile_pattern+outfile_type
    
    in_dir = os.path.dirname(infile_pattern)
    sys.path.append(in_dir)
    
    try:
        from tile_colours import p1top2_colours, p1tofrozen_colours
    except ImportError, info:
        print 'unable to import colour mappings, using defaults'
        # default colour mapping
        p1colour = (180, 72, 72)
        p1mirror_colour = (255, 180, 180)
        
        p2colour = (72, 180, 72)
        #p2colour = (72, 72, 180)# test blue
        p2mirror_colour = (180, 255, 180)
        
        frozen_colour = (180, 180, 180)
        
        p1top2_colours = {p1mirror_colour : p2mirror_colour, p1colour : p2colour}
        p1tofrozen_colours = {p1mirror_colour : frozen_colour, p1colour : frozen_colour}
    try:
        from tile_colours import orig_to_p1_colours
    except ImportError, info:
        print 'no change of colour for p1 pieces'
        orig_to_p1_colours = {}
    
    change_colours_p1 = change_colours(orig_to_p1_colours )
    change_colours_p2 = change_colours(p1top2_colours)
    change_colours_gray = change_colours(p1tofrozen_colours)
    
    infile=infile_pattern%(in_piece_name, 0)
    im = Image.open(infile)
    tile_width, tile_height = im.size
    print im.format, im.size, im.mode
    if out_dirname is None:
        out_dirname="pieces_%(tile_width)dx%(tile_height)d" % locals()
    else:
        # not sure about this bit...
        out_dirname=out_dirname+"_%(tile_width)dx%(tile_height)d" % locals()
    try:
        os.mkdir(out_dirname)
        print 'created directory:', out_dirname
    except OSError, info:
        if info.errno==17:
            # already exists
            pass
        else:
            raise
    temp_file=open(os.path.join(out_dirname, 'size.txt'), 'w')
    temp_file.write("%(tile_width)dx%(tile_height)d\n" % locals())
    temp_file.close()
    
    outfile_pattern = os.path.join(out_dirname, outfile_pattern)

    out = im.rotate(90) # degrees counter-clockwise
    for tile_count in range(0,8,2):
        player_number=1
        outfile=outfile_pattern % locals()
        out = out.rotate(-90) # degrees clockwise
        # TODO transparent background
        #print outfile
        #out.save(outfile)
        dumb_filter_and_save(out, change_colours_p1, outfile)
        # TODO change colour...., re-save with new filename prefixed with green
        player_number=2
        outfile=outfile_pattern % locals()
        dumb_filter_and_save(out, change_colours_p2, outfile)
        frozen_outfile = outfile_pattern % { 'player_number':9, 'out_piece_name':out_piece_name, 'tile_count':tile_count}
        dumb_filter_and_save(out, change_colours_gray, frozen_outfile)
    
    infile=infile_pattern%(in_piece_name, 1)
    if not os.path.exists(infile):
        infile=infile_pattern%(in_piece_name, 0)
    im = Image.open(infile)
    image1x, image1y = im.size
    print im.format, im.size, im.mode
    assert tile_width == image1x, '45 rotated width does not match 0 rotated %d %d' % (tile_width, image1x)
    assert tile_height == image1y, '45 rotated height does not match 0 rotated %d %d' % (tile_height, image1y)
    
    out = im.rotate(90) # degrees counter-clockwise
    for tile_count in range(1,8,2):
        player_number=1
        outfile=outfile_pattern % locals()
        out = out.rotate(-90) # degrees clockwise
        # TODO transparent background
        #out.save(outfile)
        dumb_filter_and_save(out, change_colours_p1, outfile)
        # TODO change colour...., re-save with new filename prefixed with green
        player_number=2
        outfile=outfile_pattern % locals()
        dumb_filter_and_save(out, change_colours_p2, outfile)
        frozen_outfile = outfile_pattern % { 'player_number':9, 'out_piece_name':out_piece_name, 'tile_count':tile_count}
        dumb_filter_and_save(out, change_colours_gray, frozen_outfile)

################

# laserchess.org tileset
#infile_pattern="in_%s%d.gif"
infile_pattern="%s%d.gif"
infile_pattern="F:\\documents\\drive_f_share\\python\\laserchess\\data\\sharpalc\\%s%d.gif"
infile_pattern="F:\\documents\\drive_f_share\\python\\laserchess\\data\\alc\\%s%d.gif"
alc_mapping = laserchess_org_2alc_name_mapping


# amiga tile set
infile_pattern="F:\\documents\\drive_f_share\\python\\laserchess\\extracted_pieces_15x15\\1_%s%d.gif"
alc_mapping = alc_names

# amiga tile set
infile_pattern="F:\\documents\\drive_f_share\\python\\laserchess\\data\\extracted_pieces_45x45\\1_%s%d.gif"
alc_mapping = alc_names

#for piece_name in ['stomper', 'laser']:
for piece_name in alc_mapping:
    #create_piece_bitmaps(infile_pattern, piece_name, alc_mapping[piece_name], outfile_type)
    create_piece_bitmaps(infile_pattern, piece_name, alc_mapping[piece_name], outfile_type, out_dirname='testpieces')

