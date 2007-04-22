import os
import sys
import glob
from cgi import escape as html_escape

import alc_model

"""
# TODO winner colour should be on screen (part of you can carry on playing problem partly this modeule, partly game engine?)
# TODO losses, two styles:
            what is missing (DONE)
            ALL pieces what is still here (zero count) and missing
"""


#html constants

# http://www.somacon.com/p141.php is a great resource, I ended up hand changing this but as a starting point great!
# <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Strict//EN">
## http://webkit.org/blog/?p=68
html_head='''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <meta content="text/html; charset=ISO-8859-1" 
 http-equiv="content-type">
  <title>alc test board</title>

<style type="text/css">
table.alc_board {
	border-width: 0px 0px 0px 0px;
	border-spacing: 0px;
	border-style: outset outset outset outset;
	border-color: blue blue blue blue;
	border-collapse: separate;
	background-color: black;
}
table.alc_board th {
	border-width: 1px 1px 1px 1px;
	padding: 1px 1px 1px 1px;
	border-style: inset inset inset inset;
	border-color: blue blue blue blue;
	background-color: black;
	-moz-border-radius: 0px 0px 0px 0px;
}
table.alc_board td {
	border-width: 1px 1px 1px 1px;
	padding: 1px 1px 1px 1px;
	border-style: inset inset inset inset;
	border-color: blue blue blue blue;
	background-color: black;
	color: white;
	-moz-border-radius: 0px 0px 0px 0px;
}
div.game_status {
    position:absolute;
    top:0;
    right:0;
	width:150px;
	padding:10px;
	background-color:#eee;
	border:1px dashed #999;
	}
div.game_status2 {
    position:absolute;
    top:100;
    right:0;
	width:150px;
	padding:10px;
	background-color:#eee;
	border:1px dashed #999;
	}
div.player_green {
	width:20px;
	padding:20px;
	background-color:rgb(72, 180, 72);
	border:1px dashed #999;
	}
div.player_red {
	background-color:rgb(180, 72, 72);
	}
body.red {
	background-color:rgb(180, 72, 72);
	}
body.green {
	background-color:rgb(72, 180, 72);
	}

</style>

    <!-- http://www.walterzorn.com/jsgraphics/jsgraphics_e.htm //-->
    <script type="text/javascript" src="wz_jsgraphics.js"></script>
    <script language="javascript" type="text/javascript">
        <!--
            // idea/code from http://24ways.org/2006/writing-responsible-javascript
            
        function addLoadEvent(func) {
            var oldonload = window.onload;
            if (typeof window.onload != 'function') {
                window.onload = func;
            } else {
                window.onload = function() {
                    if (oldonload) {
                        oldonload();
                    }
                    func();
                }
            }
        }        
        //function myFunc(tile_name) {
        function myFunc_test(e) {
            // see http://www.quirksmode.org/js/introevents.html
            var mystr="";
            var targ;
            var centre_cord=[7,5];
            if (!e) var e = window.event;
            if (e.target) targ = e.target;
            else if (e.srcElement) targ = e.srcElement;
            if (targ.nodeType == 3) // defeat Safari bug
                targ = targ.parentNode;            
            alert('myFunc!' + targ ); // targ is;t actually much use....
            //alert('myFunc!' + targ.id ); // doesn't have name :-(
            thing_clicked_name = this.id;
            splitstring = thing_clicked_name.split("_");
            mystr = "(" + splitstring[1] + ", "  + splitstring[2] + ")";
            //the_coords = splitstring.slice(1,2);
            the_coords = splitstring.slice(1);
            alert('myFunc! ' + thing_clicked_name +' ' +mystr +' (' + the_coords + ')'); // name of thing clicked!
            if (e.which) rightclick = (e.which == 3);
            else if (e.button) rightclick = (e.button == 2);
            alert('Rightclick: ' + rightclick); // true or false
            //if ( [7,5] == the_coords ) alert('centre'); // does not work, assume array compare not possible
            if ( centre_cord[0] == the_coords[0] && centre_cord[1] == the_coords[1] ) alert('centre');
            alert(document.getElementById('move_str').value);
            document.getElementById('move_str').value = ' (' + the_coords + ') ';
            //this.src = 'http://127.0.0.1:8088/pieces_46x46/1_laser3.gif'
            // http://www.quirksmode.org/js/strings.html
            // http://fahdi.wordpress.com/title-javascript-check-to-see-if-string-starts-with-ste-or-ste/
            // http://www.oluyede.org/blog/2006/08/16/startswith-and-endswith-in-javascript-15/
            // http://www.quirksmode.org/js/this.html
            // 
        }
        
        normal_visibility = 1;
        selected_visibility = 0.6;
        text_entry_name = 'move_str'; // NOTE at the moment this is generated in cherry_alc.py :-(
        move_form_name = 'move_form'; // NOTE at the moment this is generated in cherry_alc.py :-(
        lastClickCoords = [-1,-1];
        num_rotations = 0;
        orig_rotations = -1;
        orig_image = '';
        var jg = 0; // global canvas/pixel buffer for gfx painting
        var shot_array = %r; // global array of array of array for shot information; filled in from python

        // set_image_visibility -- takes in an IMG tag/id
        // seriously thinking about making this the mechanism for displaying frozen pieces....
        // other option is to simple have 3 player pieces, player one, player two... and frozen player which both 1 and 2 share
        // in amiga alc the frozzen piece is just one solid grey colour (i.e. can't even see mirror side)
        function set_image_visibility(self, visibility)
        {
            if (self.style.MozOpacity)
                self.style.MozOpacity=visibility;
            else if (self.filters)
                self.filters.alpha.opacity=visibility*100;
                // set highlighted border??
        }
        
        // set_image_visibility -- takes in an IMG tag/id
        function set_image_border(self)
        {
            // doesn't appear to work in IE (6)
            // set highlighted border??
            self.border=2; // this is nasty as it relies on the background bage colour, just a place marker hack until can get sorted properly :-(
            //self.border=1; // this is nasty as it relies on the background bage colour, just a place marker hack until can get sorted properly :-(
            // really want it to be yellow (or some definite colour
            // would really like to use the table TD border "thing" to avod re-size
        }
        
        // unset_image_highlighted -- takes in an IMG tag/id
        function unset_image_set_image_border(self)
        {
            // set highlighted border??
            self.border=0; // this is nasty as it relies on the background bage colour, just a place marker hack until can get sorted properly :-(
        }
        
        // set_image_visibility -- takes in an IMG tag/id
        function set_image_highlighted(self)
        {
            set_image_border(self);
            
            set_image_visibility(self, selected_visibility);
        }
        
        // unset_image_highlighted -- takes in an IMG tag/id
        function unset_image_highlighted(self)
        {
            unset_image_set_image_border(self);
            
            set_image_visibility(self, normal_visibility);
        }
        
        function handle_mousewheel(delta) {
            // going to be used as a rotation mechanism
            if (delta < 0)
                rotate_clockwise();
            else
                rotate_anticlockwise();
        }
        // from http://adomas.org/javascript-mouse-wheel/ includes comments        
        /** This is high-level function.
         * It must react to delta being more/less than zero.
         */
        function handle_mousewheel_test(delta) {
            // going to be used as a rotation mechanism
            if (delta < 0)
                alert("delta < 0 ;; DOWN rotated towards bottom of mouse");
            else
                alert("delta >= 0 ;; UP rotated towards top of mouse");
        }
        
        /** Event handler for mouse wheel event.
         */
        function wheel(event){
            var delta = 0;
            if (!event) /* For IE. */
                event = window.event;
            if (event.wheelDelta) { /* IE/Opera. */
                delta = event.wheelDelta/120;
                /** In Opera 9, delta differs in sign as compared to IE.
                 */
                if (window.opera)
                        delta = -delta;
            } else if (event.detail) { /** Mozilla case. */
                /** In Mozilla, sign of delta is different than in IE.
                 * Also, delta is multiple of 3.
                 */
                delta = -event.detail/3;
            }
            /** If delta is nonzero, handle it.
             * Basically, delta is now positive if wheel was scrolled up,
             * and negative, if wheel was scrolled down.
             */
            if (delta)
                handle_mousewheel(delta);
            /** Prevent default actions caused by mouse wheel.
             * That might be ugly, but we handle scrolls somehow
             * anyway, so don't bother here..
             */
            if (event.preventDefault)
                event.preventDefault();
            event.returnValue = false;
        }
        
        function capture_mousewheel(){
            // NOTE does not support Konqueror, OmniWeb, iCab

            if (window.addEventListener)
                /** DOMMouseScroll is for mozilla. */
                window.addEventListener('DOMMouseScroll', wheel, false);
            /** IE/Opera. */
            window.onmousewheel = document.onmousewheel = wheel;
        }
        
        function release_mousewheel(){
            if (window.removeEventListener)
                /** DOMMouseScroll is for mozilla. */
                window.removeEventListener('DOMMouseScroll', wheel, false);
            /** IE/Opera. */
            window.onmousewheel = document.onmousewheel = null;
        }
        
        function reset_move_info()
        {
            if ( lastClickCoords[0] != -1 && lastClickCoords[1] != -1 )
            {
                last_tile = document.getElementById('tile_'+lastClickCoords[0]+'_'+lastClickCoords[1])
                unset_image_highlighted(last_tile);
                last_tile.src = orig_image;
                
                document.getElementById(text_entry_name).value = '';
                lastClickCoords = [-1,-1];
                num_rotations = 0;
                orig_rotations = -1;
                orig_image = '';
                
                release_mousewheel();
            }
        }

        function take_turn(move_str)
        {
            //reset_move_info(); //??
            document.getElementById(text_entry_name).value = move_str;
            document.getElementById(move_form_name).submit();
        }


        // from http://blog.firetree.net/2005/07/04/javascript-find-position/ also see http://www.quirksmode.org/js/findpos.html
        function findPosX(obj) {
            var curleft = 0;
            if (obj.offsetParent) {
                while (1) {
                    curleft+=obj.offsetLeft;
                    if (!obj.offsetParent) {
                        break;
                    }
                    obj=obj.offsetParent;
                }
            } else if (obj.x) {
                curleft+=obj.x;
            }
            return curleft;
        }
        function findPosY(obj) {
            var curtop = 0;
            if (obj.offsetParent) {
                while (1) {
                    curtop+=obj.offsetTop;
                    if (!obj.offsetParent) {
                        break;
                    }
                    obj=obj.offsetParent;
                }
            } else if (obj.y) {
                curtop+=obj.y;
            }
            return curtop;
        }
        
        var shot_colour="blue";
        function draw_shot(drawbuf, direction, tile_x, tile_y) {
            // tile_x, tile_y are board positions/co-ords NOT pixel co-ords
            var tileWidth=0;
            var tileHeight=0; // make these global save on lookup??
            var end_x=0;
            var end_y=0;
            var start_x=0;
            var start_y=0;
            
                        
            temp_piece = document.getElementById('tile_'+tile_x+'_'+tile_y); // use tostring??
            tileWidth=temp_piece.clientWidth;
            tileHeight=temp_piece.clientHeight;
            start_x = findPosX(temp_piece);
            start_y = findPosY(temp_piece);
            
            if ( direction ==  135 || direction ==  315 ) // SOUTH_EAST, NORTH_WEST
            {
                end_x = start_x + tileWidth;
                end_y = start_y + tileHeight;
            }
            if ( direction ==  45 || direction ==  225 ) // NORTH_EAST, SOUTH_WEST
            {
                end_x = start_x;
                start_x = start_x + tileWidth;
                //start_y = start_y ;
                end_y = start_y + tileHeight;
            }
            if ( direction ==  0 || direction ==  180 ) // NORTH, SOUTH
            {
                start_x = start_x + tileWidth/2;
                end_y = start_y + tileHeight;
                end_x = start_x;
            }
            if ( direction ==  90 || direction ==  270 ) // EAST, WEST
            {
                start_y = start_y + tileWidth/2;
                end_y = start_y;
                end_x = start_x + tileWidth;
            }

            drawbuf.setStroke(4); // set width of line
            //drawbuf.setColor("#ff0000"); // red
            //drawbuf.setColor("green");
            drawbuf.setColor(shot_colour);
            drawbuf.drawLine(start_x, start_y, end_x, end_y);
            drawbuf.paint();
        }
        
        function draw_hit(drawbuf, tile_x, tile_y) {
            // tile_x, tile_y are board positions/co-ords NOT pixel co-ords
            var tileWidth=0;
            var tileHeight=0; // make these global save on lookup??
            var end_x=0;
            var end_y=0;
            var start_x=0;
            var start_y=0;
            
                        
            temp_piece = document.getElementById('tile_'+tile_x+'_'+tile_y); // use tostring??
            tileWidth=temp_piece.clientWidth;
            tileHeight=temp_piece.clientHeight;
            start_x = findPosX(temp_piece);
            start_y = findPosY(temp_piece);
            
            //start_x = start_x + tileWidth/2;
            //start_y = start_y + tileWidth/2;
            end_x = tileWidth;
            end_y = tileHeight;
            

            //drawbuf.setStroke(3); // set width of line
            drawbuf.setColor(shot_colour);
            drawbuf.fillEllipse(start_x, start_y, end_x, end_y);
            // TODO consider using fillPolygon or even lots of lines criss-crossed
            drawbuf.paint();
        }
        
        function myFunc(e) {
            // see http://www.quirksmode.org/js/introevents.html
            var mystr="";
            var targ;
            //var jg = new jsGraphics("alc_board"); // see http://www.walterzorn.com/jsgraphics/jsgraphics_e.htm


            thing_clicked_name = this.id;
            
            //temp_clickedpieceinfo = ' parent:' + this.parentNode.nodeName + ' ' + thing_clicked_name + ' pos: ' + findPosX(this).toString() + ', ' + findPosY(this).toString();
            //the_alc_board = document.getElementById("alc_board");
            //temp_boardinfo = ' the_alc_board pos: '  + findPosX(the_alc_board).toString() + ', ' + findPosY(the_alc_board).toString();
            //alert(temp_clickedpieceinfo + ' ** ' + temp_boardinfo );
            
            //temp_piece_tile_0_0 = document.getElementById("tile_0_0");
            //temp_piece_tile_1_1 = document.getElementById("tile_1_1");
            //temp_piece_tile_14_10 = document.getElementById("tile_14_10");
            //start_x = findPosX(temp_piece_tile_0_0);
            //start_y = findPosY(temp_piece_tile_0_0);
            //end_x = findPosX(temp_piece_tile_14_10);
            //end_y = findPosY(temp_piece_tile_14_10);
            //end_x = findPosX(temp_piece_tile_1_1);
            //end_y = findPosY(temp_piece_tile_1_1);
            //end_x = start_x + temp_piece_tile_0_0.clientWidth;
            //end_y = start_y + temp_piece_tile_0_0.clientHeight;
            
            //jg.setStroke(3); // set width of line
            //jg.setColor("#ff0000"); // red
            //jg.drawLine(start_x, start_y, end_x, end_y); // co-ordinates related to the DIV (canvas)
            ////jg.drawLine(10, 113, 220, 55); // co-ordinates related to the DIV (canvas)
            ////jg.fillEllipse(220, 55, 10, 10);  
            
            //jg.setColor("#0000ff"); // blue
            //jg.drawLine(0, 0, 300, 100); // co-ordinates related to the table (canvas)
            //jg.fillEllipse(300, 100, 10, 10);  
            //jg.paint();
            
            //draw_shot(jg, 45, 0, 0);
            //draw_shot(jg, 45, 2, 3);
            //draw_shot(jg, 225, 1, 4);
            
            //draw_shot(jg, 0, 2, 4);
            //draw_shot(jg, 180, 2, 5);
            
            //draw_shot(jg, 90, 2, 7);
            //draw_shot(jg, 270, 1, 7);
            
            //draw_shot(jg, 135, 13, 4);
            //draw_shot(jg, 135, 14, 5);
            
            //draw_hit(jg, 1, 9);
            
            splitstring = thing_clicked_name.split("_");
            mystr = "(" + splitstring[1] + ", "  + splitstring[2] + ")";
            the_coords = splitstring.slice(1);
            //alert('myFunc! ' + thing_clicked_name +' ' +mystr +' (' + the_coords + ')' + this.src); // name of thing clicked!
            if ( lastClickCoords[0] == the_coords[0] && lastClickCoords[1] == the_coords[1] )
            {
                // same tile selected as last time so unselect it
                ////alert('same coords clicked');
                //visibility = normal_visibility;
                //lastClickCoords = [-1,-1];
                //document.getElementById(text_entry_name).value = '';
                reset_move_info();
                jg.clear(); // canvas needs to be globally defined, i.e the same one that was written to!
            }
            else
            {
                last_tile = document.getElementById('tile_'+the_coords[0]+'_'+the_coords[1])
                orig_image = last_tile.src;
                if (document.getElementById(text_entry_name).value == '' || ( lastClickCoords[0] == -1 && lastClickCoords[1] == -1 ))
                {
                    document.getElementById(text_entry_name).value = ' (' + the_coords + ') ';
                    lastClickCoords = the_coords;
                    set_image_highlighted(this);
                    capture_mousewheel();
                }
                else
                {
                    last_tile = document.getElementById('tile_'+lastClickCoords[0]+'_'+lastClickCoords[1])
                    unset_image_highlighted(last_tile);
                    document.getElementById(text_entry_name).value = 'move ' + '(' + lastClickCoords  + ')' + ' (' + the_coords + ')';
                    lastClickCoords = [-1,-1];
                    document.getElementById(move_form_name).submit(); // document.move_form.submit();
                }
            }
            
        }
        
        function pass_turn()
        {
            take_turn('pass');
        }

        function shoot()
        {
            document.getElementById(text_entry_name).value = 'shoot ' + document.getElementById(text_entry_name).value;
            document.getElementById(move_form_name).submit();
        }
        
        function oldrotate()
        {
            //var num_rotations=0;
            var num_rotations=8; // 8 is bad or no rotations depending on how you look at it
            if (num_rotations >= 8)
                num_rotations = num_rotations - 8;
            if (num_rotations == 0)
            {
                alert('back to orig not rotating');
                //last_tile = document.getElementById('tile_'+lastClickCoords[0]+'_'+lastClickCoords[1])
                //visibility = normal_visibility;
                //set_image_visibility(last_tile, visibility);
            }
            else
            {
                //if (num_rotations >= 0 && num_rotations <= 7 ) // maybe too paranoid?
                document.getElementById(text_entry_name).value = 'rotate ' + document.getElementById(text_entry_name).value + ' num_rotations='+num_rotations;
                document.getElementById(move_form_name).submit();
            }
        }
        
        // rotate clock wise one rotation, on-screen only
        function rotate()
        {
            if ( lastClickCoords[0] != -1 && lastClickCoords[1] != -1 )
            {
                num_rotations = num_rotations + 1;
                if (num_rotations >= 8)
                    num_rotations = num_rotations - 8;
                if (num_rotations < 0)
                    num_rotations = num_rotations + 8;
                last_tile = document.getElementById('tile_'+lastClickCoords[0]+'_'+lastClickCoords[1])
                move_str = 'rotate ' + '(' + lastClickCoords + ') '+ ' num_rotations='+num_rotations;
                
                // this.src = 'http://127.0.0.1:8088/pieces_46x46/1_laser3.gif'
                // set rotated image
                bitmap_src = last_tile.src
                if (orig_rotations == -1)
                {
                    //bitmap_src  extract roataion, add num_rotations, round to under 8, insert near end of string
                    //orig_rotations = parseInt(bitmap_src[bitmap_src.length - 5]); // no work in IE :-(
                    //bitmap_src[bitmap_src.length - 5] // fails as "undefined in IE javascript!
                    orig_rotations = parseInt(bitmap_src.charAt(bitmap_src.length - 5));
                }
                
                new_rotation = orig_rotations + num_rotations;
                if (new_rotation >= 8)
                    new_rotation = new_rotation - 8;
                if (new_rotation < 0)
                    new_rotation = new_rotation + 8;
                bitmap_src = bitmap_src.slice(0, bitmap_src.length - 5) + new_rotation.toString() + bitmap_src.slice(bitmap_src.length - 4);
                last_tile.src = bitmap_src;
                // image already selected/highlighted
                document.getElementById(text_entry_name).value = move_str;
            }
        }
        
        // rotate one rotation, on-screen only
        function rotate_any(direction)
        {
            // direction is either +1 or -1, any other value is invalid (not currently note checked/enforced)
            
            if ( lastClickCoords[0] != -1 && lastClickCoords[1] != -1 )
            {
                num_rotations = num_rotations + direction;
                if (num_rotations >= 8)
                    num_rotations = num_rotations - 8;
                if (num_rotations < 0)
                    num_rotations = num_rotations + 8;
                last_tile = document.getElementById('tile_'+lastClickCoords[0]+'_'+lastClickCoords[1])
                move_str = 'rotate ' + '(' + lastClickCoords + ') '+ ' num_rotations='+num_rotations;
                
                // this.src = 'http://127.0.0.1:8088/pieces_46x46/1_laser3.gif'
                // set rotated image
                bitmap_src = last_tile.src
                if (orig_rotations == -1)
                {
                    //bitmap_src  extract roataion, add num_rotations, round to under 8, insert near end of string
                    //orig_rotations = parseInt(bitmap_src[bitmap_src.length - 5]); // no work in IE :-(
                    //bitmap_src[bitmap_src.length - 5] // fails as "undefined in IE javascript!
                    orig_rotations = parseInt(bitmap_src.charAt(bitmap_src.length - 5));
                }
                
                new_rotation = orig_rotations + num_rotations;
                if (new_rotation >= 8)
                    new_rotation = new_rotation - 8;
                if (new_rotation < 0)
                    new_rotation = new_rotation + 8;
                bitmap_src = bitmap_src.slice(0, bitmap_src.length - 5) + new_rotation.toString() + bitmap_src.slice(bitmap_src.length - 4);
                last_tile.src = bitmap_src;
                // image already selected/highlighted
                document.getElementById(text_entry_name).value = move_str;
            }
        }
        
        // rotate clockwise one rotation, on-screen only
        function rotate_clockwise()
        {
            //rotate();
            rotate_any(1);
        }
        
        // rotate anti-clockwise one rotation, on-screen only
        function rotate_anticlockwise()
        {
            rotate_any(-1);
        }
        
        function show_shots() {
            // display shots/hits/explosions (if frozen not actually an explosion) on board, relies on global "shot_array" and "jg" for canvas
            var EFFECTIVE_HIT = -9999; // constant copied from Python source
            for (row=0; row<shot_array.length; row++)
            {
                current_row = shot_array[row];
                for (column=0; column<current_row.length; column++)
                {
                    current_column = current_row[column];
                    if (current_column.length > 0)
                    {
                        for (i=0; i<current_column.length; i++)
                        {
                            shot_info = current_column[i];
                            if (shot_info == EFFECTIVE_HIT)
                                draw_hit(jg, column, row);
                            else
                                draw_shot(jg, shot_info, column, row);
                        }
                    }
                }
            }
            
        }
        function hide_shots() {
            // hide/remove shots that show_shots() displays
            jg.clear();
        }
        
        function debug_show_shots() {
            // test showing some shots with a hard coded array - idealy use json to get ito client but could just place in html/script
            shot_array = [[[], [], [], [], [], [], [], [], [], [], [], [], [], [], []], [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []], [[], [], [], [], [], [], [], [], [] , [], [], [], [], [], []], [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []], [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []], [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []], [[], [90], [90, -9999], [],  [], [], [], [], [], [], [], [], [], [], []], [[], [], [], [], [], [], [], [], [ ], [], [], [], [], [], []], [[], [], [], [], [], [], [], [], [], [], [], [], [],  [], []], [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []], [[], [],  [], [], [], [], [], [], [], [], [], [], [], [], []]];
            
            // alert(shot_array.length);// 11 correct!
            //alert(shot_array[0].length);// 15 correct!
            //alert(shot_array[1].length);//  15 correct!
            //alert(shot_array[6].length);//  15 correct!
            //alert(shot_array[6][0].length);//  0 correct
            //alert(shot_array[6][1].length);// 1 correct
            //alert(shot_array[6][2].length);// 2 correct
            //alert(shot_array[6][3].length);// 0 correct
            //alert(shot_array.length);
            
            for (row=0; row<shot_array.length; row++)
            {
                current_row = shot_array[row];
                //alert(row + ' ' + current_row );
                for (column=0; column<current_row.length; column++)
                {
                    current_column = current_row[column];
                    //alert(column+ ' ' + current_column );
                    if (current_column.length > 0)
                    {
                        //alert('row: ' + row + ' ' + 'col: ' + column + ' ' + current_column + ' ' + current_column.length );
                        for (i=0; i<current_column.length; i++)
                        {
                            shot_info = current_column[i];
                            var EFFECTIVE_HIT = -9999;
                            if (shot_info == EFFECTIVE_HIT)
                            {
                                draw_hit(jg, column, row);
                            }
                            else
                            {
                                draw_shot(jg, shot_info, column, row);
                            }
                        }
                    }
                }
            }
            
            return;
            // couldn't get iteration to work :-(
            for (var row in shot_array ) 
            {
                // array iteration is different to Python  :-( looks like one gets an index not the actual item
                current_row = shot_array[row];
                alert(current_row );
                
                for (var column in current_row )
                {
                    current_column = current_row[column];
                    if (current_column.length > 0)
                    {
                        alert('row: ' + row + ' ' + 'col: ' + column + ' ' + current_column + ' ' + current_column.length );
                    }
                    //for (var shot_info in column )
                    //{
                        
                        //if (shot_info.length > 0)
                        //{
                        //    alert('row: ' + row_num + ' ' + 'col: ' + col_num + ' ' + shot_info+ ' ' + shot_info.length );
                        //}
                    //}
                }
            }
        }
        
        function myInit() {
            //document.getElementById('tile_0_0').onclick = myFunc;
            //document.getElementById('tile_0_1').onclick = myFunc;
            var width=14;
            var height=10;
            jg = new jsGraphics("alc_board"); // see http://www.walterzorn.com/jsgraphics/jsgraphics_e.htm
            for(tempY = 0; tempY <= height; tempY++)
                for(tempX = 0; tempX <= width; tempX++)
                    document.getElementById('tile_'+tempX+'_'+tempY).onclick = myFunc;
        }
        
        // main
        addLoadEvent(myInit);
        addLoadEvent(show_shots);
        //addLoadEvent(capture_mousewheel);
        //-->
    </script>
    
</head>
<body class="%s">
'''

table_head='''
<div>
<table id="alc_board" class="alc_board" style="width: %dpx; height: %dpx;" >
  <tbody>
'''
## <body bgcolor="#ff0000">
## note firefox won't honour RGB but IE does!: <body bgcolor="rgb(255,0,0)">
## from http://www.thescripts.com/forum/thread148875.html, "rgb(...)" is allowed in CSS only.


table_tail='''
  </tbody>
</table>
</div>
'''

html_tail='''
<br>

<div class="game_status">
Round: %d<br>
Player Turn: %s<br>
Moves Left: <div class="player_%s">%d</div>
</div>

    <a id="show_last_shots" onclick="show_shots();">show_shots</a>
    <a id="clear_last_shots" onclick="hide_shots()();">clear_shots</a>
    <a id="hide_last_shots" onclick="jg.clear();">clear_shots</a>

</body>
</html>
'''


def html_boardV1(board, fileptr, piece_dirname=None, tile_xlen=None, tile_ylen=None, dumb_str=None):
    """Dumb diagnostic, dumps to fileptr
    Does not handle checker board pattern like original alc, 
    uses single colour like laserchess.org
    """
    if dumb_str is None:
        dumb_str=''
    if piece_dirname is None:
        piece_dirname ="pieces_%dx%d" % (46, 46)
    
    # determine bitmap type (note pattern much match pattern in tile_fname_pat
    #imagefile_type='.gif'
    #imagefile_type='.png'
    temp_filematch_str=os.path.join(piece_dirname, '1_king0*')
    imagefile_type=glob.glob(temp_filematch_str)[0][len(temp_filematch_str)-1:]
    tile_fname_pat = '%d_%s%d'+imagefile_type
    print tile_fname_pat 
    #tile_fname_pat = os.path.join(piece_dirname, tile_fname_pat)
    tile_fname_pat = piece_dirname +'/'+ tile_fname_pat
    
    if tile_xlen is None or tile_ylen is None:
        # if either is missing default (or determine?) size
        #tile_xlen = 18
        #tile_ylen = 18
        tile_xlen = 46
        tile_ylen = 46
        
        try:
            temp_file=open(os.path.join(piece_dirname, 'size.txt'))
            temp_size_str = temp_file.readline()
            temp_file.close()
            try:
                tile_xlen, tile_ylen = tuple(map(int, temp_size_str.split('x')))
            except ValueError:
                pass
        except IOError, info:
            if info.errno==2:
                # does not exist
                pass
            else:
                raise

    fileptr.write(html_head % (board.shootboard, alc_model.player_map[board.current_player][0]) )
    if alc_model.debug:
        fileptr.write('<div><h2>WARNING debug mode, random is not random!</h2></div>' )
    if board.winner is not None:
        do_nasty_blink=True
        fileptr.write('<div><h1>')
        if do_nasty_blink:
            fileptr.write('<blink>')
        fileptr.write('Game Over! Winner: '+ str(board.winner))
        if do_nasty_blink:
            fileptr.write('</blink>')
        fileptr.write('</h1></div>')

    fileptr.write(table_head % (tile_xlen, tile_ylen) )
    show_side_display_numbers = True
    row_count=0
    for temp_row in board.board:
        fileptr.write('''<tr>''')
        col_count=0
        if show_side_display_numbers:
            fileptr.write('''<td>%d</td>\n''' % (row_count) )
        for temp_col in temp_row:
            piece_position = (col_count, row_count)
            if temp_col is None:
               tile_fname = tile_fname_pat % (1, 'blank', 0)
            else:
                #print temp_col.piece_name()
                try:
                   temp_rotation = temp_col.rotation
                except AttributeError, info:
                   temp_rotation = 0
                if isinstance(temp_col, alc_model.player_piece):
                    player_number = temp_col.player_number
                    if temp_col.frozen:
                        player_number = 9
                    tile_fname = tile_fname_pat % (player_number, temp_col.piece_name(), alc_model.direction_to_order[temp_rotation])
                elif isinstance(temp_col, alc_model.hole_square) or isinstance(temp_col, alc_model.warp_piece):
                    tile_fname = tile_fname_pat % (1, temp_col.piece_name(), alc_model.direction_to_order[temp_rotation])
                else:
                    #tile_fname = 'missing.gif'
                    tile_fname = 'missing' + imagefile_type
            #if col_count >= board.board_size[0]/2:
            #   tile_fname = 'green_' + tile_fname

            #fileptr.write('''<td><img style="width: %dpx; height: %dpx;" alt="" src="./%s" title="%r"></td>\n''' % (tile_xlen, tile_ylen, tile_fname, piece_position) )
            #fileptr.write('''<td><a href="http://google.com"><img style="width: %dpx; height: %dpx;" alt="" src="./%s" title="%r"></a></td>\n''' % (tile_xlen, tile_ylen, tile_fname, piece_position) )
            #fileptr.write('''<td><a id="tile_%d_%d"><img style="width: %dpx; height: %dpx;" alt="" src="./%s" title="%r"></a></td>\n''' % (piece_position[0], piece_position[1], tile_xlen, tile_ylen, tile_fname, piece_position) ) ## WORKS!
            #fileptr.write('''<td><img id="tile_%d_%d" style="width: %dpx; height: %dpx;" alt="" src="./%s" title="%r"></td>\n''' % (piece_position[0], piece_position[1], tile_xlen, tile_ylen, tile_fname, piece_position) ) ## also works, no need for <a>
            fileptr.write('''<td><img id="tile_%d_%d" style="filter:alpha(opacity=100);-moz-opacity:1; width: %dpx; height: %dpx;" alt="" src="./%s" title="%r"></td>\n''' % (piece_position[0], piece_position[1], tile_xlen, tile_ylen, tile_fname, piece_position) ) ## test opacity
            # one idea is that select piece will actually change border-colour and frozen pieces changes opacity in html
            # other option is to simple have 3 player pieces, player one, player two... and frozen player which both 1 and 2 share
            # in amiga alc the frozzen piece is just one solid grey colour (i.e. can't even see mirror side) -- probably the one to do
            col_count += 1
        fileptr.write('''</tr>\n\n''')
        row_count+=1
    if show_side_display_numbers:
        fileptr.write('''<tr>''')
        fileptr.write('''<td></td>\n''')
        for temp_col_count in xrange(col_count):
            fileptr.write('''<td>%d</td>\n''' % (temp_col_count) )
        fileptr.write('''</tr>\n\n''')
    fileptr.write(table_tail)
    fileptr.write(dumb_str)
    fileptr.write(html_tail % (board.rounds_played+1, alc_model.player_map[board.current_player][0], alc_model.player_map[board.current_player][0], board.turns_left) )


def determine_tiles(piece_dirname=None, tile_xlen=None, tile_ylen=None):
    """work out where to get tiles from"""
    if piece_dirname is None:
        piece_dirname ="pieces_%dx%d" % (46, 46)
    
    # determine bitmap type (note pattern much match pattern in tile_fname_pat
    #imagefile_type='.gif'
    #imagefile_type='.png'
    temp_filematch_str=os.path.join(piece_dirname, '1_king0*')
    imagefile_type=glob.glob(temp_filematch_str)[0][len(temp_filematch_str)-1:]
    tile_fname_pat = '%d_%s%d'+imagefile_type
    print tile_fname_pat 
    #tile_fname_pat = os.path.join(piece_dirname, tile_fname_pat)
    tile_fname_pat = piece_dirname +'/'+ tile_fname_pat
    
    if tile_xlen is None or tile_ylen is None:
        # if either is missing default (or determine?) size
        #tile_xlen = 18
        #tile_ylen = 18
        tile_xlen = 46
        tile_ylen = 46
        
        try:
            temp_file=open(os.path.join(piece_dirname, 'size.txt'))
            temp_size_str = temp_file.readline()
            temp_file.close()
            try:
                tile_xlen, tile_ylen = tuple(map(int, temp_size_str.split('x')))
            except ValueError:
                pass
        except IOError, info:
            if info.errno==2:
                # does not exist
                pass
            else:
                raise
        
    return (piece_dirname, tile_xlen, tile_ylen, tile_fname_pat)

def html_determine_tiles(piece_dirname=None, tile_xlen=None, tile_ylen=None):
    """work out where to get tiles from"""
    if piece_dirname is None:
        piece_dirname ="pieces_%dx%d" % (46, 46)
    
    # determine bitmap type (note pattern much match pattern in tile_fname_pat
    #imagefile_type='.gif'
    #imagefile_type='.png'
    temp_filematch_str=os.path.join(piece_dirname, '1_king0*')
    imagefile_type=glob.glob(temp_filematch_str)[0][len(temp_filematch_str)-1:]
    tile_fname_pat = '%d_%s%d'+imagefile_type
    print tile_fname_pat 
    #tile_fname_pat = os.path.join(piece_dirname, tile_fname_pat)
    tile_fname_pat = piece_dirname +'/'+ tile_fname_pat
    
    if tile_xlen is None or tile_ylen is None:
        # if either is missing default (or determine?) size
        #tile_xlen = 18
        #tile_ylen = 18
        tile_xlen = 46
        tile_ylen = 46
        
        try:
            temp_file=open(os.path.join(piece_dirname, 'size.txt'))
            temp_size_str = temp_file.readline()
            temp_file.close()
            try:
                tile_xlen, tile_ylen = tuple(map(int, temp_size_str.split('x')))
            except ValueError:
                pass
        except IOError, info:
            if info.errno==2:
                # does not exist
                pass
            else:
                raise
        
    return (tile_fname_pat, tile_xlen, tile_ylen)


def html_boardV2(board, fileptr, piece_dirname=None, tile_xlen=None, tile_ylen=None, dumb_str=None):
    """
    Performance statistics:
        Page size: 58.69KB
        
        0.016s
        0.031s
    """
    tile_fname_pat, tile_xlen, tile_ylen = html_determine_tiles(piece_dirname=piece_dirname, tile_xlen=tile_xlen, tile_ylen=tile_ylen)
    
    fileptr.write(html_head % (board.shootboard, alc_model.player_map[board.current_player][0]) )
    if alc_model.debug:
        fileptr.write('<div><h2>WARNING debug mode, random is not random!</h2></div>' )
    if board.winner is not None:
        do_nasty_blink=True
        fileptr.write('<div><h1>')
        if do_nasty_blink:
            fileptr.write('<blink>')
        fileptr.write('Game Over! Winner: '+ str(board.winner))
        if do_nasty_blink:
            fileptr.write('</blink>')
        fileptr.write('</h1></div>')

    fileptr.write(table_head % (tile_xlen, tile_ylen) )
    show_side_display_numbers = True
    row_count=0
    for temp_row in board.board:
        fileptr.write('''<tr>''')
        col_count=0
        if show_side_display_numbers:
            fileptr.write('''<td>%d</td>\n''' % (row_count) )
        for temp_col in temp_row:
            piece_position = (col_count, row_count)
            if temp_col is None:
               tile_fname = tile_fname_pat % (1, 'blank', 0)
            else:
                try:
                   temp_rotation = temp_col.rotation
                except AttributeError, info:
                   temp_rotation = 0
                if isinstance(temp_col, alc_model.player_piece):
                    player_number = temp_col.player_number
                    if temp_col.frozen:
                        player_number = 9
                    tile_fname = tile_fname_pat % (player_number, temp_col.piece_name(), alc_model.direction_to_order[temp_rotation])
                elif isinstance(temp_col, alc_model.hole_square) or isinstance(temp_col, alc_model.warp_piece):
                    tile_fname = tile_fname_pat % (1, temp_col.piece_name(), alc_model.direction_to_order[temp_rotation])
                else:
                    #tile_fname = 'missing.gif'
                    tile_fname = 'missing' + imagefile_type
            fileptr.write('''<td><img id="tile_%d_%d" style="filter:alpha(opacity=100);-moz-opacity:1; width: %dpx; height: %dpx;" alt="" src="./%s" title="%r"></td>\n''' % (piece_position[0], piece_position[1], tile_xlen, tile_ylen, tile_fname, piece_position) ) ## test opacity
            # one idea is that select piece will actually change border-colour and frozen pieces changes opacity in html
            # other option is to simple have 3 player pieces, player one, player two... and frozen player which both 1 and 2 share
            # in amiga alc the frozen piece is just one solid grey colour (i.e. can't even see mirror side) -- probably the one to do
            col_count += 1
        fileptr.write('''</tr>\n\n''')
        row_count+=1
    if show_side_display_numbers:
        fileptr.write('''<tr>''')
        fileptr.write('''<td></td>\n''')
        for temp_col_count in xrange(col_count):
            fileptr.write('''<td>%d</td>\n''' % (temp_col_count) )
        fileptr.write('''</tr>\n\n''')
    fileptr.write(table_tail)
    fileptr.write(dumb_str)
    fileptr.write(html_tail % (board.rounds_played+1, alc_model.player_map[board.current_player][0], alc_model.player_map[board.current_player][0], board.turns_left) )

def html_boardV3(board, fileptr, piece_dirname=None, tile_xlen=None, tile_ylen=None, error_text=None):
    """
    Performance statistics:
            Page size: 60.85KB
            0.047s
            0.062s
    """
    piece_dirname, tile_xlen, tile_ylen, tile_fname_pat = determine_tiles(piece_dirname=piece_dirname, tile_xlen=tile_xlen, tile_ylen=tile_ylen)
    
    from html2template import Template

    template_file_name = 'test_template.html'
    template_file_name = 'template_alc.html'
    if os.path.exists(template_file_name):
        template_file = open(template_file_name, 'r')
        template_content = template_file.read()
        template_file.close()
    else:
        raise NotImplementedError ('mising template file: ' + template_file_name)
    
    def renderMain(template, debug_info, game_winner, bodyclass, alc_board_style, round_num, player_turn, moves_left, moves_left_classname, error_info, piece_pictures, the_board, shot_info):
        """Renders the template.
            bodyclass : string -- class/css style name for body
            alc_board_style: string -- width stlye string for table
            round_num: int or string number of current round
            player_turn: int or string number of current player
            moves_left: int or string number of moves left
            
            Result : string -- the finished HTML
        """
        node = template.copy()
        topnode = node

        #print node._RichContent__nodesDict
        node.bodyclass.atts['class'] = bodyclass ##  node="con:bodyclass" -- if you set body atributes, the body value is emptied, which is the template!
        node = node.bodyclass
        #node.alc_board.atts['style'] = alc_board_style ##  node="con:alc_board" # if set rows break
        
        if debug_info:
            #node.debug_info.val = 'WARNING debug mode, random is not random!'
            node.debug_info.text = 'WARNING debug mode, random is not random!'
        else:
            # FIXME make this cleaner/suck less
            # kinda dumb but sort of works, reset
            #node.debug_info.val = ''
            node.debug_info.text = ''
        #node.game_winner.val = game_winner
        #node.game_winner.text = game_winner ## <div><h1><blink node="con:game_winner">Game Over! Winner: player info</blink></h1></div>
        node.game_winner.html = '<h1><blink>' + html_escape(game_winner) + '</blink></h1>'
        
        #node.round_num.val= str(round_num)
        node.round_num.text= str(round_num)
        #node.player_turn.val= str(player_turn)
        node.player_turn.text= str(player_turn)
        
        node.moves_left.atts['class'] = moves_left_classname
        #node.moves_left.val= str(moves_left)
        node.moves_left.text= str(moves_left)
        
        #node.error_info.val= error_info
        node.error_info.text= error_info
        node.piece_pictures.atts['value'] = piece_pictures
        
        node.shot_info.atts['value'] = shot_info # pretty savage and an abuse.... :-(
        #node.shot_info.val = '' # reset
        node.shot_info.text = '' # reset
        
        node.table_rows.repeat(renderCols, the_board)
        
        return topnode.render()
    def renderCols(node, the_cols):
        """Callback function used by render().
            node : Repeater -- the copy of the rep:item node to manipulate
            the_cols: list of col info
        """
        node.table_cols.repeat(renderCell, the_cols)
    def renderCell(node, the_cell):
        """Callback function used by render().
            node : Repeater -- the copy of the rep:item node to manipulate
            the_cell: tuplet
        """
        ## <img node="con:single_table_cell" id="tile_%d_%d" style="filter:alpha(opacity=100);-moz-opacity:1; width: %dpx; height: %dpx;" alt="" src="./%s" title="%r"/>
        ## <img node="con:single_table_cell" src="./pieces_46x46/1_laser2.gif" style="filter:alpha(opacity=100);-moz-opacity:1; width: 46px; height: 46px;" title="(0, 4)" alt="" id="tile_0_4" />
        cell_id, cell_style, cell_src, cell_title =the_cell
        node.single_table_cell.atts['id'] = cell_id
        node.single_table_cell.atts['style'] = cell_style
        node.single_table_cell.atts['src'] = cell_src
        node.single_table_cell.atts['title'] = cell_title

    
    template = Template(template_content)
    
    ## this logic could/should be moved into renderMain()
    debug_info = alc_model.debug
    game_winner = ''
    if board.winner is not None:
        #game_winner = 'Game Over! Winner: '+ str(board.winner)
        winner_colour = alc_model.player_map[board.winner][0]  # get player colour name
        game_winner = 'Game Over! Winner: '+ winner_colour.capitalize()
        current_player = winner_colour
    else:
        # overloading variable usage :-(
        current_player = alc_model.player_map[board.current_player][0]
    alc_board_style="width: %dpx; height: %dpx;" % (tile_xlen, tile_ylen)
    current_round = board.rounds_played+1
    turns_left = board.turns_left
    moves_left_classname="player_%s" % current_player ## string; green or red
    error_info=error_text
    if error_info is None:
        error_info="PASSME IN!!"
    piece_pictures=piece_dirname ##             
    
    shot_info = '%r' % board.shootboard ## this is basically a Python to JSON string call
    
    the_board = []
    show_side_display_numbers = False
    show_side_display_numbers = True
    row_count=0
    for temp_row in board.board:
        col_count=0
        the_temp_row=[]
        if show_side_display_numbers:
            pass
            #fileptr.write('''<td>%d</td>\n''' % (row_count) )
        for temp_col in temp_row:
            piece_position = (col_count, row_count)
            if temp_col is None:
               tile_fname = tile_fname_pat % (1, 'blank', 0)
            else:
                try:
                   temp_rotation = temp_col.rotation
                except AttributeError, info:
                   temp_rotation = 0
                if isinstance(temp_col, alc_model.player_piece):
                    player_number = temp_col.player_number
                    if temp_col.frozen:
                        player_number = 9
                    tile_fname = tile_fname_pat % (player_number, temp_col.piece_name(), alc_model.direction_to_order[temp_rotation])
                elif isinstance(temp_col, alc_model.hole_square) or isinstance(temp_col, alc_model.warp_piece):
                    tile_fname = tile_fname_pat % (1, temp_col.piece_name(), alc_model.direction_to_order[temp_rotation])
                else:
                    #tile_fname = 'missing.gif'
                    tile_fname = 'missing' + imagefile_type
            the_temp_row.append( (
                'tile_%d_%d' % (piece_position[0], piece_position[1]),
                'filter:alpha(opacity=100);-moz-opacity:1; width: %dpx; height: %dpx;' % (tile_xlen, tile_ylen),
                './%s' % (tile_fname,),
                '%r' % (piece_position,)
                )
            )
            col_count += 1
        row_count+=1
        the_board.append(the_temp_row)
    if show_side_display_numbers:
        pass
        # don't think this is possible with the template system used
        #for temp_col_count in xrange(col_count):
        #    fileptr.write('''<td>%d</td>\n''' % (temp_col_count) )
        
    
    fileptr.write(renderMain(template, debug_info, game_winner, current_player, alc_board_style, current_round, current_player, turns_left, moves_left_classname, error_info, piece_pictures, the_board, shot_info))


html_board = html_boardV1
html_board = html_boardV2
html_board = html_boardV3

def html_losses(board, fileptr, piece_dirname=None, tile_xlen=None, tile_ylen=None):
    """Dumb losses information, dumps to fileptr"""
    print ' == TEST losses =='
    print html_determine_tiles(piece_dirname=piece_dirname, tile_xlen=tile_xlen, tile_ylen=tile_ylen)
    tile_fname_pat, tile_xlen, tile_ylen = html_determine_tiles(piece_dirname=piece_dirname, tile_xlen=tile_xlen, tile_ylen=tile_ylen)
    fileptr.write('''
<table>
  <tbody>
''')
    
    for player_number in board.lost_pieces:
        print 'Player', player_number
        for piece_name in board.lost_pieces[player_number]:
            if board.lost_pieces[player_number][piece_name] !=0:
                print '    ', piece_name, board.lost_pieces[player_number][piece_name]
                image_name = piece_name.replace('_piece', '')
                tile_fname = tile_fname_pat % (player_number, image_name, 0)
                fileptr.write('''<tr>''')
                fileptr.write('''<td><img style="width: %dpx; height: %dpx;" alt="" src="./%s"></td>\n''' % (tile_xlen, tile_ylen, tile_fname) )
                fileptr.write('''<td>%d</td>''' % board.lost_pieces[player_number][piece_name])
                fileptr.write('''</tr>''')
                fileptr.write('\n')
        print ''
    fileptr.write('''
  </tbody>
</table>
''')


if __name__ == '__main__':
    playing_board = alc_model.board()
    print playing_board.random_position()
    print playing_board.random_position()
    print playing_board.random_position()
    print playing_board.random_position()
    
    test_moves_type='move into holes and warps'
    #test_moves_type='test attempt to transport with same piece twice'
    #test_moves_type='test attempt to attack with same piece twice'
    #test_moves_type='take king'
    #test_moves_type='king attacks hole'
    if test_moves_type == 'nunch f stuff':
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_ROTATE, origin_coords=(8,7), new_direction=alc_model.SOUTH_EAST)) # bad, move blank
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_ROTATE, origin_coords=(7,7), new_direction=alc_model.SOUTH_EAST)) # bad, move warp
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_ROTATE, origin_coords=(14,4), new_direction=alc_model.NORTH)) # move wrong player piece
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_ROTATE, origin_coords=(0,4), new_direction=alc_model.NORTH))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_ROTATE, origin_coords=(0,6), new_direction=alc_model.SOUTH_EAST))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_ROTATE, origin_coords=(1,8), new_direction=alc_model.SOUTH_EAST))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_ROTATE, origin_coords=(14,4), new_direction=alc_model.NORTH))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(12,5), dest_coords=(11,5)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(13,3), dest_coords=(13,2))) # valid move, transport own piece - needs to be implemented!
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(12,3), dest_coords=(12,4))) # valid move, taking own piece - needs to be implemented!
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(14,4), dest_coords=(14,3))) ## bad move hemmed in and not a taking piece
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(13,2), dest_coords=(9,2))) ## bad move too far
        
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(2,5), dest_coords=(3,5))) # bad, wrong piece Red
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_SHOOT, origin_coords=(0,4)))
        
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(2,5), dest_coords=(3,5)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(3,5), dest_coords=(4,5))) ## take (random transported) piece!
    elif test_moves_type == 'move into holes and warps':
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(2,5), dest_coords=(3,5)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(3,5), dest_coords=(4,5)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(4,5), dest_coords=(5,5)))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(12,5), dest_coords=(11,5)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(11,5), dest_coords=(10,5)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(10,5), dest_coords=(9,5)))
    
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(5,5), dest_coords=(6,5)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
    
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(9,5), dest_coords=(8,5)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
    
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(2,3), dest_coords=(3,3)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(3,3), dest_coords=(4,3)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(4,3), dest_coords=(5,3)))
    
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(12,3), dest_coords=(11,3)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(11,3), dest_coords=(10,3)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(10,3), dest_coords=(9,3)))
    
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(5,3), dest_coords=(6,3)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
    
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(9,3), dest_coords=(8,3)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
    
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(6,5), dest_coords=(7,5))) ## move onto warp
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(6,3), dest_coords=(7,3))) ## move onto hole
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(8,5), dest_coords=(7,5))) ## move onto warp
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(8,3), dest_coords=(7,3))) ## move onto hole
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(3,5), dest_coords=(4,5)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(4,5), dest_coords=(5,5)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(5,5), dest_coords=(6,5)))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(2,4), dest_coords=(3,4)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(3,4), dest_coords=(4,4)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(4,4), dest_coords=(5,4)))

        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))

        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(5,4), dest_coords=(6,4)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))

        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(6,5), dest_coords=(6,4))) # take piece
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(6,4), dest_coords=(7,4))) # move right
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(7,4), dest_coords=(7,3))) # move to hole
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(7,4), dest_coords=(7,5))) # move to warp
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(13,3), dest_coords=(12,3)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(12,3), dest_coords=(11,3)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(11,3), dest_coords=(10,3)))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(10,3), dest_coords=(9,3)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(9,3), dest_coords=(8,3)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(8,3), dest_coords=(8,4)))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(8,4), dest_coords=(7,4)))
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(7,4), dest_coords=(7,3))) # move to hole
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(7,4), dest_coords=(7,5))) # move to warp

    elif test_moves_type == 'test attempt to transport with same piece twice':
        # red
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        # Green
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(13,3), dest_coords=(13,2))) # valid move, transport own piece - needs to be implemented!
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(13,2), dest_coords=(13,1))) # invalid move, already transported once transport own piece - needs to be implemented!
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(13,2), dest_coords=(13,1))) # valid move, transport own piece - needs to be implemented!
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(13,1), dest_coords=(13,2))) # empty square move
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(13,2), dest_coords=(14,2))) # bad attempt to transport twice
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(13,1), dest_coords=(13,0))) # transport own piece - needs to be implemented!
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(13,0), dest_coords=(14,0))) # invalid duplicate transport own piece - needs to be implemented!
        
    elif test_moves_type == 'test attempt to attack with same piece twice':
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(2,5), dest_coords=(2,4)))
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(2,4), dest_coords=(2,3))) # bad 2nd attempt
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(2,4), dest_coords=(2,3))) 
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(2,3), dest_coords=(3,3))) 
    elif test_moves_type == 'take king':
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(2,5), dest_coords=(1,5)))
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(1,5), dest_coords=(0,5)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(1,5), dest_coords=(0,5)))
    elif test_moves_type == 'king attacks hole':
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(2,5), dest_coords=(1,5)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))

        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(1,5), dest_coords=(1,6)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(0,5), dest_coords=(1,5)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(1,5), dest_coords=(2,5)))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(2,5), dest_coords=(3,5)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(3,5), dest_coords=(4,5)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(4,5), dest_coords=(5,5)))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(5,5), dest_coords=(6,5)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(6,5), dest_coords=(6,4)))
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(6,4), dest_coords=(7,4)))
        
        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_PASS))

        playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(7,4), dest_coords=(7,3))) # move king to hole and die!
        #playing_board.enter_move(alc_model.piece_move(move_type=alc_model.MOVE_MOVEMENT, origin_coords=(7,4), dest_coords=(7,5))) # move to warp


    playing_board.print_board()
    playing_board.losess()
    
    dumb_str=''
    dumb_str='<div><p>Error place holder<p>enter in move</div>'
    dumb_str='Error place holder'
    
    htmlfilename = '\\Storage Card\\alc\\test.html'
    htmlfilename = 'ltest.html'
    htmlfile = sys.stdout
    htmlfile = open(htmlfilename, 'w')
    
    pieces_location=None
    pieces_location='pieces_18x18'
    pieces_location='pieces_46x46'
    #html_board(playing_board, htmlfile)
    #html_boardV2(playing_board, htmlfile, piece_dirname=pieces_location, dumb_str=dumb_str)
    html_board(playing_board, htmlfile, piece_dirname=pieces_location, error_text=dumb_str)
    htmlfile.close()

    htmlfilename = 'lossestest.html'
    htmlfile = open(htmlfilename, 'w')
    html_losses(playing_board, htmlfile, piece_dirname=pieces_location)
    htmlfile.close()

