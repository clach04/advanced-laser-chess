# uses PIL
# see http://www.pythonware.com/library/pil/handbook/introduction.htm

# rotates 2 input files to make 8 output files
# does not change colour(s) yet

import os

import Image

piece_name='stomper'

def create_piece_bitmaps(in_piece_name):
    #infile_pattern="in_%s%d.gif"
    infile_pattern="%s%d.gif"
    infile_pattern="F:\\documents\\drive_f_share\\python\\laserchess\\data\\sharpalc\\%s%d.gif"
    infile_pattern="F:\\documents\\drive_f_share\\python\\laserchess\\small_%s%d.gif"
    infile_pattern="F:\\documents\\drive_f_share\\python\\laserchess\\green_small_%s%d.gif"
    infile_pattern="F:\\documents\\drive_f_share\\python\\laserchess\\extracted_pieces_15x15\\1_%s%d.gif"
    
    infile=infile_pattern%(in_piece_name, 0)
    im = Image.open(infile)
    im = im.convert() ## convert pixel/image data to RGB mode
    image0x, image0y = im.size
    print im.format, im.size, im.mode
    height = image0y 
    width = image0x
    
    colour_counts={}
    for y in range(height):
        pixels_across = range(width)
        row_num = str(y+1)
        for x in pixels_across:
            pixel_info = im.getpixel((x, y))
            #print pixel_info
            try:
                colour_counts[pixel_info] += 1
            except KeyError, info:
                colour_counts[pixel_info] = 1
    print colour_counts
    """
    for red only laserchess.org images:
    
    For an indexed image (P mode) get something like:
        {1: 30, 2: 166, 3: 128}
        
    For an full colour image (RGB mode) get something like:
        {(0, 0, 0): 128, (255, 180, 180): 30, (180, 72, 72): 166}
    
    
    for orig Amiga laserchess extracted tiles:
    
    red
    >python -u "colour_info.py"
    None (15, 17) RGB
    {(96, 96, 96): 126, (176, 32, 0): 105, (240, 48, 0): 24}
    
    green
    >python -u "colour_info.py"
    None (15, 17) RGB
    {(96, 96, 96): 126, (144, 224, 0): 24, (0, 160, 0): 105}
    
    """
    

create_piece_bitmaps(piece_name, )

