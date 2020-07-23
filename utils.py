
from config       import *



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

def make_gen_msg(obj):
    tup = ("GEN_OBJ", obj)
    return tup

def die(obj):
    """ add self to the del list """
    tup = make_del_msg(obj)
    MESSAGES.put(tup)

def get_game_time():
    return DATA["game_time"]

def get_game_objects():
    return DATA["game_objects_ref"]

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