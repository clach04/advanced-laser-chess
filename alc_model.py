"""Advanced Laser Chess Model
shutterstock.com

## destroying pieces that are shot - 
##      need to mark for destroy at end of all shooting then destroy at end,
##      e.g. piece shot and dstryed but what about it prism hit first and
##      that hits reflective side of same piece on another hangle that sends it back
## TODO move multiple spaces (if allowed)
## TODO remove stdout "print" calls
## TODO in laser shot info, display laser/freezer type (by colours?)
## TODO shooters -- need to support beams that only go half way across a tile/space
## TODO freezer/frozen pieces (unfreeze after random time, frozen items also need to be removed from list if taken), add to freezer.shot_effect() and enter_move() for unfreezing
## TODO centre board pieces, Warp and Holes, random (dis-)appearance!
## TODO game state load/save - could use xml pickle thing as used in kpg project as it is quick to use but doesn't allow board editing as easily as a simple plain text file
## TODO game move logging/saving/replaying
##      need to save random info as part of move, ideally random could pick up random value from replay log
##      - or just save the init value to random at begiinging pick it up from sys time and save to log
## TODO html show losses in a DIV and toggle visibility - seperate function/window or even google portlet style gadget
## TODO html show shots in a transparent DIV and toggle visibility
"""

import sys
import random

if sys.version == '2.1':
    # old Python version, probably Jython!
    # emulate newstyle class defs (don't get benefits but syntax works)
    # not sure this will work but hey worth a try ;-)
    class object:
        pass

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

debug = True
debug = False
if main_is_frozen():
    debug = False

class ALC_Exception(Exception):
    """Base alc exception, probably redundant"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        # could return expr()
        #return self.value
        return repr(self.value)

class InvalidMove(ALC_Exception):
    pass
class ALCNotImplemented(ALC_Exception):
    pass
class Winner(ALC_Exception):
    pass


# TODO decide if board co-ordinates start at 0 (zero), like lists or 1 (one)

# constants for direction/rotatation
NORTH=0
NORTH_EAST=NORTH+45
EAST=NORTH_EAST+45
SOUTH_EAST=EAST+45
SOUTH=SOUTH_EAST+45
SOUTH_WEST=SOUTH+45
WEST=SOUTH_WEST+45
NORTH_WEST=WEST+45
EFFECTIVE_HIT=-9999 # magic value :-(

# bunch of look up tables to (hopefully) save on math for Snell's law;
# i.e. using angle of incidence, to calculate angle of reflection. 
DIRECTION_ORDER = [NORTH, NORTH_EAST, EAST, SOUTH_EAST, SOUTH, SOUTH_WEST, WEST, NORTH_WEST]
DIRECTION_ORDER_STR = ['NORTH', 'NORTH_EAST', 'EAST', 'SOUTH_EAST', 'SOUTH', 'SOUTH_WEST', 'WEST', 'NORTH_WEST']
direction_to_string = dict(zip(DIRECTION_ORDER, DIRECTION_ORDER_STR ) )
string_to_direction = dict(zip(DIRECTION_ORDER_STR, DIRECTION_ORDER ) )
direction_to_order = dict(zip(DIRECTION_ORDER, range(len(DIRECTION_ORDER)) ) )
order_to_direction = dict(zip(range(len(DIRECTION_ORDER)), DIRECTION_ORDER) )

# direction to (x,y) vector mapping
DIRECTION_VECTORS = {
                    NORTH : (0,-1), 
                    NORTH_EAST : (1,-1), 
                    EAST : (1,0), 
                    SOUTH_EAST : (1,1), 
                    SOUTH : (0,1), 
                    SOUTH_WEST : (-1,1), 
                    WEST : (-1,0), 
                    NORTH_WEST : (-1,-1)
                    }
def ORIGnormalize_angle(x):
    if x >= 360:
        x -= 360
    if x < 0:
        x += 360
    return x
    
def normalize_angle(x):
    while x >= 360:
        x -= 360
    while x < 0:
        x += 360
    return x
    
def calculate_reverse_beam_direction_v1(in_direction):
    # also the side of piece hit
    # calculate opposite/reverse direction
    temp_q = direction_to_order[in_direction]
    temp_q += 4
    if temp_q >= len( direction_to_order):
        temp_q = temp_q - len( direction_to_order)
    
    return order_to_direction[temp_q]

def calculate_reverse_beam_direction_v2(in_direction):
    # also the side of piece hit
    # calculate opposite/reverse direction
    temp_q = in_direction + 180
    temp_q = normalize_angle(temp_q)
    
    return temp_q
    
calculate_reverse_beam_direction=calculate_reverse_beam_direction_v2


class board_piece(object):
    """main super class for any board piece"""
    """
    def __init__(self):
        pass
    """
    def __init__(self, position):
        self.position=position # position/co-ordinate on board. Tuple (x,y)
    
    def piece_name(self):
        #return self.__class__.__name__
        #return self.__class__.__name__
        tmp_str = self.__class__.__name__
        tmp_str=tmp_str.replace('_piece', '')
        return tmp_str 

    def shoot(self, *args, **kwargs):
        raise InvalidMove('%s piece can not shoot' % (self.__class__.__name__,) )
'''
    def defend_move(self, attacking_piece, board):
        """TODO work out what if anything is returned
        Peforms any operations that need to be made, return True is attached was defeated
        Used by "holes" in board, along with centrally located Warp transporter
        to modify location/destroyed status of moving/attacking piece
        """
        
    def defend_shot(self, attacking_piece, board, angle_of_hit):
        """returns if successfully defended being shot at angle_of_hit
        where angle_of_hit is simply the same type as self.rotation
        and attacking_piece the shooter, can be called to determine what sort of shooter and for shooting rules.
        TODO for transporters, defusers and maybe "hole" squares, propigate laser
        """
        # considered "shot_type" as param but this is not part of ALC rules
        return False # default is to fail to defend
'''

# TODO need a class/function to mix in that calculates angles

class taking_piece(object):
    """A piece that can take a (player) piece
    MUST be inherited WITH real board piece type as this 
    class accesses player_piece attributes!
    """
    can_move_onto_playerpiece=True ## can piece move onto squares containing other pieces?

    def take_piece(self, new_position, board):
        """actually take a piece, assumes OK to take piece (i.e. taking a player_piece and not a hole_piece)
        does NOT perform move
        ## TODO only accept piece and board as params and avoid piece lookup.?
        look to re-use take_piece() for hole_piece in defend()?
        set dest to blank_square? sort of a no-op for tking/stomper as they then set their own piece there
        """
        self.check_valid_move(new_position, board) # probably over-kill but sanity checks may not hurt :-)
        piece_at_destination = board.get_board_piece(new_position)
        if self.special_used == True:
            # should not get here as player_piece.check_valid_move() makes this check and it would have failed earlier.
            raise InvalidMove('this piece has already taken this turn')
        self.special_used=True
        board.destroy(piece_at_destination)
        ##board.pieces_changed_this_turn.append() ## FIXME
        board.pieces_to_reset_after_this_turn.append(self)
    
    def perform_move(self, new_position, board):
        """move player piece, can and will take player pieces in destination!
        """
        self.check_valid_move(new_position, board)
        piece_at_destination = board.get_board_piece(new_position)
        if is_a_blank_square(piece_at_destination):
            pass # handled later on, this is bad form but refactor later
        elif isinstance(piece_at_destination, player_piece):
            self.take_piece(new_position, board)
        else:
            if hasattr(piece_at_destination, 'defend_move'):
                if piece_at_destination.defend_move(self, board):
                    return
            elif isinstance(piece_at_destination, player_piece):
                raise InvalidMove('not yet implemented '+self.__class__.__name__+' move onto '+piece_at_destination.__class__.__name__+' '+str(self.position)+' -> '+str(new_position))
            else:
                # Should never happen!
                raise InvalidMove('invalid OR not yet implemented '+self.__class__.__name__+' move onto '+piece_at_destination.__class__.__name__+' '+str(self.position)+' -> '+str(new_position))
        original_coords = self.position
        board.set_board_piece(new_position, self) # move ourselves
        board.set_board_piece(original_coords, None) # blank_square - clean up previous location

class mirrored_piece(object):
    """A piece that can defend shots
    MUST be inherited WITH real board piece type as this 
    class accesses player_piece attributes!
    FIXME TODO this handles all mirroring (bar bomb pice) need to break out into each class
    """
    #mirrored_sides= {NORTH:180}
    # 180 = reverse shot
    # 0 = pass through
    # 90 = right angled (but may be -90 or 90 depending on angle of shot need to look at incoming angle)
    
    def defend_shot(self, attacking_piece, board, angle_of_hit):
        """returns if successfully defended being shot at angle_of_hit
        where angle_of_hit is simply the same type as self.rotation
        and attacking_piece the shooter, can be called to determine what sort of shooter and for shooting rules.
        TODO for transporters, defusers and maybe "hole" squares, propigate laser
        """
        if self.frozen:
            return False
        #print 'piece type', self.__class__.__name__
        #print 'angle_of_hit', angle_of_hit
        #print 'self.rotation', self.rotation
        #print 'self.mirrored_sides', self.mirrored_sides
        #print 'if piece was facing NORTH, would have been hit on %s side'% direction_to_string[calculate_reverse_beam_direction(angle_of_hit)]
        #print angle_of_hit, calculate_reverse_beam_direction(angle_of_hit),
        #print direction_to_string[angle_of_hit], direction_to_string[calculate_reverse_beam_direction(angle_of_hit)]
        side_hit_on = calculate_reverse_beam_direction(angle_of_hit) - self.rotation
        side_hit_on = normalize_angle(side_hit_on)
        print self.__class__.__name__, ' at ', self.position, ' defend_shot',
        print 'side_hit_on ', side_hit_on , direction_to_string[side_hit_on], 
        try:
            bounce_angle = self.mirrored_sides[side_hit_on]
            print 'bounce_angle', bounce_angle
            defended_shot=True
            if bounce_angle == 0:
                # straight through
                new_shot_direction=angle_of_hit
            elif bounce_angle == 180:
                # bounce straight back
                new_shot_direction=calculate_reverse_beam_direction(angle_of_hit)
            elif bounce_angle == 90:
                ## basically a bunch of magic value lookups :-( not clean but fairly small
                # right angle bounce back BUT depends on angle_of_hit
                # as to whether it is +90 or -90
                # cheat lookup table as have so few values
                """
                # Law of Reflection holds where the incident angle equals the reflected angle. Thus b = 180 - a
                Law of Reflection holds where the incident angle equals the reflected angle.
                    Thus b = 180o  - a.
                
                for case where mirror is horizontal i.e. ------ for hits above and below
                falls down for vertical mirror, i.e. |
                """
                if side_hit_on == NORTH_EAST:
                    # "normal" flat mirror
                    bounce_angle = NORTH_WEST
                elif side_hit_on == NORTH_WEST:
                    # "normal" flat mirror
                    bounce_angle = NORTH_EAST
                elif side_hit_on == WEST:
                    # prism side on hit
                    bounce_angle = SOUTH
                elif side_hit_on == EAST:
                    # prism side on hit
                    bounce_angle = SOUTH
                elif side_hit_on == SOUTH:
                    # prism hit on bottom, need to split beam
                    # perform one shot, the other wil be handled as normal
                    bounce_angle = EAST
                    new_shot_direction = normalize_angle(bounce_angle + self.rotation)
                    print 'prism first split'
                    attacking_piece.perform_shoot(board, origin_coords=self.position, angle_of_shot=new_shot_direction)
                    print 'prism second split'
                    bounce_angle = WEST
                else:
                    # do not yet have pieces with 45 degree mirror on any other surface so skip
                    raise ALCNotImplemented('DEBUG 90 degree bounces not implemented for %d in %s' % (side_hit_on,self.__class__.__name__))
                new_shot_direction = normalize_angle(bounce_angle + self.rotation)
            elif bounce_angle == 999:
                # dumb magic values again :-( this is a transporter/warp
                # FIXME TODO check alc to see what happens when laser hits 
                # transporter and then warped beam his reflective surface, 
                # that bounces back 180 degrees this version keeps bouncing 
                # until hit something (or wall)
                new_shot_direction = board.random_direction()
            else:
                raise ALCNotImplemented('unhandled bound angle %d in  %s' % (side_hit_on,self.__class__.__name__))
            print 'new_shot_direction', new_shot_direction
            attacking_piece.perform_shoot(board, origin_coords=self.position, angle_of_shot=new_shot_direction)
        except KeyError, info:
            print 'no mirror side, DESTROYED'
            defended_shot=False
        
        #print self.__class__.__name__, ' at ', self.position, 'defended_shot result', defended_shot
        return defended_shot

class shooting_piece(object):
    """A piece that can shoot
    MUST be inherited WITH real board piece type as this 
    class accesses player_piece attributes!
    """
    """
    def shot_effect(self, attacked_piece, board):
        board.destroy(attacked_piece)
    """
        
    def shoot(self, board, origin_coords=None, angle_of_shot=None):
        self.check_and_set_special(board)
        self.perform_shoot(board, origin_coords=origin_coords, angle_of_shot=angle_of_shot)

    def perform_shoot(self, board, origin_coords=None, angle_of_shot=None):
        ## TODO only allow one special move on a piece per round
        ## make two shoot methods, this one the grunt horse and an initial one that handles special move and we now is the main entry point
        if angle_of_shot is None:
            angle_of_shot=self.rotation
        if origin_coords is None:
            origin_coords = self.position
        #print 'DEBUG', origin_coords
        #print 'DEBUG', angle_of_shot
        #print 'DEBUG', DIRECTION_VECTORS[angle_of_shot]
        print self.__class__.__name__, ' at ', self.position, ' called to shoot from', origin_coords, ' angle', angle_of_shot,
        origin_x, origin_y = origin_coords
        current_x, current_y = origin_coords
        shot_direction = angle_of_shot
        delta_x, delta_y = DIRECTION_VECTORS[shot_direction]

        # not super happy with this here, but need a way to show bounces and originations - refactor? this code is (almost) duplicated in the loop
        list_of_shots = board.get_shootboard_xy(origin_coords)
        if shot_direction not in list_of_shots:
            list_of_shots.append(shot_direction)
        """
        can't stop here, if a prsim is hit and bounces many times, eg hit split and first slpit ends up bouncing back into the prism
        
        problem though is that I have cases where a transporter is hit, goes off in a direction and then bounces back into the transoporter, currently the transporter may randomly send it back teh same way AGAIN
        to handle first case above may need to break square down into quarter pieces so we know if a trail has been followed yet or not :-(
        else:
            # already processed shooting in this direction just stop!
            # e.g. shot goes in square with laser having unprotected rear
            return
        """


        next_shot_position = (current_x+delta_x, current_y+delta_y)
        print 'next_shot_position', next_shot_position
        while board.position_in_board(next_shot_position):
            #print next_shot_position, 'is in board'
            piece_to_shoot = board.get_board_piece(next_shot_position)
            if is_a_blank_square(piece_to_shoot) or isinstance(piece_to_shoot, hole_square):
                # this is a a normal empty square or hole that shots just go straight through
                list_of_shots = board.get_shootboard_xy(next_shot_position)
                if shot_direction not in list_of_shots:
                    list_of_shots.append(shot_direction)
                else:
                    # already processed shooting in this direction just stop!
                    # e.g. shot goes in square with laser having unprotected rear
                    break
            else:
                shot_defended = False
                if hasattr(piece_to_shoot, 'defend_shot'):
                    #print 'calling defend_move'
                    list_of_shots = board.get_shootboard_xy(next_shot_position) #remove/refactor into one update in this routine
                    if shot_direction not in list_of_shots: #remove/refactor into one update
                        list_of_shots.append(shot_direction) #remove/refactor into one update
                    shot_defended = piece_to_shoot.defend_shot(self, board, shot_direction)
                '''
                try:
                    shot_defended = piece_to_shoot.defend_shot(self, board, shot_direction)
                except AttributeError, info:
                    # can not check attribute name easiy without string pasrsing? :-(
                    print info
                    print dir(info)
                    print info.args
                    print dir(info.args)
                    raise
                '''
                if shot_defended:
                    print 'shot_defended SUCCESS', shot_defended, 'at', piece_to_shoot.position, 'with', piece_to_shoot.__class__.__name__
                    # FIXME TODO add to (or simple set a flag to True) that a shot "bounced"
                    # / maybe make note of bounced back and hit one way mirror? mosdtly for sound effects
                else:
                    print 'shot_defended FAILED', shot_defended, 'at', piece_to_shoot.position, 'with', piece_to_shoot.__class__.__name__
                    board.successfully_shot_this_turn.append(piece_to_shoot)
                    list_of_shots = board.get_shootboard_xy(next_shot_position)
                    list_of_shots.append(EFFECTIVE_HIT)
                break
                # error?
                raise ALCNotImplemented('DEBUG not implemented shooting none blank squares; %s' % (piece_to_shoot.__class__.__name__,))
            current_x, current_y = next_shot_position
            next_shot_position = (current_x+delta_x, current_y+delta_y)
        # hit a piece or edge of board, shots just die in ALC (i.e. walls/edge of board are not reflective
        # but could be a neat extended version feature. TODO look at ealc board :-)
        print 'hit a piece or edge of board at, shot instance dies here', next_shot_position
        # should be the end of the shooting "loop"


# visible/physical board pieces

class hole_square(board_piece):
    """(random) empty square in centre line of board
    Destroys anything that enters it
    """
    text_repr='#'
    def defend_move(self, attacking_piece, board):
        attacking_piece.destroyed=True
        #raise InvalidMove('not yet implemented move onto '+self.__class__.__name__)
        #raise InvalidMove('not yet implemented '+attacking_piece.__class__.__name__+' move onto '+self.__class__.__name__+' '+str(attacking_piece.position)+' -> '+str(self.position)) ## fails as missing position attribute
        #raise InvalidMove('not yet implemented '+attacking_piece.__class__.__name__+' move onto '+self.__class__.__name__+' '+str(attacking_piece.position))
        if isinstance(attacking_piece, player_piece):
            original_coords = attacking_piece.position
            board.destroy(attacking_piece, explode=True, explode_position=self.position)
            return True # defend successful, caller should stop
        else:
            raise InvalidMove('bad piece moved onto hole')

class warp_piece(mirrored_piece, board_piece):
    """Warp/Hyper Hole in centre of board"""
    text_repr='W'
    mirrored_sides= {NORTH : 999, NORTH_EAST : 999, EAST : 999, SOUTH_EAST : 999, SOUTH : 999, SOUTH_WEST : 999, WEST : 999, NORTH_WEST : 999}
    rotation=0 ## used by defend_shot() but other than that not needed
    ## nolonger needed hack now has pos #position=(7, 5) ## bit of a hack, used by defend_shot() - may need to update init_board_piece()
    frozen=False ## bit of a hack, used by defend_shot() - may need to update init_board_piece()

    def defend_move(self, attacking_piece, board):
        """warp piece defend is like transport move/attack"""
        # add default which is fail, either False or (False, )
        if isinstance(attacking_piece, player_piece):
            original_coords = attacking_piece.position
            new_destcoords, new_destrotation = board.random_position()
            attacking_piece.rotation = new_destrotation
            #FIXME teleport to hole should be destroyed!!
            piece_at_destination = board.get_board_piece(new_destcoords)
            # Logic for calling defend from taking_piece.perform_move()
            if hasattr(piece_at_destination, 'defend_move'):
                if piece_at_destination.defend_move(attacking_piece, board):
                    return True # defend successful, caller should stop
            
            board.set_board_piece(new_destcoords, attacking_piece)
            board.set_board_piece(original_coords, None) # blank_square - clean up previous location
            return True # defend successful, caller should stop
        else:
            raise InvalidMove('bad piece moved onto warp')

class blank_square(board_piece):
    """TODO decided if this is needed or over designed.
    Simply a blank, empty square
    currently unused, None is used instead"""
    pass

def is_a_blank_square(piece_to_check):
    #return isinstance(piece_to_check, blank_square)
    return piece_to_check is None


class player_piece(board_piece):
    """Super class of piece that player can/will move
    """
    
    # maybe move into __init__ ?
    can_move_onto_playerpiece=False ## can piece move onto squares containing other pieces?
    can_attack=False ## can piece attack this turn? false if not an attacking piece or if an attacking piece and have attacked this turn
    can_shoot=False ## can piece shoot this turn? false if not an shooting piece or if an shooting piece and have shot this turn
    
    def __init__(self, player_number, rotation, position):
        self.frozen=False
        self.destroyed=False
        self.position=position # position/co-ordinate on board. Tuple (x,y)
        self.rotation=rotation # direction
        self.player_number=player_number # player colour
        self.special_used=False # only used for transporters, guns and stompers
        self.range=0 #?

    def __repr__(self):
        return '%s(player_number=%r, rotation=%r, position=%r) self.frozen=%r' % (self.__class__.__name__, self.player_number, self.rotation, self.position, self.frozen)

    def check_and_set_special(self, board):
        """Check if special has been used and then set it
        raises exception on check failure"""
        if self.special_used == True:
            # should not get here as player_piece.check_valid_move() makes this check and it would have failed earlier.
            raise InvalidMove(self.__class__.__name__ + ' has already used special move/attack this turn')
        
        self.special_used=True
        ##board.pieces_changed_this_turn.append() ## fixme
        board.pieces_to_reset_after_this_turn.append(self) 

    #def check_valid_move(self, new_position, board, moves_left=1):
    def check_valid_move(self, new_position, board):
        """Is the new location a place this piece can move too?
        raises exception if bad
        does nothing if move ok (i.e. ignore return value)
        only handles 1 space movements, does not yet handle alc piece can moveupto 3 spaces
        """
        if self.frozen:
            # Should never get here as this is checked in board.enter_move()
            # only way to handle rotation as that is handled soley by enter_move() at the moment
            raise InvalidMove('%s at %r is frozen and can not be used' % (self.__class__.__name__,self.position) )
        board.check_position(new_position)
        moves_left=1
        cur_x, cur_y = self.position
        new_x, new_y = new_position
        x_delta = abs(cur_x - new_x)
        y_delta = abs(cur_y - new_y)
        try:
            assert (y_delta == 0 and x_delta <= moves_left) or (x_delta == 0 and y_delta <= moves_left), 'move too large/far'
            piece_at_destination = board.get_board_piece(new_position)
            if self.can_move_onto_playerpiece:
                if isinstance(piece_at_destination, player_piece) and self.special_used == True:
                    raise InvalidMove('this piece has already used special move/attack this turn')
            else:
                assert not isinstance(piece_at_destination, player_piece), '%s can not take other pieces' % (self.__class__.__name__)
        except AssertionError, info:
            raise InvalidMove(str(info))

    def perform_move(self, new_position, board):
        self.check_valid_move(new_position, board)
        piece_at_destination = board.get_board_piece(new_position)
        if is_a_blank_square(piece_at_destination): # blank_square
            original_coords = self.position
            board.set_board_piece(new_position, self) # move ourself
            board.set_board_piece(original_coords, None) # blank_square - clean up previous location
        else:
            if hasattr(piece_at_destination, 'defend_move'):
                if piece_at_destination.defend_move(self, board):
                    return
            else:
                # FIXME TODO if warp or hole can attack but have to call defend
                raise InvalidMove('not yet implemented '+self.__class__.__name__+' move onto '+piece_at_destination.__class__.__name__+' '+str(self.position)+' -> '+str(new_position))


# Real player controlled pieces

class stomper_piece(mirrored_piece, taking_piece, player_piece):
    """stomper or pawn piece
    Only has mirror on 3 angles/sides.
    Direction up/north/0 means the central mirrored side is facing up
    it has protection on NORTHWEST, NORTH, and NORTHEAST sides
    """
    # TODO two different types of stomper, use just one class with different attributes?
    text_repr='S'
    mirrored_sides= {NORTH : 180, NORTH_EAST : 180, NORTH_WEST : 180}
    
class mirrorstomper_piece(mirrored_piece, taking_piece, player_piece):
    """mirror stomper- invunerable to direct laser and freezer shots"""
    # TODO two different types of stomper, use just one class with different attributes?
    text_repr='Z'
    mirrored_sides= {NORTH : 180, NORTH_EAST : 180, EAST : 180, SOUTH_EAST : 180, SOUTH : 180, SOUTH_WEST : 180, WEST : 180, NORTH_WEST : 180}

class mirror_piece(mirrored_piece, player_piece):
    """alc mirror in triangle
    
    direction up/north/0 means the mirrored side is facing up
    and vunerable to shoots from SOUTH,
    i.e. shoots moving NORTH hitting SOUTH side of mirror
    """
    text_repr='M'
    mirrored_sides= {NORTH : 180, NORTH_EAST : 90, NORTH_WEST : 90, EAST : 0, WEST : 0}

class oneway_mirror_piece(mirrored_piece, player_piece):
    """one way mirror
    direction up/north/0 means the mirrored side is facing up"""
    text_repr='O'

    #mirrored_sides= {NORTH:180}
    mirrored_sides= {NORTH:180, SOUTH:0}
    # 180 = reverse shot
    # 0 = pass through
    # 90 = right angled (but may be -90 or 90 depending on angle of shot need to look at incoming angle)

class transporter_piece(mirrored_piece, player_piece):
    """Transporter/hypercube"""
    text_repr='T'
    mirrored_sides= {NORTH : 999, NORTH_EAST : 999, EAST : 999, SOUTH_EAST : 999, SOUTH : 999, SOUTH_WEST : 999, WEST : 999, NORTH_WEST : 999}
    can_move_onto_playerpiece=True ## can piece move onto squares containing other pieces?
    
    def perform_move(self, new_position, board):
        move_target_piece=True
        self.check_valid_move(new_position, board)
        # if new_position contains empty space just move/attack
        # if new_position contains player perform transport move/attack
        # if new_position contains warp, warp transports us - warp defends
        # if new_position contains hole, we get destroyed - hole defends
        piece_at_destination = board.get_board_piece(new_position)
        if is_a_blank_square(piece_at_destination): # blank_square
            pass # handled later on, this is bad form but refactor later
        elif isinstance(piece_at_destination, player_piece):
            #assert self.special_used == False, 'this piece has already transported this turn'
            if self.special_used == True:
                # should not get here as player_piece.check_valid_move() makes this check and it would have failed earlier.
                raise InvalidMove('this piece has already transported this turn')
            # lets tranport it!
            new_destcoords, new_destrotation = board.random_position()
            piece_at_destination.rotation = new_destrotation
            #FIXME teleport to hole should be destroyed!!
            self.special_used=True
            ##board.pieces_changed_this_turn.append() ## fixme
            board.pieces_to_reset_after_this_turn.append(self) 
            new_destination_piece = board.get_board_piece(new_destcoords)
            # Logic for calling defend from taking_piece.perform_move()
            if hasattr(new_destination_piece, 'defend_move'):
                if new_destination_piece.defend_move(piece_at_destination, board):
                    move_target_piece=False
            if move_target_piece:
                board.set_board_piece(new_destcoords, piece_at_destination)
        else:
            if hasattr(piece_at_destination, 'defend_move'):
                if piece_at_destination.defend_move(self, board):
                    return
            else:
                raise InvalidMove('debug, unhandled transport location type in board')
        original_coords = self.position
        board.set_board_piece(new_position, self) # move ourselves
        board.set_board_piece(original_coords, None) # blank_square - clean up previous location

class prism_piece(mirrored_piece, player_piece):
    """prism/splitter
    direction up/north/0 means the vunerable non-mirrored side is facing up/north
    
    if shot on the NORTH side (i.e. shot going south, hitting north side) 
        will be destroyed
    if shot on the SOUTH side (i.e. shot going north, hitting south side) 
        beam will split in perpendicular directions
    
    """
    text_repr='P'
    mirrored_sides= {NORTH_EAST : 0, NORTH_WEST : 0, SOUTH_EAST : 0, SOUTH_WEST : 0, EAST : 90, WEST : 90, SOUTH : 90}

class freezer_piece(shooting_piece, mirrored_piece, player_piece):
    """freezer/stunner
    direction up/north/0 means the shooting side is facing up
    mirror sides facing SOUTH, EAST, WEST
    """
    text_repr='F'
    mirrored_sides= {SOUTH : 180, EAST : 180, WEST : 180}

    def shot_effect(self, attacked_piece, board):
        """Quick way to freeze, 
        calculate ahead of time WHEN the frozen piece will be unfrozen
        According to http://www.laserchess.org/instructions_alc.html 
        each round there is a 75% chance of remaining frozen
        could implement that here and simply find out when BUT need to deal with infinite loops in extreme case
        could simply check each frozen piece each round"""
        attacked_piece.frozen = True
        # 1 works, 2 works, need random
        # TODO FIXME add random 1 to ???
        num_round_frozen = 2 # random number from 1 (unfreeze next round) to infinity?
        num_round_frozen = random.choice(range(1,10)) # i.e. maximum number of frozen rounds is 10
        attacked_piece.unfreeze_in_round = board.rounds_played + num_round_frozen
        if attacked_piece not in board.frozen_pieces:
            board.frozen_pieces.append(attacked_piece)
        # TODO timeout for unfrozen (alternative is to random check each turn)
        # TODO currently pieces that unfreeze, unfreeze at the start of the round, should be on a turn?
        # TODO test freezing an already frozen piece
        # TODO test taking (shot with laser and take with stomper/king/transporter) an already frozen piece
        # TODO - how to hell to display this on screen!! not a problem for game engine but ideas go here!
        # currently have frozen images/bitmaps
        # one idea is that select piece will actually change border-colour and frozen pieces changes opacity in html
        # other option is to simple have 3 player pieces, player one, player two... and frozen player which both 1 and 2 share
        # in amiga alc the frozzen piece is just one solid grey colour (i.e. can't even see mirror side) -- probably the one to do


class bomb_piece(player_piece):
    """bomb/diffuser
    direction up/north/0 means the entry hole side is facing up,down,left,right
    vunerable to normal shots/actions on diagonal NORTHEAST, SOUTHEAST, etc. sides"""
    text_repr='B'

    def defend_shot(self, attacking_piece, board, angle_of_hit):
        """returns if successfully defended being shot at angle_of_hit
        where angle_of_hit is simply the same type as self.rotation
        and attacking_piece the shooter, can be called to determine what sort of shooter and for shooting rules.
        """
        if self.frozen:
            return False
        side_hit_on = calculate_reverse_beam_direction(angle_of_hit) - self.rotation
        side_hit_on = normalize_angle(side_hit_on)
        if side_hit_on == NORTH or side_hit_on == SOUTH or side_hit_on == EAST or side_hit_on == WEST:
            # bomb mode! effect all surrounding pieces
            origin_x, origin_y = self.position
            for delta_x in xrange(-1, 2):
                for delta_y in xrange(-1, 2):
                    temp_coords = (origin_x+delta_x, origin_y+delta_y)
                    if temp_coords != self.position and board.position_in_board(temp_coords):
                        piece_at_destination = board.get_board_piece(temp_coords)
                        if isinstance(piece_at_destination, player_piece):
                            #attacking_piece.shot_effect(piece_at_destination, board)
                            board.successfully_shot_this_turn.append(piece_at_destination)
                            list_of_shots = board.get_shootboard_xy(piece_at_destination.position)
                            list_of_shots.append(EFFECTIVE_HIT)
        return False

class laser_piece(shooting_piece, player_piece):
    """laser/gun
    direction up, north, 0 means the shooting side is facing up"""
    text_repr='L'

    def shot_effect(self, attacked_piece, board):
        board.destroy(attacked_piece)

class king_piece(taking_piece, player_piece):
    """King"""
    text_repr='K'
    
    # using stomper method does not work :-(
    ##perform_move = stomper_piece.perform_move
    ## TypeError: unbound method perform_move() must be called with stomper_piece instance as first argument (got tuple instance instead)


def str2int_tuple(in_str):
    """takes in string returns tuple of ints
    """
    # this is for pre Python 2.4
    # see http://news.hping.org/comp.lang.python.archive/0317.html
    return tuple([int(x) for x in in_str[1:-1].split(",")])
"""
MOVE_PASS=1
MOVE_ROTATE=2
MOVE_SHOOT=3
MOVE_MOVEMENT=4
"""
MOVE_PASS='p'
MOVE_ROTATE='r'
MOVE_SHOOT='s'
MOVE_MOVEMENT='m'
movement_names={
    MOVE_PASS:'MOVE_PASS',
    MOVE_ROTATE:'MOVE_ROTATE',
    MOVE_SHOOT:'MOVE_SHOOT',
    MOVE_MOVEMENT:'MOVE_MOVEMENT'
    }
class piece_move(object):
    """Advanced Laser Chess move"""
    def __init__(self, *args, **kwargs):
        """
        move_type=None, origin_coords=None, dest_coords=None, new_direction=None, 
        """
        self.origin_coords = None
        self.dest_coords = None
        self.new_direction = None
        try:
            self.move_type = kwargs['move_type'] # movement, rotate, shoot, pass
        except KeyError, info:
            self.move_type = None
        if self.move_type is None:
            # pick up string param and decode
            if not args:
                raise InvalidMove('movement instruction missing')
            try:
                command_items = args[0].split()
                self.move_type = command_items[0][0].lower()
                if self.move_type != MOVE_PASS:
                    try:
                        kwargs['origin_coords']= str2int_tuple(command_items[1])
                    except ValueError, info:
                        raise InvalidMove('invalid origin %r' % (command_items[1]))
                    
                    if self.move_type == MOVE_ROTATE:
                        ## TODO add optional num_rotations=x instead of direction
                        ## e.g. num_rotations=0 (do nothing);
                        ##      num_rotations=1 (clock wise 45 degrees)
                        ##      num_rotations=2 (clock wise 90 degrees)
                        ##      num_rotations=7 (clock wise 360-45 degrees)
                        ##      num_rotations=8 (do nothing). Suport?
                        ##      num_rotations=9 (clock wise 45 degrees). Suport?
                        temp_intx = 0
                        temp_rotation_str = command_items[2].upper()
                        NUM_ROTATIONS_STR = 'NUM_ROTATIONS='
                        perform_num_rotations=False
                        if temp_rotation_str.startswith(NUM_ROTATIONS_STR):
                            perform_num_rotations=True
                            temp_rotation_str = temp_rotation_str.replace(NUM_ROTATIONS_STR, '')
                        try:
                            temp_intx = int(temp_rotation_str)
                        except ValueError, info:
                            # assume 'invalid literal for int()'
                            # see if it is a NORTH/SOUTH/etc. string
                            try:
                                temp_intx = string_to_direction[temp_rotation_str]
                            except KeyError, info:
                                raise InvalidMove('invalid rotation %r' % (temp_rotation_str))
                        if perform_num_rotations:
                            kwargs['num_rotations'] = temp_intx
                        else:
                            kwargs['new_direction'] = temp_intx
                        
                    elif self.move_type == MOVE_MOVEMENT:
                        try:
                            kwargs['dest_coords']= str2int_tuple(command_items[2])
                        except ValueError, info:
                            raise InvalidMove('invalid destination')
            except IndexError, info:
                raise InvalidMove('bad movement instructions (move information missing): %r' % (args))
                
        if self.move_type != MOVE_PASS:
            self.origin_coords = kwargs['origin_coords']
        
        if self.move_type == MOVE_ROTATE:
            try:
                self.num_rotations = int(kwargs['num_rotations'])
                self.new_direction = None
                #assert self.num_rotations >=0 and self.num_rotations <=7, 'to many num_rotations'
                if self.num_rotations < 0 or self.num_rotations >7:
                    raise InvalidMove('to many num_rotations %r' % (self.num_rotations))
            except KeyError, info:
                self.num_rotations = None
                self.new_direction = kwargs['new_direction']
                #assert self.new_direction in DIRECTION_ORDER, 'invalid rotation'
                if self.new_direction not in DIRECTION_ORDER:
                    raise InvalidMove('invalid rotation')
        elif self.move_type == MOVE_MOVEMENT:
            self.dest_coords = kwargs['dest_coords']
            if self.origin_coords is None:
                raise InvalidMove('origin_coords missing')
            if self.dest_coords is None:
                raise InvalidMove('dest_coords missing')
        elif self.move_type == MOVE_PASS:
            pass
        elif self.move_type == MOVE_SHOOT:
            pass
        else:
            raise InvalidMove('unknown move type')
    
    def __repr__(self):
        extra_str = ''
        if self.move_type != MOVE_PASS:
            extra_str = ', origin_coords=%r' % (self.origin_coords,)
        if self.move_type == MOVE_MOVEMENT:
            extra_str += ', dest_coords=%r' % (self.dest_coords,)
        elif self.move_type == MOVE_ROTATE:
            if self.num_rotations is not None:
                extra_str += ', num_rotations=%r' % (self.num_rotations )
            if self.new_direction is not None:
                extra_str += ', new_direction=%r' % (self.new_direction)
        #return '%s(move_type=%s%s)' % (self.__class__.__name__, movement_names[self.move_type], extra_str )
        return '%s(move_type=%r%s)' % (self.__class__.__name__, self.move_type, extra_str )

    def __str__(self):
        extra_str = ''
        if self.move_type != MOVE_PASS:
            extra_str = ' %r' % (self.origin_coords,)
        if self.move_type == MOVE_MOVEMENT:
            extra_str += ' %r' % (self.dest_coords,)
        elif self.move_type == MOVE_ROTATE:
            if self.num_rotations is not None:
                extra_str += ' %r' % (self.num_rotations)
            if self.new_direction is not None:
                extra_str += ' %r' % (self.new_direction)
        return '%s %s' % (self.move_type, extra_str )



#EMPTY_SQUARE=None
EMPTY_SQUARE_STR=' '

#PLAYER_ONE=0
#PLAYER_TWO=1
PLAYER_ONE=1
PLAYER_TWO=2
RED_PLAYER=PLAYER_ONE
GREEN_PLAYER=PLAYER_TWO
player_map={
    RED_PLAYER: ('red', (180, 72, 72)), 
    GREEN_PLAYER: ('green', (72, 180, 72))
    }
class board(object):
    """The Advanced Laser Chess board"""
    def __init__(self, board_size=None):
        ## FIXME TODO - add optional keyword params for fileobjects/name
        ##  object more converient BUT if have crash filename (always open/write/close) would be safer;
        ##      1 for real moves log (which currently logged in memory)
        ##          need some way of loggin random events too to allow replays
        ##          needs __str__ for moves for logging
        ##      2 for all moves requested (including invalid moves)
        ##          NOTE would not log completly bad moves like invalid directions, etc. only invalid moves for pieces
        if debug:
            random.seed(0) # debug - ensure random... isn't! :-)
        if board_size is None:
            board_size=(15,11) # alc board size
        self.board_size = board_size
        self.board=[]
        self.current_player=PLAYER_ONE ## PLAYER_ONE or PLAYER_TWO
        self.turns_left=3 ## 0 to 3
        self.rounds_played=0 ## Number of rounds played so far. rounds_played+1 = current round number (assume round 1 is the first)
        self.moves_history=[] ## history log of moves (for replays). list of piece_move
        self.pieces_changed_this_turn=[] # current phase of turn changes, e.g. stuff to blow up? squares to display laser ray?
        self.pieces_to_reset_after_this_turn=[] # stompers that have taken, transporters that have transported, guns that have shot
        self.frozen_pieces=[]
        
        self.init_shots() ## init shot board; lists what shots are on what tiles/spaces
        
        # 0,0 is top left hand corner. Red player left hand back corner
        # on alc board 14,10 is bottom right hand corner. Green rear left hand corner if looking towards opponent.
        x_len, y_len = self.board_size
        for temp_y in range(y_len):
            temp_row=[]
            for temp_x in range(x_len):
                #temp_row.append(EMPTY_SQUARE)
                temp_row.append(None)
            self.board.append(temp_row)
        
        ## Advanced Laser Chess board piece init
        # TODO FIX direction/rotation
        temp_player_number = PLAYER_ONE
        temp_rotation = EAST
        self.init_board_piece((0, 0), oneway_mirror_piece, temp_player_number, temp_rotation)
        self.init_board_piece((0, 1), mirror_piece, temp_player_number, temp_rotation)
        self.init_board_piece((0, 2), bomb_piece, temp_player_number, temp_rotation)
        self.init_board_piece((0, 3), freezer_piece, temp_player_number, WEST)
        self.init_board_piece((0, 4), laser_piece, temp_player_number, temp_rotation)
        self.init_board_piece((0, 5), king_piece, temp_player_number, temp_rotation)
        self.init_board_piece((0, 6), laser_piece, temp_player_number, temp_rotation)
        self.init_board_piece((0, 7), freezer_piece, temp_player_number, WEST)
        self.init_board_piece((0, 8), bomb_piece, temp_player_number, temp_rotation)
        self.init_board_piece((0, 9), mirror_piece, temp_player_number, temp_rotation)
        self.init_board_piece((0, 10), oneway_mirror_piece, temp_player_number, temp_rotation)
        self.init_board_piece((1, 0), mirror_piece, temp_player_number, SOUTH_EAST)
        self.init_board_piece((1, 1), mirror_piece, temp_player_number, NORTH)
        self.init_board_piece((1, 2), oneway_mirror_piece, temp_player_number, temp_rotation)
        self.init_board_piece((1, 3), transporter_piece, temp_player_number, temp_rotation)
        self.init_board_piece((1, 4), prism_piece, temp_player_number, temp_rotation)
        self.init_board_piece((1, 5), freezer_piece, temp_player_number, WEST)
        self.init_board_piece((1, 6), prism_piece, temp_player_number, temp_rotation)
        self.init_board_piece((1, 7), transporter_piece, temp_player_number, temp_rotation)
        self.init_board_piece((1, 8), oneway_mirror_piece, temp_player_number, temp_rotation)
        self.init_board_piece((1, 9), mirror_piece, temp_player_number, SOUTH)
        self.init_board_piece((1, 10), mirror_piece, temp_player_number, NORTH_EAST)
        self.init_board_piece((2, 3), stomper_piece, temp_player_number, temp_rotation)
        self.init_board_piece((2, 4), stomper_piece, temp_player_number, temp_rotation)
        #self.init_board_piece((2, 5), stomper_piece, temp_player_number, temp_rotation) ## mega stomper
        self.init_board_piece((2, 5), mirrorstomper_piece, temp_player_number, temp_rotation) ## mega stomper
        self.init_board_piece((2, 6), stomper_piece, temp_player_number, temp_rotation)
        self.init_board_piece((2, 7), stomper_piece, temp_player_number, temp_rotation)
        
        temp_player_number = PLAYER_TWO
        temp_rotation = WEST
        self.init_board_piece((14, 0), oneway_mirror_piece, temp_player_number, temp_rotation)
        self.init_board_piece((14, 1), mirror_piece, temp_player_number, temp_rotation)
        self.init_board_piece((14, 2), bomb_piece, temp_player_number, temp_rotation)
        self.init_board_piece((14, 3), freezer_piece, temp_player_number, EAST)
        self.init_board_piece((14, 4), laser_piece, temp_player_number, temp_rotation)
        self.init_board_piece((14, 5), king_piece, temp_player_number, temp_rotation)
        self.init_board_piece((14, 6), laser_piece, temp_player_number, temp_rotation)
        self.init_board_piece((14, 7), freezer_piece, temp_player_number, EAST)
        self.init_board_piece((14, 8), bomb_piece, temp_player_number, temp_rotation)
        self.init_board_piece((14, 9), mirror_piece, temp_player_number, temp_rotation)
        self.init_board_piece((14, 10), oneway_mirror_piece, temp_player_number, temp_rotation)
        self.init_board_piece((13, 0), mirror_piece, temp_player_number, SOUTH_WEST)
        self.init_board_piece((13, 1), mirror_piece, temp_player_number, NORTH)
        self.init_board_piece((13, 2), oneway_mirror_piece, temp_player_number, temp_rotation)
        self.init_board_piece((13, 3), transporter_piece, temp_player_number, temp_rotation)
        self.init_board_piece((13, 4), prism_piece, temp_player_number, temp_rotation)
        self.init_board_piece((13, 5), freezer_piece, temp_player_number, EAST)
        self.init_board_piece((13, 6), prism_piece, temp_player_number, temp_rotation)
        self.init_board_piece((13, 7), transporter_piece, temp_player_number, temp_rotation)
        self.init_board_piece((13, 8), oneway_mirror_piece, temp_player_number, temp_rotation)
        self.init_board_piece((13, 9), mirror_piece, temp_player_number, SOUTH)
        self.init_board_piece((13, 10), mirror_piece, temp_player_number, NORTH_WEST)
        self.init_board_piece((12, 3), stomper_piece, temp_player_number, temp_rotation)
        self.init_board_piece((12, 4), stomper_piece, temp_player_number, temp_rotation)
        #self.init_board_piece((12, 5), stomper_piece, temp_player_number, temp_rotation) ## mega stomper
        self.init_board_piece((12, 5), mirrorstomper_piece, temp_player_number, temp_rotation) ## mega stomper
        self.init_board_piece((12, 6), stomper_piece, temp_player_number, temp_rotation)
        self.init_board_piece((12, 7), stomper_piece, temp_player_number, temp_rotation)

        # testing centre pieces, not always located here as they should be random!
        self.init_board_piece((7, 5), warp_piece)
        self.init_board_piece((7, 1), hole_square)
        self.init_board_piece((7, 3), hole_square)
        self.init_board_piece((7, 7), hole_square)
        self.init_board_piece((7, 9), hole_square)
        
        self.lost_pieces = {
            PLAYER_ONE: {'king_piece': 0, 'oneway_mirror_piece': 0, 
                'transporter_piece': 0, 'prism_piece': 0, 
                'mirror_piece': 0, 'mirrorstomper_piece': 0, 
                'freezer_piece': 0, 'laser_piece': 0, 
                'stomper_piece': 0, 'bomb_piece': 0}, 
            PLAYER_TWO: {'king_piece': 0, 'oneway_mirror_piece': 0, 
                'transporter_piece': 0, 'prism_piece': 0, 
                'mirror_piece': 0, 'mirrorstomper_piece': 0, 
                'freezer_piece': 0, 'laser_piece': 0, 
                'stomper_piece': 0, 'bomb_piece': 0}
        }
        self.winner=None

    def init_shots(self):
        # init list of shot types on the board
        # board could contain laser/freezer shots from all
        # angles if shot bounces around enough
        # so need a list, shots have a direction, e.g.
        # NORTH means heading NORTH(up), SOUTH means heading SOUTH (down)
        # NORTH and SOUTH may "look" the same but are different directions
        self.successfully_shot_this_turn=[]
        self.shootboard=[]
        x_len, y_len = self.board_size
        for temp_y in range(y_len):
            temp_row=[]
            for temp_x in range(x_len):
                temp_row.append([])
            self.shootboard.append(temp_row)
    def debug_print_shots(self):
        print 'debug_print_shots'
        temp_str=[]
        current_row=0
        for temp_row in self.shootboard:
            temp_str.append('%2d'%current_row)
            temp_str.append('|')
            for temp_col in temp_row:
                if EFFECTIVE_HIT in temp_col:
                    temp_str.append('*')
                elif len(temp_col) != 0:
                    # TODO determine direction!
                    temp_str.append('o')
                else:
                    temp_str.append(' ')
            temp_str.append('|')
            temp_str.append('\n')
            current_row += 1
        print ''.join(temp_str)
        
    def get_shootboard_xy(self, position):
        """helper function to get list of shots at position"""
        self.check_position(position)
        temp_x, temp_y = position
        # set piece and board co-ordinates
        # NOTE x,y in cartisian order for piece and reversed for board indexing
        return self.shootboard[temp_y][temp_x]


    def losess(self):
        print ' == losess =='
        for x in self.lost_pieces:
            print 'Player', x
            for y in self.lost_pieces[x]:
                if self.lost_pieces[x][y] !=0:
                    print '    ', y, self.lost_pieces[x][y]
            print ''
            
    def debug_check_positions(self):
        boardx, boardy = self.board_size
        for x in xrange(boardx):
            for y in xrange(boardy):
                temp_piece = self.board[y][x]
                if isinstance(temp_piece, player_piece):
                    temp_x, temp_y = temp_piece.position
                    assert x == temp_x and y == temp_y, 'piece coords do not match board piece coords; board coords: %r piece coords:%r' % ((x, y), temp_piece.position)
                else:
                    assert is_a_blank_square(temp_piece) or isinstance(temp_piece, board_piece), 'not a valid piece at %r' % ((x, y))
        
    def random_direction(self):
        result = random.choice(DIRECTION_ORDER)
        return result
    def random_position(self):
        """Returns random EMPTY or HOLE (position, rotation), tuple is a valid board position
        Should the centre warper be a valid position?
        Rather a brute force approach, finds all suitable places and picks ones
        FIXME TODO add non random pos and rotation (not seed related) to test warp on to holes and centre warper
        """
        def suitable_destination(piece_to_test):
            result = True
            if isinstance(piece_to_test, player_piece):
                result = False
            if isinstance(piece_to_test, warp_piece):
                ## TODO confirm if this is correct!
                result = False
            return result
        boardx, boardy = self.board_size
        valid_destinations=[]
        row_count=0
        for temp_row in self.board:
            col_count=0
            for temp_col in temp_row:
                if suitable_destination(temp_col):
                    valid_destinations.append((col_count, row_count))
                col_count += 1
            row_count+=1
        random_position = random.choice(valid_destinations)
        debug_random_pos=False
        #debug_random_pos=True## FIXME!
        if debug_random_pos:
            random_position = (7,7) ## hard coded Hole
        random_rotation = self.random_direction()
        if debug:
            print 'random location', (random_position, random_rotation)
        return (random_position, random_rotation)

        
    def position_in_board(self, position):
        """check position is a valid board position, return True or False"""
        boardx, boardy = self.board_size
        temp_x, temp_y = position
        return temp_x >= 0 and temp_x < boardx and temp_y >= 0 and temp_y < boardy
        
    def check_position(self, position):
        """check position is a valid board position"""
        ## FIXME TODO make call to position_in_board for assert!
        boardx, boardy = self.board_size
        temp_x, temp_y = position
        try:
            assert temp_x >= 0 and temp_x <= boardx and temp_y >= 0 and temp_y <= boardy, 'invalid board location, %r' % (position,)
        except AssertionError, info:
            raise InvalidMove(str(info))
        
    def get_board_piece(self, position):
        """helper function to get piece instance at position"""
        self.check_position(position)
        temp_x, temp_y = position
        # set piece and board co-ordinates
        # NOTE x,y in cartisian order for piece and reversed for board indexing
        return self.board[temp_y][temp_x]
        
    def set_board_piece(self, position, the_piece):
        """helper function to set piece instance at position"""
        self.check_position(position)
        temp_x, temp_y = position
        # set piece and board co-ordinates
        # NOTE x,y in cartisian order for piece and reversed for board indexing
        self.board[temp_y][temp_x] = the_piece
        if isinstance(the_piece, player_piece):
            # only have to set position/coords for player pieces
            the_piece.position = position
    
    def destroy(self, attacked_piece, explode=False, explode_position=None):
        self.lost_pieces[attacked_piece.player_number][attacked_piece.__class__.__name__] += 1
        self.set_board_piece(attacked_piece.position, None) # blank_square - clean up previous location
        if explode:
            # set explosion marker, using in passed in coords
            list_of_shots = self.get_shootboard_xy(explode_position)
            if EFFECTIVE_HIT not in list_of_shots:
                # i.e. explode, changes meaning of EFFECTIVE_HIT some what..
                list_of_shots.append(EFFECTIVE_HIT)

    #def init_board_piece(self, position, player_number, rotation, piece_type):
    #def init_board_piece(self, position, player_number=None, rotation=None, piece_type=None):
    def init_board_piece(self, position, piece_type, player_number=None, rotation=None):
        """create a new piece at the specified location with specified init values
        """
        temp_x, temp_y = position
        # set piece and board co-ordinates
        # NOTE x,y in cartisian order for piece and reversed for board indexing
        if player_number is None and rotation is None:
            #self.board[temp_y][temp_x] = piece_type() #(temp_x, temp_y)
            self.board[temp_y][temp_x] = piece_type( (temp_x, temp_y) )
        else:
            self.board[temp_y][temp_x] = piece_type(player_number, rotation, (temp_x, temp_y))

    def enter_move(self, moveinfo):
        """performs a single moveinfo, where move is an instance of piece_move 
        """
        self.init_shots()
        if moveinfo.move_type == MOVE_PASS:
            self.turns_left=0
        else:
            piece_to_move = self.get_board_piece(moveinfo.origin_coords)
            # two different styles of doing the same check!
            # TODO frozen piece?
            """
            if not isinstance(piece_to_move, player_piece):
                raise InvalidMove('only allowed to move player pieces')
            if piece_to_move.player_number != self.current_player:
                raise InvalidMove('wrong player piece')
            """
            try:
                # FIXME CRITICAL
                # asserts do not get called/used in py2exe - really only used in debug
                # not good for runtime checks
                assert isinstance(piece_to_move, player_piece), 'only allowed to move player pieces %r' % (moveinfo.origin_coords,)
                assert piece_to_move.player_number == self.current_player, 'wrong player piece %r' % (moveinfo.origin_coords,)
            except AssertionError, info:
                raise InvalidMove(str(info))
            
            if piece_to_move.frozen:
                raise InvalidMove('%s at %r is frozen and can not be used' % (piece_to_move.__class__.__name__,piece_to_move.position) )
            
            if moveinfo.move_type == MOVE_ROTATE:
                if moveinfo.num_rotations is not None:
                    temp_direction = piece_to_move.rotation + moveinfo.num_rotations*45
                    if temp_direction >= 360:
                        temp_direction -= 360
                if moveinfo.new_direction is not None:
                    temp_direction = moveinfo.new_direction
                piece_to_move.rotation = temp_direction
            elif moveinfo.move_type == MOVE_MOVEMENT:
                piece_at_destination = self.get_board_piece(moveinfo.dest_coords)
                #TODO transport warp (transport), hole (destroy) - make attack/defend calls
                piece_to_move.perform_move(moveinfo.dest_coords, self)
            elif moveinfo.move_type == MOVE_SHOOT:
                # FIXME TODO incomplete debug code
                self.init_shots()
                print 'before shot'
                self.debug_print_shots()
                piece_to_move.shoot(self)
                print 'after shot'
                self.debug_print_shots()
                #print self.shootboard
                #self.init_shots() ## reset information?? does not get done here in case board/viewer needs to see it
                for x in self.successfully_shot_this_turn:
                    piece_to_move.shot_effect(x, self)
                self.print_board()
                self.losess()
            else:
                raise InvalidMove('debug, unhandled move type %r in board at %r' % (moveinfo.move_type, moveinfo.origin_coords) )
        
        self.turns_left = self.turns_left - 1
        if self.turns_left <= 0:
            if self.current_player == PLAYER_ONE:
                self.current_player = PLAYER_TWO
            else:
                self.current_player = PLAYER_ONE
                self.rounds_played += 1
                unfrozen_pieces=[]
                for temp_piece in self.frozen_pieces:
                    if temp_piece.unfreeze_in_round == self.rounds_played:
                        temp_piece.frozen=False
                        unfrozen_pieces.append(temp_piece)
                for temp_piece in unfrozen_pieces:
                    self.frozen_pieces.remove(temp_piece )
            self.turns_left=3
            for temp_piece in self.pieces_to_reset_after_this_turn:
                temp_piece.special_used = False
            self.pieces_to_reset_after_this_turn=[]
        self.moves_history.append(moveinfo)
        self.debug_check_positions()
        if self.lost_pieces[PLAYER_ONE]['king_piece'] != 0:
            self.winner=PLAYER_TWO
        if self.lost_pieces[PLAYER_TWO]['king_piece'] != 0:
            self.winner=PLAYER_ONE
        # debug
        #if self.winner is not None:
        #    raise Winner('Player '+ str(self.winner))
        # return move result/changes (for UI, view, etc.)?
        # E.g. red Wins, transport effect, etc.

    def print_board(self):
        """Dumb diagnostic, dumps to stdout, ignores rotation information!
        """
        temp_str=[]
        if self.winner is not None:
            temp_str.append('Game Over! Winner: '+ str(self.winner))
        temp_str.append('Round: %d\n' % (self.rounds_played+1))
        #'Player Turn: %d' % self.current_player
        temp_str.append('Player Turn: %s\n' % (player_map[self.current_player][0]))
        temp_str.append('Moves Left: %d\n' % (self.turns_left))
        
        #x_len, y_len = self.board_size
        current_row=0
        for temp_row in self.board:
            temp_str.append('%2d'%current_row)
            temp_str.append('|')
            for temp_col in temp_row:
                if is_a_blank_square(temp_col):
                    temp_str.append(EMPTY_SQUARE_STR)
                else:
                    #print temp_col
                    #temp_str.append(temp_col.text_repr)
                    if isinstance(temp_col, player_piece):
                        if temp_col.player_number == PLAYER_TWO:
                            temp_piece_string=temp_col.text_repr.lower()
                        elif temp_col.player_number == PLAYER_ONE:
                            temp_piece_string=temp_col.text_repr.upper()
                        temp_str.append(temp_piece_string)
                        del temp_piece_string
                    else:
                        temp_str.append(temp_col.text_repr)
            temp_str.append('|')
            temp_str.append('\n')
            current_row += 1
        print ''.join(temp_str)
                    

    def html_board(self, fileptr):
        """Dumb diagnostic, dumps to fileptr, ignores rotation information!
        """
        tile_xlen = 18
        tile_ylen = 18
        tile_xlen = 46
        tile_ylen = 46
        #tile_fname_pat = 'small_stomper%d.gif'
        #tile_fname_pat = '18x18_%d_%s%d.gif'
        tile_fname_pat = '%dx%d_%%d_%%s%%d.gif' % (tile_xlen, tile_ylen)
        print tile_fname_pat 
        #fileptr.write(html_head)
        fileptr.write(html_head % (tile_xlen, tile_ylen) )

        for temp_row in self.board:
            fileptr.write('''<tr>''')
            col_count=0
            for temp_col in temp_row:
                if is_a_blank_square(temp_col):
                   tile_fname = tile_fname_pat % (1, 'blank', 0)
                else:
                    #print temp_col.piece_name()
                    try:
                       temp_rotation = temp_col.rotation
                    except AttributeError, info:
                       temp_rotation = 0
                    if isinstance(temp_col, player_piece):
                        tile_fname = tile_fname_pat % (temp_col.player_number, temp_col.piece_name(), direction_to_order[temp_rotation])
                    elif isinstance(temp_col, hole_square) or isinstance(temp_col, warp_piece):
                        tile_fname = tile_fname_pat % (1, temp_col.piece_name(), direction_to_order[temp_rotation])
                    else:
                        tile_fname = 'missing.gif'
                #if col_count >= self.board_size[0]/2:
                #   tile_fname = 'green_' + tile_fname

                fileptr.write('''<td><img style="width: %dpx; height: %dpx;" alt="" src="./%s"></td>\n''' % (tile_xlen, tile_ylen, tile_fname) )
                col_count += 1
            fileptr.write('''</tr>\n\n''')
        fileptr.write(html_tail)



def test_some_movements():
    my_move = piece_move(move_type=MOVE_PASS)
    print 'straight print', my_move 
    print 'repr print', repr(my_move)
    my_move = piece_move(move_type=MOVE_SHOOT, origin_coords=(3,3))
    print 'straight print', my_move 
    print 'str print', str(my_move)
    print 'repr print', repr(my_move)
    my_move = piece_move(move_type=MOVE_ROTATE, origin_coords=(3,3), new_direction=NORTH_EAST)
    print 'straight print', my_move 
    print 'str print', str(my_move)
    print 'repr print', repr(my_move)
    my_move = piece_move(move_type=MOVE_MOVEMENT, origin_coords=(3,3), dest_coords=(3,5))
    print 'straight print', my_move 
    print 'str print', str(my_move)
    print 'repr print', repr(my_move)
    
    my_move = piece_move('p')
    print my_move 
    
    my_move = piece_move('pass')
    print my_move 
    
    my_move = piece_move('shoot (5,3)')
    print my_move 
    
    my_move = piece_move('s (5,3)')
    print my_move 
    
    my_move = piece_move('m (5,3) (5,5)')
    print my_move 
    
    my_move = piece_move('move (5,3) (5,5)')
    print my_move 
    
    my_move = piece_move('r (5,3) 45')
    print my_move 
    
    my_move = piece_move('rotate (5,3) 45')
    print 'straight print', my_move 
    print 'str print', str(my_move)
    print 'repr print', repr(my_move)
    
    my_move = piece_move('rotate (5,3) num_rotations=4')
    print 'straight print', my_move 
    print 'str print', str(my_move)
    print 'repr print', repr(my_move)
    
    
    test_invalid_move=True
    test_invalid_move=False
    if test_invalid_move:
        my_move = piece_move('hello')
        print my_move 

if __name__ == '__main__':
    test_some_movements()
    
    playing_board = board()
    playing_board.print_board()

    # generate lost_pieces table
    dummy_dict={}
    dummy_dict[PLAYER_ONE]={}
    dummy_dict[PLAYER_TWO]={}
    for temp_row in playing_board.board:
        for temp_col in temp_row:
            if isinstance(temp_col, player_piece):
                #print temp_col.player_number
                #print temp_col.__class__.__name__
                #dummy_dict[temp_col.player_number][temp_col.__class__.__name__]=0
                dummy_dict[PLAYER_ONE][temp_col.__class__.__name__]=0
                dummy_dict[PLAYER_TWO][temp_col.__class__.__name__]=0
    print 'dummy_dict=', dummy_dict
                
    print direction_to_order
    
    for x in DIRECTION_ORDER:
        print x, calculate_reverse_beam_direction(x),
        print direction_to_string[x], direction_to_string[calculate_reverse_beam_direction(x)]
    
    
    print 'DIRECTION_ORDER', DIRECTION_ORDER
    print DIRECTION_ORDER_STR 
    for x in DIRECTION_ORDER:
        print x, direction_to_string[x]
