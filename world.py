
from config       import *



class ObjectArt(object): #procedure: get sprite index from gameObject.animation.getSpriteIndex(), then get the sprite with this class
  def __init__(self):
    self.data = []
    
  def clear(self):
    del self.data[:]
    
  def setData(self, data):
    self.clear
    self.data = data
    
  def getSprite(self, spriteIndx):
    return self.data[spriteIndx]


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
    #self.gameObjectData = []
    #self.gameObjects = None

  def setTileData(self, data):
    self.tileData = data
    self.numTilesWidth  = data.shape[0]
    self.numTilesHeight = data.shape[1]

class World(object):
  #class for the map
  count = -1
  screen=None
  def __init__(self):
    
    World.count += 1
    self.id = World.count
    self.screenloc=[0,0,0,0] #screen location [tilew,tileh,pixel offsetx, pixel offset y]
    self.maps = defaultdict(Map)
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
        
  def loadGameObjects(self, imagefile, f, factories): #height/width of tiles
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
      pixelWidth  = factories[objectType].values['pixelWidth']
      pixelHeight = factories[objectType].values['pixelHeight']
      tileWidth   = factories[objectType].values['width']
      tileHeight  = factories[objectType].values['height']
      tiley = 0
      while tiley*pixelHeight < imgh:
        rect=(tilex*pixelWidth, tiley*pixelHeight, pixelWidth, pixelHeight)
        tile = image.subsurface(rect)
        tile = pygame.transform.scale(tile,(int(tileWidth*pixelsPerTileWidth), 
                int(tileHeight*pixelsPerTileHeight)))
        spriteRow.append(tile)
        tiley += 1
      tilex += 1 
      pixelCount += pixelWidth
      self.objectArts[objectType].setData(spriteRow)
    
  def setMap(self, mapType, data):
    #require all maps to be numpy arrays
    self.maps[mapType].setTileData(data) #think I have to copy
    
  def setParent(self, mapType, parentType):
    self.mapParents[mapType] = parentType
    
  def getTile(self, mapType, indices):
    i, j = indices
    tileValue = self.maps[mapType].tileData[i][j]
    return self.tileArt.data[tileValue]
    
  def convertTileToPixel(self, indices): #offset backwards so that it'll appear correct ????????????
    pos_tile = np.array(indices, dtype='float')
    factor = np.array((pixelsPerTileWidth, pixelsPerTileHeight))
    pos_pixel = np.multiply(pos_tile, factor) #check syntax
    return pos_pixel.tolist()

  def convertPixelToScreen(self, pixelList, screenLocation):
    # subtract the screen location, in tiles, from the pixels
    pos_pixels = np.array(pixelList, dtype='float')
    pos_screen = np.array(screenLocation, dtype='float')
    factor = np.array((pixelsPerTileWidth, pixelsPerTileHeight))
    out = pos_pixels - np.multiply(pos_screen, factor) #check syntax
    return out.tolist()

    
    
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
  
  
  def resetDrawnStatus(self, gameObjects, gameObjectsMap, indices):
    maxIDX_x, maxIDX_y = indices
    for i in range(self.screenLocationX, maxIDX_x):
      for j in range(self.screenLocationY, maxIDX_y):
        for gameObjectID in gameObjectsMap[i][j]:
          gameObject = gameObjects[gameObjectID]
          if gameObject.hasSprite: gameObject.drawn = False
  

  
  def writeScreen(self, gameObjects, gameObjectsARR, screenLocation):
    self.screenLocation = np.array(screenLocation, dtype='float')
    self.screenMaxIDX = self.screenLocation + 1 + np.array( 
      (screenTileWidth, screenTileHeight), dtype='float')
    self.screenLocationX = int(self.screenLocation[0])
    self.screenLocationY = int(self.screenLocation[1])
    
    def recurse(mapType): #must check ability to change isDrawn in nested Function, it's bit me before
      if isDrawn[mapType]: #all parents are drawn too, then
        return
      elif mapType in self.mapParents:
        parentType = self.mapParents[mapType]
        recurse(parentType)
      #draw it
      isDrawn[mapType] = True
      if self.maps[mapType].invisible: return
      self.drawMap(mapType)
      self.drawGameObjects(gameObjects, gameObjectsARR)
      
    isDrawn = defaultdict(bool)
    for mapType in self.maps:
      recurse(mapType)

  def clipScreen(self, mapLength):
    maxIDX_x, maxIDX_y = np.clip(self.screenMaxIDX, np.zeros(2), 
      np.array(mapLength))
    minIDX_x, minIDX_y = np.clip(self.screenLocation, np.zeros(2), 
      np.array(mapLength))
    # convert to integer
    maxIDX_x = int(maxIDX_x); maxIDX_y = int(maxIDX_y)
    minIDX_x = int(minIDX_x); minIDX_y = int(minIDX_y)
    return maxIDX_x, maxIDX_y, minIDX_x, minIDX_y
    
  
  def drawMap(self, mapType):
    mapARR = self.maps[mapType].tileData
    mapLenX, mapLenY = mapARR.shape
    #restrict screen to map-bounds
    maxIDX_x, maxIDX_y, minIDX_x, minIDX_y = self.clipScreen((mapLenX, mapLenY))


    # add sub-tile offset
    
    #offset backwards so that it'll appear correct
    for i in range(minIDX_x, maxIDX_x):
      for j in range(minIDX_y, maxIDX_y):
        if mapARR[i][j] == -1 or mapARR[i][j] == 19:
          continue
        xpixel, ypixel = self.convertTileToPixel((i, j))
        xscreen, yscreen = self.convertPixelToScreen((xpixel, ypixel), self.screenLocation)
          #(self.screenLocationX, self.screenLocationY))
        tile = self.getTile(mapType, (i, j))
        World.screen.blit(tile, (xscreen, yscreen))
        
  def drawGameObjects(self, gameObjects, gameObjectsARR): #right now this could be pulled up into classHolder ...
    mapLenX = len(gameObjectsARR)
    mapLenY = len(gameObjectsARR[0])
    #setting map bounds for mobs
    maxIDX_x, maxIDX_y, minIDX_x, minIDX_y = self.clipScreen((mapLenX, mapLenY))
      
    #reset drawn status for each mob in frame
    self.resetDrawnStatus(gameObjects, gameObjectsARR, (maxIDX_x, maxIDX_y))
          
    #moving objects -- reverse order so that overlapping mobs are drawn correctly
    for i in range(maxIDX_y-1, minIDX_y, -1):
      for j in range(maxIDX_x-1, minIDX_x, -1):
        for gameObjectID in gameObjectsARR[i][j]:
          gameObject = gameObjects[gameObjectID]
          if gameObject.hasSprite and gameObject.drawn == False:
            xpixel, ypixel = gameObject.getArtPosition_pixels()
            xscreen, yscreen = self.convertPixelToScreen((xpixel, ypixel), self.screenLocation)
              #(self.screenLocationX, self.screenLocationY))

            spriteType = gameObject.spriteType
            spriteIndex = gameObject.animation.getSpriteIndex()
            sprite = self.objectArts[spriteType].getSprite(spriteIndex)
            World.screen.blit(sprite, (xscreen, yscreen))
            gameObject.drawn = True
      
      
      
      
      
  
class TitleScreen(World):
  #class for title screen
  
  def __init__(self):
    super(TitleScreen, self).__init__()
    
    
    
    
  #def writeScreen(self):
  #  #
  #  pass
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
