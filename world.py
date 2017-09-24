
from config       import *



class ObjectArt(object):
  left = 0
  down = 1
  right = 2
  up = 3
  def __init__(self):
    self.sprites = []
    
  def clear(self):
    for i in range(len(self.sprites)): del self.sprites[i][:]
    
  def setData(self, data):
    del self.data[:]
    self.data = data
    
    
  def getSprite(self, spriteIndx):
    return self.sprites[spriteIndx]


class TileArt(object):
  def __init__(self):
    self.data = []
  
  def clear(self):
    del self.data[:]
  def addTile(self, tile):
    self.data.append(tile)

class Map(object):
  def __init__(self):
    self.invisible = False
    self.tileData = []
    self.gameObjectData = []
    self.gameObjects


class World(object):
  #class for the map
  count = -1
  screen=None
  def __init__(self):
    
    World.count += 1
    self.id = World.count
    self.screenloc=[0,0,0,0] #screen location [tilew,tileh,pixel offsetx, pixel offset y]
    self.maps = {}
    self.mapParents = {}
    self.tileArt = TileArt()
    self.objectArts = {}
    self.neighborMaps = [] #which maps are connected to this one
    self.edit=False #whether or not in edit mode
    
  def loadTiles(self, imagefile, width, height):
    #reads in image, resets tileArt, fills with tiles
    self.tileArt.clear()
    
    image = pygame.image.load(imagefile).convert_alpha()
    imgw, imgh = image.get_size()
    for tiley in range(0,int(imgh/height)):
      for tilex in range(0,int(imgw/width)):
      
        rect = (tilex*width, tiley*height, width, height)
        tile = image.subsurface(rect)
        tile = pygame.transform.scale(tile,(pixelsPerTileWidth,pixelsPerTileHeight))
        self.tileArt.addTile(tile)
        
  def loadGameObjects(self, imagefile, f): #height/width of tiles
    #reads in image, resets, fills with sprites
    # input: 'f' is the file object which specifies names of game objects
    self.objectArts.clear()
    image = pygame.image.load(imagefile).convert_alpha()
    imgw, imgh = image.get_size() # in pixels
    
    
    #objectType = f.parse_lines()
    #objectFactory = exec(objectType+'Factory') #dynamic name
    
    tilex = 0
    pixelCount = 0
    while pixelCount < imgw: #each column is a different game object
      objectType = f.parse_lines()
      self.objectArts[objectType] = ObjectArt()
      spriteRow=[]
      pixelWidth = exec(objectType+'Factory').values['pixelWidth']
      pixelHeight = exec(objectType+'Factory').values['pixelHeight']
      tileWidth = exec(objectType+'Factory').values['tileWidth']
      tileHeight = exec(objectType+'Factory').values['tileHeight']
      tiley = 0
      while tiley*pixelHeight < imgh:
        rect=(tilex*pixelWidth, tiley*pixelHeight, pixelWidth, pixelHeight)
        tile = image.subsurface(rect)
        tile = pygame.transform.scale(tile,(tileWidth*pixelsPerTileWidth, tileHeight*pixelsPerTileHeight))
        spriteRow.append(tile)
        tiley += 1
      tilex += 1 
      pixelCount += pixelWidth
      self.objectArts[objectType].addSpriteRow(spriteRow)
    
  def setMap(self, mapType, data):
    #require all maps to be numpy arrays
    self.maps[mapType].data = data #think I have to copy
    
  def setParent(self, mapType, parentType):
    self.mapParents[mapType] = parentType
    
  def getTile(self, mapType, indices):
    i, j = indices
    tileValue = self.maps[mapType][i][j]
    return self.tileArt.data[tileValue]
    
  def convertTileToPixel(self, pos_tile): #offset backwards so that it'll appear correct ????????????
    pos_tile = np.array(indices, dtype='float')
    factor = np.array((pixelsPerTileWidth, pixelsPerTileHeight))
    pos_pixel = np.mult([pos_tile, factor]) #check syntax
    return pos_pixel.tolist()
    
    
  def gencost(self, width, height):
    if (width,height) in self.mobcosts:
      return
    int0=len(self.statmap)
    int1=len(self.statmap[0])
    self.mobcosts[(width,height)]=[[1]*int1 for i in range(0,int0)]
    cost=self.mobcosts[(width,height)]
    for pos0 in range(0,int0):
      for pos1 in range(0,int1):
        if pos0>=int0-width+1:
          cost[x][y]=0
          continue
        if pos1>=int1-height+1:
          cost[x][y]=0
          continue
        for i in range(0,width):
          x=pos0+i
          for j in range(0,height):
            y=pos1+j
            zonetype=statobjs[self.statmap[x][y]].zonetype
            if zonetype==1:
              continue
            if subtiles[zonetype].fwall==-1:
              cost[pos0][pos1]=0
    self.mobstatnbors[(width,height)]=genstatnbors(cost)
  
  
  def resetDrawnStatus(self, gameObjectsMap, indices):
    maxIDX_x, maxIDX_y = indices
    for i in range(self.screenLocationX, maxIDX_x):
      for j in range(self.screenLocationY, maxIDX_y):
        for gameObjectType in gameObjectsMap[i][j]:
          gameObject = gameObjects[gameObjectType]
          if gameObject.hasSprite: gameObject.drawn = False
  

  
  def writeScreen(self, gameObjects):
    isDrawn = defaultDict(False)
    for mapType in self.maps:
      recurse(mapType)
    
    def recurse(mapType): #must check ability to change isDrawn in nested function, it's bit me before
      if isDrawn[mapType]: #all parents are drawn too, then
        return
      elif mapType in self.mapParents:
        parentType = self.mapParents[mapType]
        recurse(parentType)
      #draw it
      isDrawn[mapType] = True
      if self.maps[mapType].invisible: return
      self.drawMap(mapType)
      self.drawGameObjects(mapType)
    
  
  def drawMap(self, mapType):
    map = self.maps[mapType].tileData
    mapLenX, mapLenY = map.shape
    #restrict screen to map-bounds
    maxIDX_x = min([mapLenX, self.screenLocationX+numTilesWidth+1])
    maxIDX_y = min([mapLenY, self.screenLocationY+numTilesHeight+1])
    
    #offset backwards so that it'll appear correct
    for i in range(self.screenLocationX, maxIDX_x):
      for j in range(self.screenLocationY, maxIDX_y):
        if map[i][j] == -1 or map[i][j] == 19:
          continue
        xpixel, ypixel = self.convertTileToPixel((i, j))
        tile = self.getTile(mapType, (i, j))
        screen.blit(tile, (xpixel, ypixel))
        
def drawGameObjects(self, mapType):
    gameObjectsMap = self.maps[mapType].gameObjectData
    #setting map bounds for mobs
    maxIDX_x = min([mapLenX, self.screenLocationX+numTilesWidth+1])
    maxIDX_y = min([mapLenY, self.screenLocationY+numTilesHeight+1])
      
    #reset drawn status for each mob in frame
    self.resetDrawnStatus(gameObjectsMap, (maxIDX_x, maxIDX_y))
          
    #moving objects -- reverse order so that overlapping mobs are drawn correctly
    for j in range(self.screenLocationY, maxIDX_y):
      for i in range(self.screenLocationX, maxIDX_x):
        for gameObjectType in gameObjectsMap[i][j]:
          gameObject = gameObjects[gameObjectType]
          if gameObject.hasSprite and gameObject.drawn == False:
            xpixel, ypixel = gameObject.getArtPosition_pixels()
            
            objectType = gameObject.objectType
            spriteIndex = gameObject.artClass.getSpriteIndex()
            sprite = self.objectArts[objectType].getSprite(spriteIndex)
            screen.blit(sprite, (xpixel, ypixel))
            gameObject.drawn = True
      
      
      
      
      
  
class TitleScreen(World):
  #class for title screen
  
  def __init__(self):
    super(World).__init__() #something like this, I can't remember
    
    
    
    
  def writeScreen(self):
    #
    pass
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    