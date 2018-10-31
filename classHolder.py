
from config       import *
from utils        import *
from world        import *
from player       import *
from gameObjects  import *
from physics      import *



class ClassHolder(object):
  #hold all of the classes for a level
  def __init__(self, configFile):
    self.configFile = configFile
    self.worldClass   = World()
    self.playerClass  = Player()
    self.physicsClass = Physics()
    # game objects dict
    self.gameObjects = {}
    self.gameObjectsARR = []
    #factories
    soldier_factory = SoldierFactory()
    player_factory = PlayerFactory()
    # group the factories
    self.factories = {'Soldier': soldier_factory,
                 'Player':  player_factory}

    
    
  def writeScreen(self):
    screenLocation = self.playerClass.screenClass.getLocation()
    screen_rect = self.playerClass.screenClass.rect
    self.worldClass.writeScreen(self.gameObjects, self.gameObjectsARR, screenLocation, screen_rect)
    
  def addGameObject(self, x, y, object):
    self.gameObjects[object.id] = object
    self.gameObjectsARR[int(x)][int(y)].append(object.id)
    
  def loadConfigFile(self):
    g=[]
    g.append(Parser(self.configFile))
    f=g[-1]
    line=f.parse_lines()
    while len(g)>0:
      if line == 0:
        f.close()
        del g[-1]
        if len(g)>0:
          f=g[-1]
        else:
          break
      
        
      elif line == '[INCL]':
        line=f.parse_lines()
        name=line.rstrip('\n')
        g.append(Parser(name))
        f=g[-1]
      
      elif line == '[source]':
        line=f.parse_lines()
        type = line.split('=')[1] #get the word after '='
        if type == 'gameObjects':
          fileName = f.parse_lines()
          #height = 
          self.worldClass.loadGameObjects(fileName, f, self.factories)
      
        elif type == 'tiles':
          line=f.parse_lines()
          self.worldClass.loadTiles(line, 16, 16)
          count = 0
          while line != '[end]':
            line = f.parse_lines()
            splitted = line.split(',') # csv
            for str1 in splitted:
              try: 
                collide = bool(int(str1))
              except:
                continue
              self.worldClass.tileArt.tiles[count].can_collide = collide
              count += 1



            
          
      elif line == '[header]': #this always comes before [layers]
        mapWidth = int(f.parse_lines()[6:])
        mapHeight = int(f.parse_lines()[7:])
        
      elif line == '[mobs]':
        while line != '[end]':
          if line in factory:
            factory = self.factories[line]
            x = float(f.parse_lines())
            y = float(f.parse_lines())
            object = factory.create(x, y)
            self.addGameObject( object )
            if line == 'Player':
                self.playerClass.setGameObject(x, y, object)
          
          line = f.parse_lines()
          
      elif line == '[layer]':
        line=f.parse_lines()
        mapType = line.split('=')[1] #get the word after '='
        f.parse_lines()
        
        if mapType != 'gameObjects':
          mapMatrix = np.empty((mapWidth, mapHeight), dtype='int')
          for j in range(0, mapHeight):
            dlist=parse_data(f.parse_lines())
            for i in range(0, mapWidth):
              mapMatrix[i][j]=int(dlist[i])-1 #Tiled is 1 indexed
          self.worldClass.setMap(mapType, mapMatrix)
        elif mapType == 'gameObjects': # special map type for units
          self.gameObjectsARR = [[[] for y in range(mapHeight)] for x in range(mapWidth)]
          for y in range(0, mapHeight):
            dlist=parse_data(f.parse_lines())
            for x in range(0, mapWidth):
              try:
                objInd = int(dlist[x])-1
              except:
                pdb.set_trace()
              if objInd == -1:
                continue
              if objInd == 0:
                objType = 'Player'
              elif objInd == 1:
                objType = 'Soldier'
              #instantiate game object
              factory = self.factories[objType]
              object = factory.create(x, y)
              self.addGameObject( x, y, object )
              if objType == 'Player':
                self.playerClass.setGameObject(object)
              
      #restart loop, get next line
      line=f.parse_lines()
