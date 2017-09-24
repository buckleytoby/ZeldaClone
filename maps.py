


class World(object):
  #class for the map
  count = -1
  imgtilew=16
  imgtileh=16
  screen=None
  def __init__(self):
    
    World.count += 1
    self.id = World.count
    self.screenloc=[0,0,0,0] #screen location [tilew,tileh,pixel offsetx, pixel offset y]
    self.maps{}
    self.mapParents{}
    self.neighborMaps = [] #which maps are connected to this one
    self.edit=False #whether or not in edit mode
    self.idtileedit=0 #id of tile to edit with
    self.layers=[] #[i][submap startx starty]
    self.transferclass=map_transfer() #how to transfer between maps
    
  def setMap(self, mapType, map):
    #require all maps to be numpy arrays
    self.maps[mapType] = map.copy() #think I have to copy
    
  def setParent(self, mapType, parentType):
    self.mapParents[mapType] = parentType
    
  def getTile(self, mapType, indices):
    i, j = indices
    tileValue = self.maps[mapType][i][j]
    tileObj = self.tiles[mapType]
    return tileObj.tiles[tileValue]
    
  def convertTileToPixel(self, pos_tile): #offset backwards so that it'll appear correct ????????????
    pos_tile = np.array(indices, dtype='float')
    factor = np.array((pixelsPerTileWidth, pixelsPerTileHeight))
    pos_pixel = np.mult([pos_tile, factor]) #check syntax
    return pos_pixel.tolist()
    
    
  def gencost(self,width,height):
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
      if self.isGameObjectMap(mapType): self.drawGameObjects(gameObjectsMap) ? self.draw(mapType)
    
  
  def drawMap(self, mapType):
    map = self.maps[mapType]
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
        
def drawGameObjects(self, gameObjectsMap):
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
            
            sprite = gameObject.getSprite()
            screen.blit(sprite, (xpixel, ypixel))
            gameObject.drawn = True
      
      
      
      
      
  
class TitleScreen(Map):
  #class for title screen
  
  def __init__(self, sourceTxtFile):
    super(Map).init(sourceTxtFile) #something like this, I can't remember
    
    
    
    
  def writeScreen(self):
    #
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    