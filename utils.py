
from config       import *

def get_mouse_pos(units):
    # units == "tiles" means the 'in-game' units
    # units == "pixels" means the 'pygame' units
    mouse_pos = np.array(pygame.mouse.get_pos(), dtype='float')
    if units == "pixels":
        return mouse_pos
    else:
        return np.divide(mouse_pos, pixel_factor)

def parse_data(raw_line):
  #print(raw_line)
  raw_line=raw_line.replace('\n', ' ')
  strip_line=raw_line.replace('\t',' ')
  strip_line=strip_line.replace(',',' ') #comma separated values
  split_line=strip_line.split(' ')
  data_list=[]
  for item in split_line:
    if item!='':
      data_list.append(item)
  return data_list
def sublist(list1,x1,x2,y1,y2):
  sublist=[]
  for i in range(x1,x2):
    sublist.append(list1[i][y1:y2]) #doesn't include list1[i][y2]
  return sublist

class Parser(object):
    def __init__(self,document_name):
        self.doc=open(document_name,'r')
        self.doc_lines=self.doc.readlines()
        #print(self.doc_lines)
        self.line= -1
    def parse_lines(self):	#returns integer 0 if at end of document
        try:
            self.doc_lines[self.line+1]
        except:
            return 0
        else:
            self.line += 1
        #print(self.doc_lines[self.line]+'data')
        return self.doc_lines[self.line].rstrip('\n')
    def close(self):
        self.doc.close()

def make_rect(xy, wh):
    x, y = [xy[0], xy[0] + wh[0]], [xy[1], xy[1] + wh[1]]
    rect = PatchExt([x, y]) # xxyy_limits' a sequence of two pairs: [[x_low, x_high], [y_low, y_high]]
    return rect

class PatchExt(m2d.geometry.Patch):
    
    def __init__(self, xxyy_limits):
        """Specified by 'xxyy_limits' a sequence of two pairs: [[x_low,
        x_high], [y_low, y_high]]."""
        arr = np.array(xxyy_limits)
        if len(arr) == 2:
            self.xlims, self.ylims = arr
        elif len(arr) == 4:
            self.xlims, self.ylims = arr[0:2], arr[2:4]

        # check for correct order
        if not (self.xlims[1] > self.xlims[0]):
            pass
            # pdb.set_trace()
        if not (self.ylims[1] > self.ylims[0]):
            pass
            # pdb.set_trace()

    def collide(self, other):
        """Compute the intersection with 'other'. If overlapping a Patch will
        be returned representing the overlap. Otherwise 'None' is
        returned.
        """
        xlims_new = max(self.xlims[0], other.xlims[0]), min(self.xlims[1], other.xlims[1])
        ylims_new = max(self.ylims[0], other.ylims[0]), min(self.ylims[1], other.ylims[1])
        if xlims_new[0] < xlims_new[1] and ylims_new[0] < ylims_new[1]:
            return True
        else:
            return False

    def get_center(self):
            """ get the center
            """
            center = 0.5 * np.array([np.sum(self.xlims), np.sum(self.ylims)])
            return center
    center = property(get_center)

    def get_bottom(self):
        """ bottom is w.r.t. screen (user)
        """
        out = self.ylims[-1]
        return out
    
    def get_top(self):
        """ top is w.r.t. screen (user)
        """
        out = self.ylims[0]
        return out

    def get_left(self):
        """ left is w.r.t. screen (user)
        """
        out = self.xlims[0]
        return out

    def get_right(self):
        """ right is w.r.t. screen (user)
        """
        out = self.xlims[-1]
        return out

    bottom = property(get_bottom)
    top    = property(get_top)
    left   = property(get_left)
    right  = property(get_right)
    x      = left
    y      = top

    def get_width(self):
        out = self.right - self.left
        return out

    def get_height(self):
        out = self.bottom - self.top
        return out

    width  = property(get_width)
    height = property(get_height)

    def convert_to_pygame_rect(self):
        # REMEMBER: pygame Rect's truncate to the nearest integer
        out = pygame.Rect(self.left, self.top, self.width, self.height)
        return out

    def convert_to_screen_rect(self, screenLocation):
        """ take a rect in game units and convert to pixel units
        as well as translate onto visible screen """
        pos = np.array([self.x, self.y])
        size = np.array([self.width, self.height])

        pos_screen = np.array(screenLocation, dtype='float')
        factor = np.array((pixelsPerTileWidth, pixelsPerTileHeight))

        new_size = np.multiply(size, factor) #check syntax
        new_pos = np.multiply(pos - pos_screen, factor)
        xxyy_limits = corner_to_limits(new_pos, new_size)
        out = PatchExt(xxyy_limits)
        return out

    def scale(self, percent):
        # scale by percent but keep the center the same
        # returns a new rect object
        center = self.center
        new_w = (1.0 + percent) * self.width
        new_h = (1.0 + percent) * self.height

        lt = center - 0.5 * np.array([new_w, new_h])
        wh = [new_w, new_h]

        x, y = [lt[0], lt[0] + wh[0]], [lt[1], lt[1] + wh[1]]
        new_rect = PatchExt([x, y])
        return new_rect

    # required functions for pygame Rect & quadtree compliance
    def collidelist(self, list):
        idx = -1
        for counter, rect in enumerate(list):
            if self.collide(rect):
                idx = counter
                break
        return idx

    def collidelistall(self, list):
        # output: indices
        pass

    def union(self, rect):
        # output: Rect
        pass

    def union_ip(self, rect):
        # output: None
        pass



def process_file_name(s1):
    """ Process file name for os independence, as well as replace [GAME_ROOT] with the variable
    """
    s2 = s1.replace("[GAME_ROOT]", "/")
    s3 = s2.replace("\\", "/")
    split = s3.split("/")
    out = os.path.join(*split)
    return out

def make_del_msg(obj):
    tup = ("DEL_OBJ", obj)
    return tup

def make_sound_msg(name):
    tup = ("PLAY_SOUND", name)
    return tup

def make_music_msg(name):
    return ("CHANGE_MUSIC", name)

def make_gen_msg(obj):
    tup = ("GEN_OBJ", obj)
    return tup

def die(obj):
    """ add self to the del list """
    tup = make_del_msg(obj)
    MESSAGES.put(tup)

    if hasattr(obj, "deathSoundFX"):
        tup = make_sound_msg(obj.deathSoundFX)
        MESSAGES.put(tup)
    

def get_game_time():
    return DATA["game_time"]

def get_game_objects():
    return DATA["game_objects_ref"]

def get_screen_location():
    return DATA["screen_location"]

def center_to_limits(input):
    center, size = np.array(input[0]), np.array(input[1])
    low = center - 0.5 * size
    high = center + 0.5 * size
    xxyy_limits = np.array([low[0], high[0], low[1], high[1]])
    return xxyy_limits

def corner_to_limits(corner, size):
    xxyy_limits = np.array([corner[0], corner[0]+size[0], corner[1], corner[1]+size[1]])
    return xxyy_limits

def get_heading(m2d_tf):
    heading = m2d_tf.orient.angle
    return heading

# https://www.pygame.org/wiki/QuadTree
# http://www.pygame.org/project-Quadtree+test-1691-.html 

# ------------------------------------------------------------------------------
# Quadtrees!
class QuadTree(object):
    """An implementation of a quad-tree.
 
    This QuadTree started life as a version of [1] but found a life of its own
    when I realised it wasn't doing what I needed. It is intended for static
    geometry, ie, items such as the landscape that don't move.
 
    This implementation inserts items at the current level if they overlap all
    4 sub-quadrants, otherwise it inserts them recursively into the one or two
    sub-quadrants that they overlap.
 
    Items being stored in the tree must be a pygame.Rect or have have a
    .rect (pygame.Rect) attribute that is a pygame.Rect
	    ...and they must be hashable.
    
    Acknowledgements:
    [1] http://mu.arete.cc/pcr/syntax/quadtree/1/quadtree.py
    """

    def __init__(self, items, depth=8, bounding_rect=None):
        """Creates a quad-tree.
 
        @param items:
            A sequence of items to store in the quad-tree. Note that these
            items must be a pygame.Rect or have a .rect attribute.
            
        @param depth:
            The maximum recursion depth.
            
        @param bounding_rect:
            The bounding rectangle of all of the items in the quad-tree. For
            internal use only.
        """

        # The sub-quadrants are empty to start with.
        self.nw = self.ne = self.se = self.sw = None
        
        # If we've reached the maximum depth then insert all items into this
        # quadrant.
        depth -= 1
        if depth == 0 or not items:
            self.items = items
            return
 
        # Find this quadrant's centre.
        if bounding_rect:
            bounding_rect = pygame.Rect( bounding_rect )
        else:
            # If there isn't a bounding rect, then calculate it from the items.
            bounding_rect = pygame.Rect( items[0].pygame_rect )
            for item in items[1:]:
                bounding_rect.union_ip( item.pygame_rect )
        cx = self.cx = bounding_rect.centerx
        cy = self.cy = bounding_rect.centery

        self.items = []
        nw_items = []
        ne_items = []
        se_items = []
        sw_items = []

        for item in items:
            # Which of the sub-quadrants does the item overlap?
            in_nw = item.pygame_rect.left <= cx and item.pygame_rect.top <= cy
            in_sw = item.pygame_rect.left <= cx and item.pygame_rect.bottom >= cy
            in_ne = item.pygame_rect.right >= cx and item.pygame_rect.top <= cy
            in_se = item.pygame_rect.right >= cx and item.pygame_rect.bottom >= cy
                
            # If it overlaps all 4 quadrants then insert it at the current
            # depth, otherwise append it to a list to be inserted under every
            # quadrant that it overlaps.
            if in_nw and in_ne and in_se and in_sw:
                self.items.append(item)
            else:
                if in_nw: nw_items.append(item)
                if in_ne: ne_items.append(item)
                if in_se: se_items.append(item)
                if in_sw: sw_items.append(item)
            
        # Create the sub-quadrants, recursively.
        if nw_items:
            self.nw = QuadTree(nw_items, depth, (bounding_rect.left, bounding_rect.top, cx, cy))
        if ne_items:
            self.ne = QuadTree(ne_items, depth, (cx, bounding_rect.top, bounding_rect.right, cy))
        if se_items:
            self.se = QuadTree(se_items, depth, (cx, cy, bounding_rect.right, bounding_rect.bottom))
        if sw_items:
            self.sw = QuadTree(sw_items, depth, (bounding_rect.left, cy, cx, bounding_rect.bottom))
 
 
    def hit(self, rect):
        """Returns the items that overlap a bounding rectangle.
 
        Returns the set of all items in the quad-tree that overlap with a
        bounding rectangle.
        
        @param rect:
            The bounding rectangle being tested against the quad-tree. This
            must possess left, top, right and bottom attributes.
        """

        # Find the hits at the current level.
        hits = set( self.items[n] for n in rect.collidelistall( [item.pygame_rect for item in self.items] ) )
        
        # Recursively check the lower quadrants.
        if self.nw and rect.left <= self.cx and rect.top <= self.cy:
            hits |= self.nw.hit(rect)
        if self.sw and rect.left <= self.cx and rect.bottom >= self.cy:
            hits |= self.sw.hit(rect)
        if self.ne and rect.right >= self.cx and rect.top <= self.cy:
            hits |= self.ne.hit(rect)
        if self.se and rect.right >= self.cx and rect.bottom >= self.cy:
            hits |= self.se.hit(rect)

        return hits