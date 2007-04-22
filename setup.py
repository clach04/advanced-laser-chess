"""
laserchess setup for py2exe (rather than source)

To use simply issue:

    setup.py py2exe
"""

from distutils.core import setup
import py2exe
import sys


hiddenimports = []
hidden_excludes=[]

## FIXME
#hiddenimports.append('elementtree')
#hiddenimports.append('elementtree.ElementTree')

zipfile = r"lib\shardlib"
options = {
    'py2exe': { 
                'includes': hiddenimports,
                'excludes': hidden_excludes,
                "compressed": 1,
                "optimize": 0,  ## 0 as I currently rely on assert statements (which I need to fix) ##"optimize": 1,  ## 1 and NOT 2 because I use the __doc__ string as the usage string. 2 optimises out the doc strings
              }
       }


program_name="alc"
exe_dest_dir="prog"


exe_info = dict(
    #script = program_name+".py",
    script = "cherry_alc.py",
    dest_base = exe_dest_dir + '/' + program_name
    )

import os
import glob
## RE-FACTOR!!
data_file_list = ['wz_jsgraphics.js', 'template_alc.html', 'readme.txt']

data_files = []
data_files.append((exe_dest_dir, data_file_list))

import cherry_alc
for temp_piecedir in cherry_alc.valid_pieces:
    data_file_list = glob.glob(os.path.join(temp_piecedir, '*'))
    tdir = os.path.join(exe_dest_dir, temp_piecedir)
    temp_tuple = (tdir, data_file_list)
    data_files.append(temp_tuple)

setup(
    # The lib directory contains everything except the executables and the python dll.
    zipfile = zipfile,
    name = program_name,
    version = "0.2",
    description = "Advanced Laser Chess",
    url="http://kpg.sourceforge.net/",
    author="Chris Clark",
    #console = ["cherry_alc.py"],
    console = [exe_info ],
    #data_files=[(exe_dest_dir, ["kpg.xrc", icon_file, 'mycolors.txt', 'template.html', 'template.txt'])],
    #data_files=[(exe_dest_dir, data_file_list)],
    data_files=data_files,
    options = options
    )

