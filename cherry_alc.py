"""
debug single (web) user!!

# TODO losses, needs to use pass in piece dirname via hidden form
# TODO add in line HTML compression (either simple space removal and/or gzip)?
# TODO Add cookie session or auth support so that only specific clients can make changes/view a specific game
# TODO add multiple games per server?
"""

import sys
import os

try:
    #raise ImportError
    import cStringIO as StringIO
    print 'really using (faster) cStringIO'
except ImportError, info:
    import StringIO
    print 'using (slower) pure StringIO'

"""
# Python 2.3 added support for .py|.pyc files in zip files
sys.path.insert(0, 'cherrypy.zip')  # Add .zip file to front of path
"""
import cherrypy

import alc_model
#import gen_alc_html
from gen_alc_html import html_board, html_boardV2, html_losses

## from http://www.py2exe.org/index.cgi/HowToDetermineIfRunningFromExe
## slightly modified
def main_is_frozen():
    import imp
    return (hasattr(sys, "frozen") or # new py2exe
            hasattr(sys, "importers") # old py2exe
            or imp.is_frozen("__main__")) # tools/freeze

def get_main_dir():
    if main_is_frozen():
        return os.path.dirname(sys.executable)
    this_module_path = os.path.abspath(os.path.dirname(__file__))
    #return os.path.dirname(sys.argv[0])
    return this_module_path

this_module_path = get_main_dir() ## os.path.abspath(os.path.dirname(__file__))

static_dirname = 'static_example' # use basename/dirname and have fully quailifed path?
static_dirname = 'different_dir' # use basename/dirname and have fully quailifed path?
pieces_location=None
pieces_location='pieces_18x18'
pieces_location='pieces_46x46'
pieces_location='PastelAmiga_pieces_45x45'
static_dirname = pieces_location
valid_pieces=[
                'OriginalAmiga_pieces_15x15', 
                'pieces_18x18', 
                'AmigaBig_pieces_45x45', 
                'PastelAmiga_pieces_45x45', 
                'pieces_46x46',
            ]

form_str = '''
<form action="test" method="GET">
    What is your name?
    <input type="text" name="name" />
    <input type="submit" />
</form>

<br><br><br><br>
or <a href=./%s/index.html>static example</a>
<br><br>
or <a href=./stop>stop server</a>
<br><br>
or <a href=./restart>restart server</a>
<br><br>
or <a href=./ctrlc>ctrlc server</a>
''' % (static_dirname)

class MyWebApp:
    
    def __init__(self):
        # game setup
        self.playing_board = alc_model.board()
        shoot_debug=False
        #shoot_debug=True
        if shoot_debug:
            self.playing_board.set_board_piece((1,6), None) # blank_square - clean up previous location
            self.playing_board.set_board_piece((2,6), None) # blank_square - clean up previous location
            self.playing_board.set_board_piece((12,6), None) # blank_square - clean up previous location
            self.playing_board.set_board_piece((13,6), None) # blank_square - clean up previous location
            self.playing_board.set_board_piece((14,6), None) # blank_square - clean up previous location
            self.playing_board.set_board_piece((1,8), None) # blank_square - clean up previous location
            self.playing_board.set_board_piece((1,10), None) # blank_square - clean up previous location
            self.playing_board.init_board_piece((3,6), alc_model.oneway_mirror_piece,alc_model.PLAYER_ONE, alc_model.EAST)
            self.playing_board.init_board_piece((2,6), alc_model.mirror_piece,alc_model.PLAYER_ONE, alc_model.EAST)

            self.playing_board.set_board_piece((12,4), None) # blank_square - clean up previous location
            self.playing_board.set_board_piece((13,4), None) # blank_square - clean up previous location
            self.playing_board.set_board_piece((13,1), None) # blank_square - clean up previous location
            self.playing_board.set_board_piece((14,8), None) # blank_square - clean up previous location
            self.playing_board.init_board_piece((11,4), alc_model.mirror_piece,alc_model.PLAYER_TWO, alc_model.EAST)
            self.playing_board.init_board_piece((10,4), alc_model.prism_piece,alc_model.PLAYER_TWO, alc_model.EAST)
            self.playing_board.init_board_piece((11,8), alc_model.bomb_piece,alc_model.PLAYER_TWO, alc_model.EAST)

    def index(self):
        #return form_str
        html_result_str = '''<META HTTP-EQUIV="Refresh"
            CONTENT="5; URL=/alc">'''
        html_result_str = '''<META HTTP-EQUIV="Refresh"
            URL=/alc">'''
        html_result_str = '''<meta HTTP-EQUIV="REFRESH" content="0; url=/alc">'''
        return html_result_str
    index.exposed = True
    
    def test(self, name = None):
        if name:
            return "Hey %s, what's up?" % name
        else:
                return 'Name missing. Please enter your name' + form_str
    test.exposed = True

    def ctrlc(self):
        """quit/stop server by emulating CTRL-C"""
        raise KeyboardInterrupt()
    ctrlc.exposed = True
   
    def restart(self):
        #cherrypy.engine.restart() # doesn't work for version 2.2.1
        cherrypy.server.restart() # for version 2.2.1
        return "app was restarted succesfully"
    restart.exposed = True
    
    def stop(self):
        #cherrypy.server.stop_http_server()
        #cherrypy.server.stop() ## appears to only stop the http server and not the app server
        #return "Stopping........."
        self.ctrlc()
    stop .exposed = True

    def alc(self, move_str=None, piece_pictures=None):
        ##TODO add setfocus script
        ## see http://www.html-faq.com/htmlforms/?entryfocus AND http://www.html-faq.com/htmlforms/?entryfocus
        if move_str is None:
            move_str=''
        if piece_pictures is None:
            piece_pictures = pieces_location
        error_info=''
        move_str=move_str.strip()
        if move_str != '':
            try:
                self.playing_board.enter_move( alc_model.piece_move(move_str) )
            except alc_model.InvalidMove, info:
                error_info = str(info)

        htmlfile = StringIO.StringIO()
        html_board(self.playing_board, htmlfile, piece_dirname=piece_pictures, error_text=error_info)
        html_result_str = htmlfile.getvalue()
        htmlfile.close()

        return html_result_str
    alc.exposed = True

    def alc_old(self, move_str=None, piece_pictures=None):
        ##TODO add setfocus script
        ## see http://www.html-faq.com/htmlforms/?entryfocus AND http://www.html-faq.com/htmlforms/?entryfocus
        alc_move_form_str = '''
        <div class="game_status2">
        %s
        <form id="move_form" action="alc" method="GET">
            Move?
            <input id="move_str" type="text" name="move_str" />
            <input type=hidden name="piece_pictures" value="%s">
            <input type="submit" value="Perform Move"/>
        </form>
        <!--
            NOTE! no code to prevent multiple submits from same "instance"
        //-->
        <div>
            <a id="pass" onclick="pass_turn();">Pass</a>
            <a id="pass" onclick="shoot();">Shoot</a>
            <a id="pass" onclick="rotate();">Rotate</a>
        </div>
        <p>examples:</p>
        pass<br>
        move (5,3) (5,5)<br>
        rotate (2,4) NORTH<br>
        shoot (5,3)<br>
        <br>
        r (2,4) 0<br>
        r (3,4) NORTH<br>
        <a id="show_shots" onclick="show_shots();">show_shots</a>
        <a id="debug_show_shots" onclick="debug_show_shots();">debug_show_shots</a>
        <a id="clear_shots" onclick="jg.clear();">clear shots</a>
        <br><a href=/tile_sizes>change board size</a>
        <br><a href=/losses>show losses</a>
        </div>
        '''
        if move_str is None:
            move_str=''
        if piece_pictures is None:
            piece_pictures = pieces_location
        error_info=''
        move_str=move_str.strip()
        if move_str != '':
            try:
                self.playing_board.enter_move( alc_model.piece_move(move_str) )
            except alc_model.InvalidMove, info:
                error_info = '<p style="color: rgb(255, 0, 0);">InvalidMove ' + str(info) + '</p>'

        dumb_str = alc_move_form_str % (error_info, piece_pictures)
        htmlfile = StringIO.StringIO()
        html_boardV2(self.playing_board, htmlfile, piece_dirname=piece_pictures, dumb_str=dumb_str)
        html_result_str = htmlfile.getvalue()
        htmlfile.close()

        return html_result_str
    alc_old.exposed = True

    def losses(self, piece_pictures=None):
        if piece_pictures is None:
            piece_pictures = pieces_location
        htmlfile = StringIO.StringIO()
        html_losses(self.playing_board, htmlfile, piece_dirname=piece_pictures)
        html_result_str = htmlfile.getvalue()
        htmlfile.close()

        return html_result_str
    losses.exposed = True

    def tile_sizes(self):
        html_result=[]
        for x in valid_pieces:
            html_result.append('''<a href=/alc?piece_pictures=%s>%s</a><br>''' % (x, x))
        
        return ''.join(html_result)
    tile_sizes.exposed = True



cherrypy.root = MyWebApp()


def main(argv=None):
    if argv is None:
        argv = sys.argv
        
    print 'using CherryPy Version:', cherrypy.__version__
    # note tested with: 2.2.1

    server_port = 8080
    server_port = 8088
    server_url = 'http://127.0.0.1:' + str(server_port)

    config_dict = {
                'server.socketPort':server_port, 
                #'server.environment':"production", ## comment out to log errors to web page (good for debug, but a security risk), also will reload on modified sources (or errors)
                'server.logToScreen':True,
                #'server.logToScreen':False,
                #'server.logFile':"/home/clach04/python/mywebserver.log"
                }
    
    if main_is_frozen():
        # avoid bug/problem - unclear on cause
        # debug cherrypy under py2exe to work out what is happening in reloader (know getting SystemExit somewhere)
        config_dict.update({
            'server.environment':"production",
            'server.logFile' : 'errlog.log',
        })
    
    
    """
    # Create static url "/static" that maps to folder on filesystem
    html_dir = static_dirname
    html_dir = os.path.join(this_module_path, html_dir)
    print html_dir
    static_web_folder='/%s' % static_dirname
    #static_web_folder='/alc/%s' % static_dirname
    config_dict.update({
        static_web_folder: {
            'staticFilter.on': True,
            'staticFilter.dir': html_dir
        }
    })
    """
    for static_dirname in valid_pieces:
        html_dir = static_dirname
        html_dir = os.path.join(this_module_path, html_dir)
        if not os.path.exists(html_dir):
            # Without this check cherrypy (2.1.1 at any rate) will fail when p2exe (if in debug (not production)) and NOT give any kind of useful information/traceback
            raise SystemExit('missing directory '+ html_dir)
        static_web_folder='/%s' % static_dirname
        config_dict.update({
            static_web_folder: {
                'staticFilter.on': True,
                'staticFilter.dir': html_dir
            }
        })
    
    ## see http://docs.cherrypy.org/serving-static-content
    if not os.path.exists('wz_jsgraphics.js'):
        # Without this check cherrypy (2.1.1 at any rate) will fail when p2exe (if in debug (not production)) and NOT give any kind of useful information/traceback
        #print 'DEBUG*******', 'missing file '+ 'wz_jsgraphics.js'
        raise SystemExit('missing file '+ 'wz_jsgraphics.js')
    config_dict.update({
        '/wz_jsgraphics.js': {
            'staticFilter.on': True,
            #'staticFilter.file': 'wz_jsgraphics.js'
            'staticFilter.file': os.path.join(this_module_path, 'wz_jsgraphics.js')
        }
    })
    
    """
    if sys.platform != 'Pocket PC':
        print 'Attempting to launch web browser....'
        def run_browser():
            import time
            import webbrowser
            time.sleep(1) # Give the server time to start
            webbrowser.open(server_url)
            
        import threading
        threading.Thread(target=run_browser).start()
    print 'Point web browser at:', server_url
    print 'Issue CTRL-C to terminate web server.'
    
    #cherrypy.config.update(file = 'tutorial.conf')
    cherrypy.config.update(updateMap = config_dict)
    cherrypy.server.start()
    ## COnsider using:
    ## cherrypy.server.start_with_callback
    ## to run_browser()
    """
    print 'Point web browser at:', server_url
    print 'Issue CTRL-C to terminate web server.'
    
    #cherrypy.config.update(file = 'tutorial.conf')
    cherrypy.config.update(updateMap = config_dict)

    if sys.platform != 'Pocket PC':
        print 'Attempting to launch web browser after web server....'
        def run_browser():
            import time
            import webbrowser
            time.sleep(1) # Give the server time to start
            webbrowser.open(server_url)
            
        cherrypy.server.start_with_callback(func=run_browser)
    else:
        #import pdb; pdb.set_trace()
        cherrypy.server.start()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
    