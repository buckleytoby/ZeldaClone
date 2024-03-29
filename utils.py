
from config       import *

def rotate_surfs(face, surfs):
    # rotate surfs 3 times by 90 degrees each 
    # surfs := list of surfs
    out = {}
    out[face] = surfs

    for i in range(3):
        new_face = (face + 1) % 4 # animation face enum is set up to be counter-clockwise
        out[new_face] = [pygame.transform.rotate(surf, 90) for surf in out[face]]
        face = new_face

    return out

def get_mouse_pos(units):
    # units == "tiles" means the 'in-game' units
    # units == "pixels" means the 'pygame' units
    mouse_pos = np.array(pygame.mouse.get_pos(), dtype='float')
    if units == "pixels":
        return mouse_pos
    else:
        return np.divide(mouse_pos, pixel_factor)

def daemon_timer(*args, **kwargs):
    # makes it so the thread will auto-shutdown when sys.exit
    th = threading.Timer(*args, **kwargs)
    th.daemon = True
    th.start()
    return th

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
    
    def __init__(self, obj):
        """Specified by 'xxyy_limits' a sequence of two pairs: [[x_low,
        x_high], [y_low, y_high]]."""
        if isinstance(obj, PatchExt):
            arr = obj.get_xxyy_limits_copy()
        else:
            arr = obj[:]
        if len(arr) == 2:
            self.xlims, self.ylims = arr
        elif len(arr) == 4:
            self.xlims, self.ylims = arr[0:2], arr[2:4]

        # check for correct order
        # if not (self.xlims[1] > self.xlims[0]):
        #     pass
        #     # pdb.set_trace()
        # if not (self.ylims[1] > self.ylims[0]):
        #     pass
            # pdb.set_trace()

    def collide(self, other):
        """Compute if self collides with other
        if (rect1.x < rect2.x + rect2.width &&
            rect1.x + rect1.width > rect2.x &&
            rect1.y < rect2.y + rect2.height &&
            rect1.y + rect1.height > rect2.y) {
                // collision detected!
            }
        """
        if self.xlims[0] < other.xlims[1] and self.xlims[1] > other.xlims[0] and \
           self.ylims[0] < other.ylims[1] and self.ylims[1] > other.ylims[0]:
            return True
        else:
            return False

    def get_center(self):
            """ get the center
            """
            center = 0.5 * np.array([self.xlims[0] + self.xlims[1], self.ylims[0] + self.ylims[1]])
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

    def set_bottom(self, y):
        """ bottom is w.r.t. screen (user)
        """
        self.ylims[-1] = y
    
    def set_top(self, y):
        """ top is w.r.t. screen (user)
        """
        self.ylims[0] = y

    def set_left(self, x):
        """ left is w.r.t. screen (user)
        """
        self.xlims[0] = x

    def set_right(self, x):
        """ right is w.r.t. screen (user)
        """
        self.xlims[-1] = x

    bottom = property(get_bottom, set_bottom)
    top    = property(get_top, set_top)
    left   = property(get_left, set_left)
    right  = property(get_right, set_right)
    x      = left
    y      = top
    X      = right
    Y      = bottom

    def get_centerx(self):
        return 0.5 * (self.x + self.X)

    def get_centery(self):
        return 0.5 * (self.y + self.Y)

    centerx = property(get_centerx)
    centery = property(get_centery)

    def get_width(self):
        out = self.right - self.left
        return out

    def get_height(self):
        out = self.bottom - self.top
        return out

    def set_width(self, w):
        self.right = self.left + w

    def set_height(self, h):
        self.bottom = self.top + h

    width  = property(get_width, set_width)
    height = property(get_height, set_height)

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

        new_size = np.multiply(size, pixel_factor) #check syntax
        new_pos = np.multiply(pos - pos_screen, pixel_factor)
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
        # collidelist(list) -> index
        idx = -1
        for counter, rect in enumerate(list):
            if self.collide(rect):
                idx = counter
                break
        return idx

    def collidelistall(self, list):
        # test if all rectangles in a list intersect
        # collidelistall(list) -> indices

        # Returns a list of all the indices that contain rectangles that collide with the Rect.
        #  If no intersecting rectangles are found, an empty list is returned.
        indices = []
        for counter, rect in enumerate(list):
            if self.collide(rect):
                indices.append(counter)
        return indices

    def union(self, rect):
        # output: Rect
        x = min(self.x, rect.x)
        y = min(self.y, rect.y)
        X = max(self.x, rect.x)
        Y = max(self.y, rect.y)
        pass

    def union_ip(self, rect):
        # output: None
        if self.xlims[0] < rect.xlims[0]:
            x = self.xlims[0]
        else:
            x = rect.xlims[0]

        if self.xlims[1] > rect.xlims[1]:
            X = self.xlims[1]
        else:
            X = rect.xlims[1]

        if self.ylims[0] < rect.ylims[0]:
            y = self.ylims[0]
        else:
            y = rect.ylims[0]

        if self.ylims[1] > rect.ylims[1]:
            Y = self.ylims[1]
        else:
            Y = rect.ylims[1]

        self.xlims[0] = x
        self.ylims[0] = y
        self.xlims[1] = X
        self.ylims[1] = Y

    def get_xxyy_limits(self):
        return (self.xlims, self.ylims)

    xxyy_limits = property(get_xxyy_limits)

    def get_xxyy_limits_copy(self):
        return (np.array(self.xlims), np.array(self.ylims))

    def copy(self):
        return PatchExt(self.xxyy_limits)

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

def get_trigger_area(name):
    dd = DATA["trigger_areas_ref"]
    if name in dd:
        return dd[name]
    else:
        return None

def get_game_time():
    return DATA["game_time"]

def get_factories():
    return DATA["factories_ref"]

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
            items must have a .patch_rect attribute.
            
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
        self.depth = depth - 1
        if self.depth == 0 or not items:
            self.items = items
            return
 
        # Find this quadrant's centre.
        if bounding_rect:
            bounding_rect = PatchExt( bounding_rect )
        else:
            # If there isn't a bounding rect, then calculate it from the items.
            bounding_rect = PatchExt( items[0].patch_rect )
            for item in items[1:]:
                bounding_rect.union_ip( item.patch_rect )
        self.bounding_rect = bounding_rect
        cx = self.cx = 0.5 * (bounding_rect.xlims[0] + bounding_rect.xlims[1])
        cy = self.cy = 0.5 * (bounding_rect.ylims[0] + bounding_rect.ylims[1])

        self.items = []
        nw_items = []
        ne_items = []
        se_items = []
        sw_items = []

        for item in items:
            # Which of the sub-quadrants does the item overlap?
            # in_nw = item.patch_rect.left <= cx and item.patch_rect.top <= cy
            # in_sw = item.patch_rect.left <= cx and item.patch_rect.bottom >= cy
            # in_ne = item.patch_rect.right >= cx and item.patch_rect.top <= cy
            # in_se = item.patch_rect.right >= cx and item.patch_rect.bottom >= cy
            in_nw = item.patch_rect.xlims[0] <= cx and item.patch_rect.ylims[0] <= cy
            in_sw = item.patch_rect.xlims[0] <= cx and item.patch_rect.ylims[1] >= cy
            in_ne = item.patch_rect.xlims[1] >= cx and item.patch_rect.ylims[0] <= cy
            in_se = item.patch_rect.xlims[1] >= cx and item.patch_rect.ylims[1] >= cy
                
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
            self.nw = QuadTree(nw_items, self.depth, (bounding_rect.xlims[0], bounding_rect.ylims[0], cx, cy))
        if ne_items:
            self.ne = QuadTree(ne_items, self.depth, (cx, bounding_rect.ylims[0], bounding_rect.xlims[1], cy))
        if se_items:
            self.se = QuadTree(se_items, self.depth, (cx, cy, bounding_rect.xlims[1], bounding_rect.ylims[1]))
        if sw_items:
            self.sw = QuadTree(sw_items, self.depth, (bounding_rect.xlims[0], cy, cx, bounding_rect.ylims[1]))

    def cleanup(self, gos):
        # recursive function to remove items that have moved and return the set
        new_items = [item for item in self.items if item.id not in gos]
        hits = set( gos[key] for key in gos if gos[key] in self.items )
        self.items = new_items

        # Recursively check the lower quadrants.
        if self.nw: hits |= self.nw.cleanup(gos)
        if self.sw: hits |= self.sw.cleanup(gos)
        if self.ne: hits |= self.ne.cleanup(gos)
        if self.se: hits |= self.se.cleanup(gos)

        return hits

    def place(self, items):
        # recursive function to place items
        
        if self.depth == 0 or not items:
            # pdb.set_trace()
            [self.items.append(item) for item in items if item not in self.items]
            return

        nw_items = []
        ne_items = []
        se_items = []
        sw_items = []

        for item in items:
            # Which of the sub-quadrants does the item overlap?
            in_nw = item.patch_rect.xlims[0] <= self.cx and item.patch_rect.ylims[0] <= self.cy
            in_sw = item.patch_rect.xlims[0] <= self.cx and item.patch_rect.ylims[1] >= self.cy
            in_ne = item.patch_rect.xlims[1] >= self.cx and item.patch_rect.ylims[0] <= self.cy
            in_se = item.patch_rect.xlims[1] >= self.cx and item.patch_rect.ylims[1] >= self.cy
                
            # If it overlaps all 4 quadrants then insert it at the current
            # depth, otherwise append it to a list to be inserted under every
            # quadrant that it overlaps.
            if in_nw and in_ne and in_se and in_sw:
                if item not in self.items: self.items.append(item)
            else:
                if in_nw: nw_items.append(item)
                if in_ne: ne_items.append(item)
                if in_se: se_items.append(item)
                if in_sw: sw_items.append(item)
            
        # place or create the sub-quadrants, recursively.
        if self.nw and nw_items:
            self.nw.place(nw_items)
        elif nw_items:
            self.nw = QuadTree(nw_items, self.depth, (self.bounding_rect.xlims[0], self.bounding_rect.ylims[0], self.cx, self.cy))

        if self.ne and ne_items:
            self.ne.place(ne_items)
        elif ne_items:
            self.ne = QuadTree(ne_items, self.depth, (self.cx, self.bounding_rect.ylims[0], self.bounding_rect.xlims[1], self.cy))

        if self.se and se_items:
            self.se.place(se_items)
        elif se_items:
            self.se = QuadTree(se_items, self.depth, (self.cx, self.cy, self.bounding_rect.xlims[1], self.bounding_rect.ylims[1]))

        if self.sw and sw_items:
            self.sw.place(sw_items)
        elif sw_items:
            self.sw = QuadTree(sw_items, self.depth, (self.bounding_rect.xlims[0], self.cy, self.cx, self.bounding_rect.ylims[1]))
 
    def update(self, gos):
        """ update items indicated by keys, this way only items that move will update.
        
        steps
        1. remove items recursively
        2. reinsert from top-level
        """
        if gos is not None:
            hits = self.cleanup(gos)
            # only place the gos that were already in the tree
            # this way items don't accidentally get re-added
            self.place(list(hits))

    def add(self, gos):
        if gos is not None:
            go_list = [gos[key] for key in gos]
            self.place(go_list)

    def remove(self, gos):
        if gos is not None:
            self.cleanup(gos)
 
    def hit(self, rect):
        """Returns the items that overlap a bounding rectangle.
 
        Returns the set of all items in the quad-tree that overlap with a
        bounding rectangle.
        
        @param rect:
            The bounding rectangle being tested against the quad-tree. This
            must possess left, top, right and bottom attributes.
        """

        # Find the hits at the current level.
        ls = [item.patch_rect for item in self.items]
        indices = rect.collidelistall( ls )
        hits = set( self.items[n] for n in indices)
        
        # Recursively check the lower quadrants.
        if self.nw and rect.xlims[0] <= self.cx and rect.ylims[0] <= self.cy:
            hits |= self.nw.hit(rect)
        if self.sw and rect.xlims[0] <= self.cx and rect.ylims[1] >= self.cy:
            hits |= self.sw.hit(rect)
        if self.ne and rect.xlims[1] >= self.cx and rect.ylims[0] <= self.cy:
            hits |= self.ne.hit(rect)
        if self.se and rect.xlims[1] >= self.cx and rect.ylims[1] >= self.cy:
            hits |= self.se.hit(rect)

        return hits

class Timer(threading.Timer):
    # threading Timer object but with a clock so you can query the passed time
    def __init__(self, *args):
        self.start_time = 0.0
        super().__init__(*args)

    def start(self):
        self.start_time = pygame.time.get_ticks() / 1000.0
        super().start()

    def get_elapsed_time(self):
        dt = pygame.time.get_ticks() / 1000.0 - self.start_time
        return dt

class Cooldown():
    # class used to define a cooldown timer
    def __init__(self, cooldown, use_fcn):
        self.cooldown = cooldown
        self.use_fcn = use_fcn

        self.cooling_down = False

    def start(self, **kwargs):
        if not self.cooling_down:
            success = self.use_fcn(**kwargs) # returns the made object if succesful, otherwise None
            if success:
                self.cooldowner()

    def cooldowner(self):
        """ spool up a thread """
        self.cooling_down = True
        # BUG: this is real time and not pygame time
        self.timer = Timer(self.cooldown, self.reset)
        self.timer.start()
        
    def reset(self):
        self.cooling_down = False