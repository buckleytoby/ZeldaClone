
from config       import *
from AI           import *
import math2d as m2d


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
    created = super(GameObjectFactory, self).create()
    return created
  
  
class SoldierFactory(GameObjectFactory):
  def __init__(self):
    super(SoldierFactory, self).__init__()
    self.values['width']      = 1.0
    self.values['height']     = 1.5
    self.values['mass']       = 100.0 # kg
    self.values['pixelWidth'] = 16
    self.values['pixelHeight'] = 24
    self.values['max_velocity'] = 6.0 #m/s
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
    self.dx = 0.0
    self.dy = 0.0
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
    # intelligence
    self.AI = AI()
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
    """

    artX = self.x + self.artXOffset
    artY = self.y + self.artYOffset
    return artX, artY
    
  def getArtPosition_pixels(self):
    artX, artY = self.getArtPosition_tiles()
    pixelX = int(artX*pixelsPerTileWidth)
    pixelY = int(artY*pixelsPerTileHeight)
    return (pixelX, pixelY)

  def update(self, seconds):
    pass
    
  def get_footprint_rect(self):
    """ get pygame Rect of the object's footprint. i.e. the portion that can be collided with.
    """
    #x = [self.x, self.x + self.width]
    #y = [self.y, self.y + self.height]
    lt = [self.x, self.y]
    wh = [self.width, self.height]
    rect = pygame.Rect(lt, wh) # Rect(left, top, width, height) -> Rect
    #rect = m2d.geometry.Patch([x, y]) # xxyy_limits' a sequence of two pairs: [[x_low, x_high], [y_low, y_high]]
    return rect
  
  rect = property(get_footprint_rect)
  
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
    
  
