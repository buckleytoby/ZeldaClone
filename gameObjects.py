
from config       import *


class Factory(object):
  # generic factory class
  def __init__(self, creator):
    self.creator = creator
    self.values = {}
    
  def create(self):
    factory = self.creator()
    # set the values
    for key in self.values:
      setattr(factory, key, self.values[key]) #equivalent to self.{key} = value
    
    return factory


class GameObjectFactory(Factory):
  # factory class for creating game objects
  def __init__(self):
    super().__init__(GameObject) #check syntax
    
  def create(self, x, y):
    self.values['x'] = x
    self.values['y'] = y
    super().create()
  
  
class SoldierFactory(GameObjectFactory):
  def __init__(self):
    super().__init__()
    self.values['width'] = 2.0
    self.values['height'] = 3.0
    self.values['pixelWidth'] = 16
    self.values['pixelHeight'] = 24
    self.values['velocity'] = 1.0 #m/s
    self.values['objectType'] = 'Soldier'
  

  
  
  
  
class Animation(object):
  def __init__(self):
    self.animationIndex = 0
    self.face = ObjectArt.down
    self.index2sprite = np.array(4*[0,0,1,1,2,2,1,1,0,0,3,3,4,4,3,3])
    self.index2sprite[0] += 10
    self.index2sprite[2] += 5

  def updateSprite(self, dx, dy):
    #animation
    if dx > 0:
      if self.face != ObjectArt.right: #face: 0-left, 1-down, 2-right, 3-up
        self.face = ObjectArt.right
      self.animationIndex += 1
    elif dx < 0:
      if self.face!=ObjectArt.left:
        self.face=ObjectArt.left
      self.animationIndex += 1
    elif dy > 0:
      if self.face != Obj.down:
        self.face = Obj.down
      self.animationIndex += 1
    elif dy < 0:
      if self.face != ObjectArt.up:
        self.face = ObjectArt.up
      self.animationIndex += 1
    elif dx == 0 and dy == 0:
      self.animationIndex = 0
    self.animationIndex %= len(self.sprites[self.face])
    
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
    self.width = 0.0
    self.height = 0.0
    # visuals
    self.hasSprite = False #False --> invisible box
    self.spriteID = 0
    self.artClass  = Animation()
    self.artWidth = 0.0
    self.artHeight = 0.0
    self.artXOffset = 0.0
    self.artYOffset = 0.0
    
  def getArtPosition_tiles(self):
    artX = self.x + self.artXOffset
    artY = self.y + self.artYOffset
    return artX, artY
    
  def getArtPosition_pixels(self):
    artX, artY = self.getArtPosition_tiles()
    pixelX = floor(artX*pixelsPerTileWidth)
    pixelY = floor(artY*pixelsPerTileHeight)
    return (pixelX, pixelY)
    
    
    
    
    
    
    
    
    
    
  