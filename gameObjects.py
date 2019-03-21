
from config       import *
from AI           import *
from utils        import *


class Factory(object):
  # generic factory class
  def __init__(self, creator):
    self.creator = creator
    self.values = {}
    
  def create(self):
    created = self.creator()
    # set the values
    for key in self.values:
      try:
        setattr(created, key, self.values[key]) #equivalent to self.{key} = value
      except:
        pdb.set_trace()
    
    return created


class GameObjectFactory(Factory):
  # factory class for creating game objects
  def __init__(self):
    super(GameObjectFactory, self).__init__(GameObject) #check syntax
    
  def create(self, x, y):
    self.values['x'] = x
    self.values['y'] = y
    self.values['old_x'] = x
    self.values['old_y'] = y
    created = super(GameObjectFactory, self).create()
    return created
  
  
class SoldierFactory(GameObjectFactory):
  def __init__(self):
    super(SoldierFactory, self).__init__()
    self.values['width']      = 1.0
    self.values['height']     = 1.0
    self.values['artWidth']      = 1.0 * 2
    self.values['artHeight']     = 1.5 * 2
    self.values['mass']       = 100.0 # kg
    self.values['pixelWidth'] = 16 # size of the sprite image
    self.values['pixelHeight'] = 24 # size of the sprite image
    self.values['max_velocity'] = 2.0 #m/s
    self.values['objectType'] = 'Soldier'
    self.values['attack'] = self.attack

  
  def create(self, x, y):
    object = super(SoldierFactory, self).create(x, y)
    # callbacks
    getattr(object, 'callbacks')['attack'] = self.attack #unbound, but should be ok
    # setup
    object.setSpriteStatus(True, 'Soldier')
    return object
  
  def attack(self):
    pass

class PlayerFactory(SoldierFactory):
  def __init__(self):
    super(PlayerFactory, self).__init__()
    self.values['max_velocity'] = 6.0 #m/s
    self.values['artWidth']      = 1.0
    self.values['artHeight']     = 1.5
  
  
  
  
class Animation(object):
  left = 0
  down = 1
  right = 2
  up = 3
  def __init__(self):
    self.animationIndex = 0
    self.face = Animation.down
    self.index2sprite = np.array(4*[[0,0,1,1,2,2,1,1,0,0,3,3,4,4,3,3]])
    self.index2sprite[0] += 10
    self.index2sprite[2] += 5

  def updateSprite(self, dx, dy):
    #animation
    if dx > 0:
      if self.face != Animation.right: #face: 0-left, 1-down, 2-right, 3-up
        self.face = Animation.right
      self.animationIndex += 1
    elif dx < 0:
      if self.face!=Animation.left:
        self.face=Animation.left
      self.animationIndex += 1
    elif dy > 0:
      if self.face != Animation.down:
        self.face = Animation.down
      self.animationIndex += 1
    elif dy < 0:
      if self.face != Animation.up:
        self.face = Animation.up
      self.animationIndex += 1
    elif dx == 0 and dy == 0:
      self.animationIndex = 0
    self.animationIndex %= self.index2sprite.shape[1]
    
  def getSpriteIndex(self):
    return self.index2sprite[self.face][self.animationIndex]

class GameObject(object):
  # class for any objects found in the game, 
  # basically if it has a hitbox, it's a game object
  id = -1
  def __init__(self):
    GameObject.id += 1
    self.id = GameObject.id
    #-------------- default values --------------
    # hitbox
    self.drawHitBox = False
    self.x = 0.0
    self.y = 0.0
    self.old_x = 0.0
    self.old_y = 0.0
    self.dx = 0.0
    self.dy = 0.0
    self.dx_actual = 0.0
    self.dy_actual = 0.0
    self.width = 0.0
    self.height = 0.0
    # physics
    self.mass = 70.0
    self.friction = 0.01
    # visuals
    self.hasSprite = False #False --> invisible box
    self.drawn = False
    self.spriteID = 0
    self.animation  = None
    self.artWidth = 0.0
    self.artHeight = 0.0
    self.artXOffset = 0.0
    self.artYOffset = 0.0
    #------------------------------------------
    # intelligence
    self.AI = AI(self)
    self.callbacks = {}
    
  def setSpriteStatus(self, hasSprite=False, spriteType=None):
    if hasSprite:
      self.hasSprite = True
      self.spriteType = spriteType
      self.animation = Animation()
    else:
      self.hasSprite = False
      del self.animation; self.animation = None

  def gen_art_frame(self):
    """ generate the art-frame using the offsets
    """
    pos = m2d.Vector([self.artXOffset, self.artYOffset])
    orient = m2d.Orientation(0.0)
    tf = m2d.Transform(pos, orient)
    
  def getArtPosition_tiles(self):
    """ get the art-frame in map-frame. Unit: tiles
    ex:
    artWidth = 1.5
    width = 1.0
    offset = 0.5
    artX = x - 0.5
    """
    artXOffset = self.artWidth - self.width
    artYOffset = self.artHeight - self.height
    artX = self.x - artXOffset
    artY = self.y - artYOffset
    return artX, artY
    
  def getArtPosition_pixels(self):
    artX, artY = self.getArtPosition_tiles()
    pixelX = int(artX*pixelsPerTileWidth)
    pixelY = int(artY*pixelsPerTileHeight)
    return (pixelX, pixelY)

  def update(self, seconds):
    # update actual movement
    self.dx_actual = self.x - self.old_x
    self.dy_actual = self.y - self.old_y
    self.old_x = self.x
    self.old_y = self.y

  def get_position(self):
    return np.array([self.x, self.y])
  position = property(get_position)

  def get_overlap_tiles(self):
    """ get all tile indices which overlap in the form out = [[idx_x1, idx_y1], ..., [idx_xn, idx_yn]]
    """
    rect = self.rect
    xmin = int(np.floor(rect.left))
    xmax = int(np.ceil(rect.right) + 1)
    ymin = int(np.floor(rect.top))
    ymax = int(np.ceil(rect.bottom) + 1)
    X, Y = np.mgrid[xmin:xmax:1, ymin:ymax:1]
    indices = np.vstack([X.ravel(), Y.ravel()]).T
    return indices

  def get_rect_total_movement(self):
    """ get pygame Rect of the object between last position and this position
    """
    # TODO
    lt = [self.x, self.y]
    wh = [self.width, self.height]
    #rect = pygame.Rect(lt, wh) # Rect(left, top, width, height) -> Rect
    x, y = [lt[0], lt[0] + wh[0]], [lt[1], lt[1] + wh[1]]
    rect = PatchExt([x, y]) # xxyy_limits' a sequence of two pairs: [[x_low, x_high], [y_low, y_high]]
    return rect

  def get_rect(self):
    """ get pygame Rect of the object's footprint. i.e. the portion that can be collided with.
    """
    lt = [self.x, self.y]
    wh = [self.width, self.height]
    #rect = pygame.Rect(lt, wh) # Rect(left, top, width, height) -> Rect
    x, y = [lt[0], lt[0] + wh[0]], [lt[1], lt[1] + wh[1]]
    rect = PatchExt([x, y]) # xxyy_limits' a sequence of two pairs: [[x_low, x_high], [y_low, y_high]]
    return rect

  def get_rect_art(self):
    """ get pygame Rect of the object's art. i.e. the portion that can be collided with.
    """
    lt = self.getArtPosition_tiles()
    wh = [self.artWidth, self.artHeight]
    #rect = pygame.Rect(lt, wh) # Rect(left, top, width, height) -> Rect
    x, y = [lt[0], lt[0] + wh[0]], [lt[1], lt[1] + wh[1]]
    rect = PatchExt([x, y]) # xxyy_limits' a sequence of two pairs: [[x_low, x_high], [y_low, y_high]]
    return rect
  rect = property(get_rect)
  rect_art = property(get_rect_art)

  def intersect(self, other, art=False):
    """ intersect with other, other can be an object which contains rect, or a Patch directly
    """
    if art:
      if isinstance(other, PatchExt): out = self.rect_art.intersect(other)
      else: out = self.rect_art.intersect(other.rect_art)
    else:
      if isinstance(other, PatchExt): out = self.rect.intersect(other)
      else: out = self.rect.intersect(other.rect)
    return out
  
  def get_velocity(self):
    out = np.array([self.dx, self.dy])
    return out
  velocity = property(get_velocity)

  def get_velocity_mag(self):
    vv = np.linalg.norm(self.velocity)
    return vv
  velocity_mag = property(get_velocity_mag)

  def get_unit_velocity(self):
    if np.isclose(self.velocity_mag, 0.0):
      out = np.zeros(2)
    else:
      out = np.array(self.velocity) / self.velocity_mag
    return out
  unit_velocity = property(get_unit_velocity)

  def get_momentum(self):
    out = self.mass * self.velocity_mag
    return out
  momentum = property(get_momentum)
    
  def get_center_of_mass(self):
    out = self.rect.center
    return out
  center_of_mass = property(get_center_of_mass)

  def com_vector(self, other):
    """ get vector from my center of mass to 'other's center of mass
    """
    # final - initial == 'to' - 'from'
    out = np.array(other.center_of_mass) - np.array(self.center_of_mass) 
    return out
    
  
