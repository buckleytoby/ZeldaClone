
from config       import *
from utils        import *
from world        import *
from player       import *
from gameObjects  import *
from physics      import *
from factory      import *
from characters   import *



class ClassHolder(object):
  #hold all of the classes for a level

  # constant dict, 1-indexed
  game_object_idxs = {1: 'Player',
                      2: 'Soldier',
                      3: 'MiniSoldier',
                      4: 'MegaSoldier',
                      5: 'Archer',
                      6: 'Archer2',
                      7: 'Archer3',
                      8: 'Archer4',
                      }

  obsolete = {'Player': 1,
                      'Soldier': 2,
                      'MiniSoldier': 3,
                      'MegaSoldier': 4,
                      'Archer': 5,
                      'Archer2': 6,
                      'Archer3': 7,
                      'Archer4': 8,
                      }

  def __init__(self, configFile):
    self.configFile = process_file_name(configFile)
    self.worldClass   = World()
    self.playerClass  = Player()
    self.physicsClass = Physics()
    # game objects dict
    self.gameObjects = {}
    self.gameObjectsARR = []

    # add to data
    DATA["game_objects_ref"] = self.gameObjects

    # group the factories
    self.factories = {'Soldier': SoldierFactory(),
                 'Player':  PlayerFactory(),
                 'MiniSoldier': MiniSoldierFactory(),
                 'MegaSoldier': MegaSoldierFactory(),
                 "Archer": ArcherFactory(),
                 "Archer2": Archer2Factory(),
                 "Archer3": Archer3Factory(),
                 "Archer4": Archer4Factory(),
                  }

    
    
  def writeScreen(self):
    screenLocation = self.playerClass.screenClass.getLocation()
    screen_rect = self.playerClass.screenClass.rect
    self.worldClass.writeScreen(self.gameObjects, self.gameObjectsARR, screenLocation, screen_rect)

  def update(self):
    """ pop queue messages and perform the commands
    queue objects must be tuples of form (cmd, obj)
    valid commands:
      GEN_OBJ
      DEL_OBJ
    """
    valid_cmds = ["GEN_OBJ", "DEL_OBJ"]

    while not MESSAGES.empty():
      msg = MESSAGES.get()
      cmd = msg[0]
      # print(msg, cmd)
      if cmd in valid_cmds:
        fcn = getattr(self, cmd)
        fcn(msg[1])

  def GEN_OBJ(self, obj):
    x = obj.x
    y = obj.y

    if False:
      print("adding game object: {} at x: {} y: {}".format(type(obj), x, y))
    self.add_game_object(x, y, obj)

  def DEL_OBJ(self, obj):
    self.remove_game_object(obj)
    del obj
    
  def add_game_object(self, x, y, object):
    self.gameObjects[object.id] = object
    self.gameObjectsARR[int(x)][int(y)].append(object.id)

  def remove_game_object(self, obj):
    del self.gameObjects[obj.id]

  def set_map(self):
    mapMatrix = np.empty((mapWidth, mapHeight), dtype='int')
    for j in range(0, mapHeight):
      dlist=parse_data(f.parse_lines())
      for i in range(0, mapWidth):
        mapMatrix[i][j]=int(dlist[i])-1 #Tiled is 1 indexed
    self.worldClass.setMap(mapType, mapMatrix)

  def set_map_json(self, json_fn):
    # load json file and extract the objects

    with open(json_fn) as json_file:
      data = json.load(json_file)
      height = data["height"]
      width = data["width"]
      
      layers = data["layers"]
      for layer in layers:
        map_type = layer["name"]
        map_matrix = np.array(layer["data"], dtype='int') - 1 #Tiled is 1 indexed
        map_matrix = np.reshape(map_matrix, (height, width)).T # must tranpose due to Tiled coord sys
        self.worldClass.setMap(map_type, map_matrix)

    # nowhere better to put this
    self.instantiate_game_objects()

  def reset_game_objects_arr(self):
    world_map = self.worldClass.getMap("staticObjects")
    width = world_map.shape[0]
    height = world_map.shape[1]
    self.gameObjectsARR = [[[] for y in range(height)] for x in range(width)]

  def instantiate_game_objects(self):
    self.reset_game_objects_arr()

    # get map
    map1 = self.worldClass.getMap("gameObjects") + 1 # np array, add 1 so that 0 is null
    indices = np.nonzero(map1)

    for x, y in zip(indices[0], indices[1]):
      val = map1[x][y]
      if val in ClassHolder.game_object_idxs:
        factory_name = ClassHolder.game_object_idxs[val]
        #instantiate game object
        object = self.factories[factory_name].create(x, y)
        self.add_game_object( x, y, object )
        if factory_name == 'Player':
          self.playerClass.setGameObject(object)
    
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

      elif line == "[json_map]":
        json_fn = process_file_name( f.parse_lines() )
        self.set_map_json(json_fn)
      
        
      elif line == '[INCL]':
        line=f.parse_lines()
        name=line.rstrip('\n')
        file_name = process_file_name(name)
        g.append(Parser(file_name))
        f=g[-1]
      
      elif line == '[source]':
        line = f.parse_lines()
        type = line.split('=')[1] #get the word after '='
        if type == 'gameObjects':
          line = f.parse_lines()
          if line == 'clear':
            clear = True
            line = f.parse_lines()
          else:
            clear = False
          file_name = process_file_name(line)
          self.worldClass.loadGameObjects(file_name, f, self.factories, clear=clear)

        elif type == 'childGameObjects':
          self.worldClass.load_child_objects(f, self.factories)
      
        elif type == 'tiles':
          line = f.parse_lines()
          file_name = process_file_name(line)
          self.worldClass.load_tiles(file_name, 16, 16)
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
              
      #restart loop, get next line
      line=f.parse_lines()
