
from config       import *
import AI
import math_utils
from utils        import *


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
    self.time_elapsed = 0.0
    self.update_rate = 0.1

  def updateSprite(self, seconds, dx, dy):
    # check if elapsed time surpasses update rate
    self.time_elapsed += seconds
    if self.time_elapsed > self.update_rate:
      self.time_elapsed -= self.update_rate
      # increment animation index for each update frame
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
        # self.animationIndex = 0
        self.animationIndex += 1
      self.animationIndex %= self.index2sprite.shape[1]
    
  def getSpriteIndex(self):
    return self.index2sprite[self.face][self.animationIndex]

class StaticGameObject(object):
  id = -1
  def __init__(self, **kwargs):
    GameObject.id += 1
    self.id = GameObject.id
    self.type = "static_object"
    self.objectType = "" # for art purposes
    #-------------- default values --------------
    # hitbox
    self.drawHitBox = False
    self.x = 0.0
    self.y = 0.0
    self.dx = 0.0
    self.dy = 0.0
    self.dx_actual = 0.0
    self.dy_actual = 0.0
    self.width = 0.0
    self.height = 0.0
    self.heading = 0.0 # from 0 to 2pi
    self.patch_rect = self.make_patch_rect()
    self.pygame_rect = self.patch_rect.convert_to_pygame_rect()
    self.pygame_screen_rect = self.patch_rect.convert_to_screen_rect([0, 0]).convert_to_pygame_rect()
    # visuals
    self.visible = False
    self.has_sprite = False #False --> rect
    self.rgb = (0, 200, 0)
    self.drawn = False
    self.spriteID = 0
    self.animation  = None
    self.artWidth = 0.0
    self.artHeight = 0.0
    self.artXOffset = 0.0
    self.artYOffset = 0.0

    # instantiate from rect
    if "rect" in kwargs:
      rect = kwargs.pop("rect")
      kwargs["x"] = rect.x
      kwargs["y"] = rect.y
      kwargs["width"] = rect.width
      kwargs["height"] = rect.height
      
    #------------------------------------------
    # over-ride default values
    self.__dict__.update(kwargs)
    
  def setSpriteStatus(self, visible, has_sprite=False):
    if visible:
      self.visible = True
      if has_sprite:
        self.has_sprite = True
        self.animation = Animation()
    else:
      self.visible = False
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

  def update_heading(self, dy, dx):
    self.heading = np.arctan2(dy, dx)
    
  def reset_pos(self, new_pos):
    self.x = new_pos[0]
    self.y = new_pos[1]
  
  def get_position(self):
    return np.array([self.x, self.y])
  position = property(get_position)

  def get_center(self):
    return np.array([self.x + 0.5 * self.width, self.y + 0.5 * self.height])
    
  def get_center_tf(self):
    pos = self.get_center()
    tf = m2d.Transform(self.heading, pos)
    return tf

  def get_heading_orient(self):
    return m2d.Orientation(self.heading)

  def get_heading_unit_direction(self):
    """ returns numpy array """
    return (self.get_heading_orient() * m2d.Vector.e0).array

  def get_reach_rect(self):
    # the rect surrounding the game object that they can reach

    lt = [self.x - self.reach, self.y - self.reach]
    wh = [self.width + 2.0 * self.reach, self.height + 2.0 * self.reach]

    return make_rect(lt, wh)

  reach_rect = property(get_reach_rect)

  def make_patch_rect(self):
    lt = [self.x, self.y]
    wh = [self.width, self.height]
    return make_rect(lt, wh)

  def update_rect(self):
    self.patch_rect.x = self.x
    self.patch_rect.y = self.y
    self.patch_rect.width = self.width
    self.patch_rect.height = self.height
  
  def get_rect(self):
    """ get pygame Rect of the object's footprint. i.e. the portion that can be collided with.
    """
    #rect = pygame.Rect(lt, wh) # Rect(left, top, width, height) -> Rect
    return self.patch_rect
  
  def update_pygame_rect(self):
    """ get pygame Rect of the object's footprint. i.e. the portion that can be collided with.
    """
    #rect = pygame.Rect(lt, wh) # Rect(left, top, width, height) -> Rect
    self.pygame_rect.x = self.x
    self.pygame_rect.y = self.y
    self.pygame_rect.width = self.width
    self.pygame_rect.height = self.height
  
  def update_pygame_screen(self, screen_location):
    """ get pygame Rect of the object's footprint. i.e. the portion that can be collided with.
    """
    self.pygame_screen_rect.x = (self.x - screen_location[0]) * pixel_factor[0]
    self.pygame_screen_rect.y = (self.y - screen_location[1]) * pixel_factor[1]
    self.pygame_screen_rect.width = self.width * pixel_factor[0]
    self.pygame_screen_rect.height = self.height * pixel_factor[1]

  def get_pygame_rect(self):
    self.update_pygame_rect()
    return self.pygame_rect

  def get_rect_art(self):
    """ get pygame Rect of the object's art. i.e. the portion that can be collided with.
    """
    lt = self.getArtPosition_tiles()
    wh = [self.artWidth, self.artHeight]
    return make_rect(lt, wh)

  rect = property(get_rect)
  rect_art = property(get_rect_art)

  def calc_pygame_rect(self):
    self.pygame_rect = self.rect.convert_to_pygame_rect()
    return self.pygame_rect

class GameObject(StaticGameObject):
  # class for any objects found in the game, 
  # basically if it has a hitbox, it's a game object
  id = -1
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.type = "game_object"
    # physics
    self.moveable = True # if the object can be moved
    self.collideable = True # if the object can be collided with
    self.can_transfer_momentum = True # if the object can transfer momentum to objects it interacts with
    self.mass = 70.0
    self.friction = 0.01
    self.reach = 2.0 # tile reach for interactions
    #------------------------------------------
    # intelligence
    self.AI = AI.Basic(self)
    self.team_id = 0
    self.callbacks = {}
      
    #------------------------------------------
    # over-ride default values
    self.__dict__.update(kwargs)
    self.old_x = self.x
    self.old_y = self.y
    
  def reset_pos(self, new_pos):
    self.x = new_pos[0]
    self.y = new_pos[1]
    
    # save values
    self.old_x = self.x
    self.old_y = self.y

  def update(self, seconds):
    # update actual movement
    self.dx_actual = self.x - self.old_x
    self.dy_actual = self.y - self.old_y

    # dead-band
    if abs(self.dx_actual) < 1e-2: self.dx_actual = 0.0
    if abs(self.dy_actual) < 1e-2: self.dy_actual = 0.0

    # save values
    self.old_x = self.x
    self.old_y = self.y

    if self.dx_actual != 0.0 or self.dy_actual != 0.0:
      self.update_heading(self.dy_actual, self.dx_actual)

    if self.has_sprite:
      self.animation.updateSprite(seconds, self.dx_actual, self.dy_actual)

  @property
  def projectile_heading(self):
    if self.objectType == "Player":
      # take from mouse direction
      mouse_pos = get_mouse_pos("tiles") + get_screen_location() # from utils
      origin = self.get_center()
      vec = mouse_pos - origin
      dx, dy = vec
      return np.arctan2(dy, dx)
    else:
      return self.heading

  # # # @profile
  def get_overlap_tiles(self):
    """ get all tile indices which overlap in the form out = [[idx_x1, idx_y1], ..., [idx_xn, idx_yn]]
    """
    rect = self.rect
    xmin = int(np.floor(rect.left))
    xmax = int(np.ceil(rect.right) + 1)
    ymin = int(np.floor(rect.top))
    ymax = int(np.ceil(rect.bottom) + 1)
    # try:
    #   X, Y = np.mgrid[xmin:xmax:1, ymin:ymax:1]
    # except:
    #   pdb.set_trace()
    # indices = np.vstack([X.ravel(), Y.ravel()]).T

    length = (xmax - xmin) * (ymax - ymin)
    indices2 = np.zeros([length, 2], dtype=int)
    # using loops
    for Y in range(ymin, ymax):
      for X in range(xmin, xmax):
        x = X - xmin
        y = Y - ymin
        idx = (xmax - xmin) * (y) + x
        indices2[idx][0] = X
        indices2[idx][1] = Y

    return indices2

  def get_rect_total_movement(self):
    """ get pygame Rect of the object between last position and this position
    """
    # TODO: finish fcn
    lt = [self.x, self.y]
    wh = [self.width, self.height]
    #rect = pygame.Rect(lt, wh) # Rect(left, top, width, height) -> Rect
    return utils.make_rect(lt, wh)

  def intersect(self, other, art=False):
    """ intersect with other, other can be an object which contains rect, or a Patch directly
    """
    if art and self.has_sprite:
      if isinstance(other, PatchExt): out = self.rect_art.intersect(other)
      else: out = self.rect_art.intersect(other.rect_art)
    else:
      if isinstance(other, PatchExt): out = self.rect.intersect(other)
      else: out = self.rect.intersect(other.rect)
    return out

  def collide(self, other, art=False):
    """ intersect with other, other can be an object which contains rect, or a Patch directly
    """
    if art and self.has_sprite:
      if isinstance(other, PatchExt): out = self.rect_art.collide(other)
      else: out = self.rect_art.collide(other.rect_art)
    else:
      if isinstance(other, PatchExt): out = self.rect.collide(other)
      else: out = self.rect.collide(other.rect)

    # call callback
    if out: self.collide_callback(other)

    return out

  def collide_callback(self, other, *args):
    # function which gets called when the other object collides with this one
    pass
  
  def get_velocity(self):
    out = np.array([self.dx_actual, self.dy_actual])
    return out
  velocity = property(get_velocity)

  def get_velocity_mag(self):
    vv = np.linalg.norm(self.velocity)
    return vv
  velocity_mag = property(get_velocity_mag)

  def get_unit_velocity(self):
    out = math_utils.zero_protection_divide(np.array(self.velocity), self.velocity_mag)
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

  def dist_to_other(self, other):
    com_vector = self.com_vector(other)
    dist = np.linalg.norm(com_vector)
    return dist



class Portal(GameObject):
  def __init__(self, source, source_id, target, target_id):
    self.target = np.array(target) # center of cell
    self.source_id = source_id
    self.target_id = target_id
    self.active = True
    self.active_cooldown = 1.0 # seconds
    #
    x = source[0] + 0.25 # make half-tile sized portal centered on tile
    y = source[1] + 0.25 # make half-tile sized portal centered on tile
    #
    super().__init__(drawHitBox = False,
                     x = x,
                     y = y,
                     width = 0.5,
                     height = 0.5,
                     moveable = False,
                     rgb = ((10 + 20*source_id)%250, 0, 0)
                    )

  def activate(self, go, portals):
    # @param go: GameObject class object
    if self.active:
      go.reset_pos(self.target)
      self.active_cooldowner()
      # deactivate the target portal too
      portals[self.target_id].active = False
      portals[self.target_id].active_cooldowner()

  def active_cooldowner(self):
    """ spool up a thread """
    self.active = False
    threading.Timer(self.active_cooldown, self.reset_active).start()
        
  def reset_active(self):
    self.active = True

class HealthBar(StaticGameObject):
  def __init__(self):
    pass