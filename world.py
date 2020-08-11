
from config       import *
from utils        import *
import characters



class ObjectArt(object): #procedure: get sprite index from gameObject.animation.getSpriteIndex(), then get the sprite with this class
  def __init__(self):
    self.data = []
    
  def clear(self):
    del self.data[:]
    
  def setData(self, data):
    self.clear
    self.data = data
    
  def getSprite(self, spriteIndx):
    # modulate spriteIndx with length of art
    idx = np.min([spriteIndx, len(self.data)-1])
    return self.data[idx]



class Tile():
  def __init__(self):
    self.can_collide = False
    self.data = None
  
class TileArt(object):
  """ This class defines the different tiles and their attributes
  """
  def __init__(self):
    self.tiles = {}
    self.gamegids = {}
  
  def clear(self):
    self.tiles.clear()

  def addTile(self, id, art):
    tile = Tile()
    tile.art = art
    self.tiles[id] = tile

  def add_name(self, name, id):
    self.gamegids[name] = id

class Map(object):
  """ This class holds data for a map in the game. Allows for layering of foreground, background, etc.
  """
  def __init__(self):
    self.invisible = False
    self.tileData = []
    self.children = []
    #self.gameObjectData = []
    #self.gameObjects = None

  def setTileData(self, data):
    """ tile data is an array the size of the map, which contains indices which specify which tile type the tile is
    """
    self.tileData = data
    self.numTilesWidth  = data.shape[0]
    self.numTilesHeight = data.shape[1]
    
  def getTileData(self):
    """ tile data is an array the size of the map, which contains indices which specify which tile type the tile is
    """
    return self.tileData

  def get_rect(self, i, j):
    # independent of tile type
    lt = float(i), float(j)
    wh = [1.0, 1.0]
    x, y = [lt[0], lt[0] + wh[0]], [lt[1], lt[1] + wh[1]]
    rect = PatchExt([x, y]) # xxyy_limits' a sequence of two pairs: [[x_low, x_high], [y_low, y_high]]
    return rect

class World(object):
  #class for the map
  count = -1
  screen=None
  def __init__(self, class_holder):
    self.class_holder = class_holder
    
    World.count += 1
    self.id = World.count
    self.screenloc=[0,0,0,0] #screen location [tilew,tileh,pixel offsetx, pixel offset y]
    self.maps = defaultdict(Map)
    self.mapParents = {}
    self.tileArt = TileArt()
    self.baked_tile_Art = TileArt()
    self.objectArts = {}
    self.neighborMaps = [] #which maps are connected to this one
    self.edit=False #whether or not in edit mode
    self.sounds = {}
    self.music = {}
    self.bake_size = 4

    # --- debugging ---
    self.draw_collision_boxes = False

  def bake_tiles(self):
    """ iterate through the layers and generate n-by-n tile surfaces which will be blitted to the screen. The advantage is that baking only occurs once per world, which will reduce the # of required blits """
    bake_size = self.bake_size

    ### set-up
    # get size of map
    baked_map = -1 * np.ones_like( self.getMap('staticObjects') )
    # 

    drawn = defaultdict(bool)
    surf_hash = defaultdict(lambda: pygame.Surface((bake_size * pixelsPerTileWidth, bake_size * pixelsPerTileHeight)))
    # iterate through layers
    def recurse(mapType): #must check ability to change isDrawn in nested Function, it has bit me before
      nonlocal surf_hash
      map = self.maps[mapType]
      if drawn[mapType]:
        return
      elif map.children: # not empty list
        [recurse(childType) for childType in map.children]
      #draw it
      drawn[mapType] = True
      if map.invisible: return

      print("Baking map: {}".format(mapType))
      map_arr = self.maps[mapType].tileData

      # assumes that each map is the same size (should be true if using Tiled)
      baked_tile_count = 0
      # iterate through the map
      for i in range(0, map.numTilesWidth, bake_size):
        for j in range(0, map.numTilesHeight, bake_size):
          # make new surface
          surf = surf_hash[baked_tile_count]
          # copy to surface
          for k in range(bake_size):
            # out of bounds protection
            if (i+k) > baked_map.shape[0] - 1:
              continue
            for m in range(bake_size):
              # out of bounds protection
              if (j+m) > baked_map.shape[1] - 1:
                continue
              if not map_arr[i+k][j+m] == -1:
                art = self.getTileArt(mapType, (i+k, j+m))
                location = np.array([k, m]) * pixel_factor
                surf.blit(art, location)

          # save surface
          self.baked_tile_Art.addTile(baked_tile_count, surf)

          # save index in the baked map
          baked_map[i][j] = baked_tile_count
          baked_tile_count += 1

    # call recurse
    for mapType in self.maps:
      if mapType == "staticObjects":
        recurse(mapType)
    
    # register map
    self.setMap("baked_map", baked_map)
    
  def load_tiles(self, imagefile, gamegid, width, height, clear=False):
    #reads in image, resets tileArt, fills with tiles
    if clear:
      self.tileArt.clear()

    image = pygame.image.load(imagefile).convert_alpha()
    imgw, imgh = image.get_size()
    count = 0
    for tiley in range(0,int(imgh/height)):
      for tilex in range(0,int(imgw/width)):
      
        rect = (tilex*width, tiley*height, width, height)
        tile = image.subsurface(rect)
        tile = pygame.transform.scale(tile,(pixelsPerTileWidth,pixelsPerTileHeight))
        self.tileArt.addTile(gamegid + count, tile)
        count += 1


  def loadGameObjects(self, imagefile, f, factories, clear=False):
    # reads in image, resets, fills with sprites
    # input: 'f' is the file object which specifies names of game objects
    # moves left to right, then top to bottom along the image
    # NOTE: Assumes 1 sprite per image file

    if clear:
      self.objectArts.clear()
    image = pygame.image.load(imagefile).convert_alpha()
    imgw, imgh = image.get_size() # in pixels
    
    objectType = f.parse_lines()
    self.objectArts[objectType] = ObjectArt()
    pixelWidth  = factories[objectType].values['pixelWidth']
    pixelHeight = factories[objectType].values['pixelHeight']
    tileWidth   = factories[objectType].values['artWidth']
    tileHeight  = factories[objectType].values['artHeight']

    nb_w = int( imgw / pixelWidth )
    nb_h = int( imgh / pixelHeight )

    spriteRow=[]
    for tiley in range(nb_h):
      for tilex in range(nb_w): # ensure we'll go left-right, then top-bottom
        rect = (tilex * pixelWidth, tiley * pixelHeight, pixelWidth, pixelHeight)
        tile = image.subsurface(rect)
        tile = pygame.transform.scale(tile, (int(tileWidth * pixelsPerTileWidth), 
                int(tileHeight * pixelsPerTileHeight)))
        spriteRow.append(tile)

    self.objectArts[objectType].setData(spriteRow)
    
  def loadGameObjects2(self, imagefile, f, factories, clear=False): #height/width of tiles
    # reads in image, resets, fills with sprites
    # input: 'f' is the file object which specifies names of game objects
    if clear:
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
      tileWidth   = factories[objectType].values['artWidth']
      tileHeight  = factories[objectType].values['artHeight']
      tiley = 0
      while tiley*pixelHeight < imgh:
        rect = (tilex * pixelWidth, tiley * pixelHeight, pixelWidth, pixelHeight)
        tile = image.subsurface(rect)
        tile = pygame.transform.scale(tile, (int(tileWidth * pixelsPerTileWidth), 
                int(tileHeight * pixelsPerTileHeight)))
        spriteRow.append(tile)
        tiley += 1
      tilex += 1 
      pixelCount += pixelWidth
      self.objectArts[objectType].setData(spriteRow)

  def load_child_objects(self, f, factories): #height/width of tiles
    line = ""

    while line != '[end]':
      line = f.parse_lines()
      # if single entry, then objectType and parentType are the same
      split = line.split(" ")
      if line == '[end]':
        break
      elif len(split) == 2:
        objectType = split[0]
        parentType = split[1]
      else:
        print("Unknown input: {}".format(line))
        continue

      self.objectArts[objectType] = ObjectArt()
      tileWidth   = factories[objectType].values['artWidth']
      tileHeight  = factories[objectType].values['artHeight']

      parent_tile_width = factories[parentType].values['artWidth']
      parent_tile_height = factories[parentType].values['artHeight']

      spriteRow=[]
      for tile in self.objectArts[parentType].data:
        tile = pygame.transform.scale(tile, (int(tileWidth * pixelsPerTileWidth), 
                int(tileHeight * pixelsPerTileHeight)))
        spriteRow.append(tile)
        
      print("Setting {} art from {}.".format(objectType, parentType))
      self.objectArts[objectType].setData(spriteRow)

    
  def setMap(self, mapType, data):
    #require all maps to be numpy arrays
    self.maps[mapType].setTileData(data) #think I have to copy
    
  def getMap(self, mapType):
    # Gets the map tile data
    # require all maps to be numpy arrays
    if mapType in self.maps:
      return self.maps[mapType].getTileData() #think I have to copy
    else:
      return None
    
  def setParent(self, mapType, parentType):
    self.mapParents[mapType] = parentType

  def set_child(self, mapType, childType):
    self.maps[mapType].children.append( childType )
    
  def getTileArt(self, mapType, indices):
    i, j = indices
    tileValue = self.maps[mapType].tileData[i][j]
    return self.tileArt.tiles[tileValue].art
    
  def get_baked_tile_art(self, mapType, indices):
    i, j = indices
    tileValue = self.maps[mapType].tileData[i][j]
    return self.baked_tile_Art.tiles[tileValue].art

  # # # # @profile
  def can_tile_collide(self, mapType, indices):
    # return False if indices are out of range
    i, j = indices
    data = self.maps[mapType].tileData
    # TODO: optimize this expression
    if i > -1 and i < data.shape[0] and j > -1 and j < data.shape[1]:
    # if np.all( np.logical_and( indices > (0, 0), indices < data.shape ) ):
      tileValue = data[i][j]
      if tileValue < 0: # null tile
        return True
      else:
        out = self.tileArt.tiles[tileValue].can_collide
      return out
    else:
      return False
    
  def convertTileToPixel(self, indices): #offset backwards so that it'll appear correct ????????????
    pos_pixel = np.multiply(indices, pixel_factor) #check syntax
    return pos_pixel

  def convertPixelToScreen(self, pixelList, screenLocation):
    # subtract the screen location, in tiles, from the pixels
    pos_screen = np.array(screenLocation, dtype='float')
    out = pixelList - np.multiply(pos_screen, pixel_factor) #check syntax
    return out

    
    
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
          if gameObject.visible: gameObject.drawn = False

  def draw_mana_bar(self, go, xy, wh):
    # https://www.reddit.com/r/pygame/comments/8b1exj/smooth_health_bar/
    value = go.attacker.mana
    max_value = go.attacker.max_mana
    #
    if value > 0: # value < max_value and
      b = min(255, 255 - (255 * ((value - (max_value - value)) / max_value)))
      g = min(255, 255 * (value / (max_value)))
      color = (0, 0, g)
      wh[0] = int( wh[0] * value / max_value)
      value_bar = pygame.Rect(xy, wh)
      pygame.draw.rect(World.screen, color, value_bar)
  
  def draw_health_bar(self, go, xy, wh):
    # https://www.reddit.com/r/pygame/comments/8b1exj/smooth_health_bar/
    health = go.attacker.health
    max_health = go.attacker.max_health
    #
    if health > 0: # health < max_health and
      r = min(255, 255 - (255 * ((health - (max_health - health)) / max_health)))
      g = min(255, 255 * (health / (max_health / 2)))
      color = (r, g, 0)
      wh[0] = int( wh[0] * health / max_health)
      health_bar = pygame.Rect(xy, wh)
      pygame.draw.rect(World.screen, color, health_bar)

  def draw_player_health(self):
    go = self.class_holder.playerClass.gameObject
    self.draw_health_bar(go, [5, 5], [100, 7])

  def draw_player_mana(self):
    go = self.class_holder.playerClass.gameObject
    self.draw_mana_bar(go, [5, 17], [100, 7])

  def draw_attack_cooldown(self):
    go = self.class_holder.playerClass.gameObject
    xy = [5, 29]
    wh = [100, 7]

    if go.attacker.disabled:
      value = go.attacker.attack_cooldown_timer.get_elapsed_time()
      max_value = go.attacker.attack_cooldown
      #
      if value > 0 and value < max_value:
        b = min(255, 255 - (255 * ((value - (max_value - value)) / max_value)))
        g = min(255, 255 * (value / (max_value)))
        color = (0, g, 0)
        wh[0] = int( wh[0] * value / max_value)
        value_bar = pygame.Rect(xy, wh)
        pygame.draw.rect(World.screen, color, value_bar)

  # # # # # @profile
  def writeScreen(self, gameObjects, gameObjectsARR, screenLocation, screen_rect):
    self.screenLocation = np.array(screenLocation, dtype='float')
    self.screenMaxIDX = self.screenLocation + 1 + np.array( 
      (screenTileWidth, screenTileHeight), dtype='float')
    self.screenLocationX = int(self.screenLocation[0])
    self.screenLocationY = int(self.screenLocation[1])
    
    # # # # # @profile
    def recurse(mapType): #must check ability to change isDrawn in nested Function, it has bit me before
      map = self.maps[mapType]
      if isDrawn[mapType]:
        return
      elif map.children: # not empty list
        [recurse(childType) for childType in map.children]
      #draw it
      isDrawn[mapType] = True
      if map.invisible: return
      self.drawMap(mapType)
      self.draw_game_objects(gameObjects, screen_rect)
      
    isDrawn = defaultdict(bool)

    # draw the baked map
    self.drawMap("baked_map")
    # draw game objects
    self.draw_game_objects(gameObjects, screen_rect)

    # UI on top
    self.draw_player_health()
    self.draw_player_mana()
    self.draw_attack_cooldown()

  def baked_screen_location(self):
    return self.screenLocation - self.bake_size - 1

  def baked_screen_wrt_screen(self):
    # location of the baked screen w.r.t. the screen (in pixels)
    x = (self.baked_screen_location() - self.screenLocation) * pixel_factor
    # x = - np.array([self.bake_size, self.bake_size]) * pixel_factor
    return x

  def clipScreen(self, mapLength):
    maxIDX_x, maxIDX_y = np.clip(self.screenMaxIDX, np.zeros(2), 
      np.array(mapLength))
    minIDX_x, minIDX_y = np.clip(self.baked_screen_location(), np.zeros(2), 
      np.array(mapLength))
    # convert to integer
    maxIDX_x = int(maxIDX_x); maxIDX_y = int(maxIDX_y)
    minIDX_x = int(minIDX_x); minIDX_y = int(minIDX_y)
    return maxIDX_x, maxIDX_y, minIDX_x, minIDX_y
    
  # # # # @profile
  def drawMap(self, mapType):
    mapARR = self.maps[mapType].tileData
    mapLenX, mapLenY = mapARR.shape
    #restrict screen to map-bounds
    maxIDX_x, maxIDX_y, minIDX_x, minIDX_y = self.clipScreen((mapLenX - 1, mapLenY - 1))


    pixeli, pixelj = pixeli0, pixelj0 = self.baked_screen_wrt_screen()
    offset = -1.0 * (self.baked_screen_location() % 1) * pixel_factor

    for i in range(minIDX_x, maxIDX_x+1):
      for j in range(minIDX_y, maxIDX_y+1):
        if not mapARR[i][j] == -1:
          location = (pixeli, pixelj) + offset

          art = self.get_baked_tile_art(mapType, (i, j))
          World.screen.blit(art, location)

          
        pixelj += pixelsPerTileHeight
      pixeli += pixelsPerTileWidth
      pixelj = pixelj0

  def draw_game_objects(self, gameObjects, screen_rect):
    """ iterate through gameobjects and only draw if they're on the screen
    """
    #reset drawn status for each mob in frame
    ###self.resetDrawnStatus(gameObjects, gameObjectsARR, (maxIDX_x, maxIDX_y))

    for key in gameObjects: 
      go = gameObjects[key]
      go.drawn = False
      if go.intersect(screen_rect, art=True):
        # draw the art
        self.low_draw_art(go)

        
  # def drawGameObjects(self, gameObjects, gameObjectsARR): #right now this could be pulled up into classHolder ...
  #   """ draw game objects by iterating through "map" of units (cheap man's quad-tree)
  #   TODO: fix bug -- gameObjectsARR never gets updated
  #   """
  #   mapLenX = len(gameObjectsARR)
  #   mapLenY = len(gameObjectsARR[0])
  #   #setting map bounds for mobs
  #   maxIDX_x, maxIDX_y, minIDX_x, minIDX_y = self.clipScreen((mapLenX, mapLenY))

  #   pdb.set_trace()
      
  #   #reset drawn status for each mob in frame
  #   self.resetDrawnStatus(gameObjects, gameObjectsARR, (maxIDX_x, maxIDX_y))
          
  #   #moving objects -- reverse order so that overlapping mobs are drawn correctly
  #   for i in range(maxIDX_y-1, minIDX_y, -1):
  #     for j in range(maxIDX_x-1, minIDX_x, -1):
  #       for gameObjectID in gameObjectsARR[i][j]:
  #         gameObject = gameObjects[gameObjectID]
  #         #pdb.set_trace()
  #         self.low_draw_art(gameObject)

  def draw_go_rect(self, go):
    # this is the collision rect
    go.update_pygame_screen(self.screenLocation)
    pygame.draw.rect(World.screen, go.rgb, go.pygame_screen_rect)

  def low_draw_art(self, go):
    if go.visible and go.drawn == False:
      if go.has_sprite:
        xpixel, ypixel = go.getArtPosition_pixels()
        xscreen, yscreen = self.convertPixelToScreen((xpixel, ypixel), self.screenLocation)
          #(self.screenLocationX, self.screenLocationY))

        objectType = go.objectType
        # spriteIndex = go.animation.getSpriteIndex()
        spriteIndex = go.animation.animationIndex
        sprite = self.objectArts[objectType].getSprite(spriteIndex)
        World.screen.blit(sprite, (xscreen, yscreen))

      else: # solid rect
        self.draw_go_rect(go)

      # debugging: draw the collision box, on top of art
      if self.draw_collision_boxes:
        self.draw_go_rect(go)

        # draw portals too
        [self.draw_go_rect(portal) for portal in self.class_holder.physicsClass.portals]
      
      go.drawn = True
      
      
      
      
      
  
class TitleScreen(World):
  #class for title screen
  
  def __init__(self):
    super(TitleScreen, self).__init__()
    
    
    
    
  #def writeScreen(self):
  #  #
  #  pass
    
    
    
    
    
class Event():
    def __init__(self):

      self.fcn

    def triggered(self):
      raise NotImplementedError


class Boss1Event(Event):
    def __init__(self):
      pass
    
    
    def triggered(self):
      # spawn Boss1 at center of spawn box
      boss1 = factories["boss1"].create(x, y)
      make_gen_msg(boss1)

      # change music
      make_music_msg("boss1")

      # make health bar game object on top layer
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
