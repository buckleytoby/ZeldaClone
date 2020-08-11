
from config       import *
from utils        import *
from world        import *
from player       import *
from gameObjects  import *
from physics      import *
from factory      import *
from characters   import *
from item_objects import *
import particle_factories

class TriggerAreas():
  def __init__(self, name, dict):
    self.name = name
    self.__dict__.update(dict)

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
                      9: 'BallOnChainGuy',
                      10: 'Boss1',
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
    self.playerClass  = Player()
    self.worldClass   = World(self)
    self.physicsClass = Physics(self.playerClass)
    # game objects dict
    self.gameObjects = {}
    self.new_game_objects = {}
    self.gameObjectsARR = []
    self.maps = {}

    # trigger areas
    self.trigger_areas = {}


    # add to data
    DATA["game_objects_ref"] = self.gameObjects
    DATA["trigger_areas_ref"] = self.trigger_areas

    # group the factories
    self.factories = {'Soldier': SoldierFactory(),
                 'Player':  PlayerFactory(),
                 'MiniSoldier': MiniSoldierFactory(),
                 'MegaSoldier': MegaSoldierFactory(),
                 "Archer": ArcherFactory(),
                 "Archer2": Archer2Factory(),
                 "Archer3": Archer3Factory(),
                 "Archer4": Archer4Factory(),
                 "BallOnChainGuy": BallOnChainGuyFactory(),
                 "Boss1": Boss1(),
                 'Potion': potionFactory,
                 'GoldKey': goldKeyFactory,
                 'Gate': gateFactory,
                 'Ghost1': GhostParticleFactory(),
                 'BigGhost1': BigGhostParticleFactory(),
                 'Blood1': BloodParticleFactory(),
                 'BigBlood1': BigBloodParticleFactory(),
                 'Explosion': particle_factories.explosionFactory,
                  }
    
    # add weapons to the list of factories
    for weapon in weapons.weapons_list:
      self.factories[weapon.name] = weapon
    
  # # # # @profile
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
    valid_cmds = ["GEN_OBJ", "DEL_OBJ", "PLAY_SOUND", "CHANGE_MUSIC"]

    max_nb_messages = 100
    count = 0
    while not MESSAGES.empty() and count < max_nb_messages:
      count += 1
      msg = MESSAGES.get()
      cmd = msg[0]
      # print(msg, cmd)
      if cmd in valid_cmds:
        fcn = getattr(self, cmd)
        fcn(msg[1])

  def CHANGE_MUSIC(self, song_name):
    obj = self.worldClass.music[song_name]
    pygame.mixer.music.load(obj)
    pygame.mixer.music.set_volume(0.5)
    if SOUND_ON:
      pygame.mixer.music.play(-1)

  def PLAY_SOUND(self, name):
    if SOUND_ON:
      self.worldClass.sounds[name].play()

  def GEN_OBJ(self, obj):
    x = obj.x
    y = obj.y

    # if True:
    #   print("adding game object: {} at x: {} y: {}".format(type(obj), x, y))
    self.add_game_object(x, y, obj)

  def DEL_OBJ(self, obj):
    self.remove_game_object(obj)
    del obj
    
  def add_game_object(self, x, y, object):
    self.gameObjects[object.id] = object
    object.update_rect()
    if self.physicsClass.go_tree:
      self.physicsClass.go_tree.add({object.id: object})
    # self.new_game_objects[object.id] = object
    # self.gameObjectsARR[int(x)][int(y)].append(object.id)

  def remove_game_object(self, obj):
    del self.gameObjects[obj.id]
    if self.physicsClass.go_tree:
      self.physicsClass.go_tree.remove({obj.id: obj})
      # print(len(self.physicsClass.go_tree.items))

  # def set_map(self):
  #   mapMatrix = np.empty((mapWidth, mapHeight), dtype='int')
  #   for j in range(0, mapHeight):
  #     dlist=parse_data(f.parse_lines())
  #     for i in range(0, mapWidth):
  #       mapMatrix[i][j]=int(dlist[i])-1 #Tiled is 1 indexed
  #   self.worldClass.setMap(mapType, mapMatrix)

  def load_tmx_map(self, tmx_fn):
    map1 = pytiled_parser.parse_tile_map(tmx_fn)
    self.maps[map1.tmx_file] = map1

    for gamegid in map1.tile_sets:
      # dict key is the gamegid 
      tileset = map1.tile_sets[gamegid]

      # load source
      self.worldClass.tileArt.add_name(tileset.name, gamegid - 1) # subtract 1 since tiled is 1-indexed


  def set_map_json(self, json_fn):
    # load json file and extract the objects

    # firstgid: index value that that tileset starts at

    with open(json_fn) as json_file:
      data = json.load(json_file)
      height = data["height"]
      width = data["width"]
      
      layers = data["layers"]
      for layer in layers:
        if layer["type"] == "tilelayer":
          map_type = layer["name"]
          map_matrix = np.array(layer["data"], dtype='int') - 1 #Tiled is 1 indexed, so null tiles are value -1
          map_matrix = np.reshape(map_matrix, (height, width)).T # must tranpose due to Tiled coord sys
          self.worldClass.setMap(map_type, map_matrix)

          # children
          if "properties" in layer:
            props = layer["properties"]
            for prop in props:
              if prop["name"] == "child": self.worldClass.set_child(map_type, prop["value"])

        # objects
        elif layer["type"] == "objectgroup":
          if layer["name"] == "trigger_areas":
            for object in layer["objects"]:
              xy = np.divide( np.array([object[key] for key in ['x', 'y']]), TILE_SIZE)
              wh = np.divide( np.array([object[key] for key in ['width', 'height']]), TILE_SIZE)
              rect = utils.make_rect(xy, wh)
              if "properties" in object:
                props = object["properties"]
                for prop in props:
                  if prop["name"] == "trigger":
                    # register_event(rect, prop["value"])
                    name = prop["value"]
                    obj = TriggerAreas(name, {'rect': rect})
                    self.trigger_areas[name] = obj

          elif layer['name'] == 'spawns': # assume all points
            for object in layer["objects"]:
              x, y = np.divide( np.array([object[key] for key in ['x', 'y']]), TILE_SIZE)
              type = object['type']
              if type in self.factories:
                obj = self.factories[type].create(x, y)

                # add on custom fields
                if "properties" in object: #hasattr(object, "properties"):
                  for prop in object['properties']:
                    setattr(obj, prop["name"], prop["value"])

                self.add_game_object( x, y, obj )
              else:
                print("Unable to spawn object: {}".format(type))

      # trigger areas

    # nowhere better to put this
    self.instantiate_game_objects()
    self.make_portals()

  def reset_game_objects_arr(self):
    world_map = self.worldClass.getMap("staticObjects")
    width = world_map.shape[0]
    height = world_map.shape[1]
    self.gameObjectsARR = [[[] for y in range(height)] for x in range(width)]

    # TODO: find a better place to put this
    map_limit = np.array([width - 1, height - 1])
    self.playerClass.screenClass.map_limit = map_limit

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

  def make_portals(self):
    # get map
    map1 = self.worldClass.getMap("portals") + 1 # np array, add 1 so that 0 is null
    if map1 is not None: # protect against None
      indices = np.nonzero(map1)
      values = map1[indices]
      #
      portals = []

      # set up array
      a = np.vstack((values, indices)).T

      # sort by portal id
      sorted1 = a[a[:,0].argsort()]
      u, s = np.unique(sorted1[:,0], return_index=True)
      
      # get all of same value
      splitted = np.split(sorted1, s[1:], axis=0)

      portal_id_counter = 0
      for split in splitted:
        if len(split) <= 1: # skip single-entry portals
          continue
        
        # 1 portal per entry
        for i in range(len(split)):
          # cyclical exit
          j = (i+1) % len(split)

          src = split[i, 1:]
          dst = split[j, 1:]

          # make portal game object
          portals.append( Portal(src, portal_id_counter + i, dst, portal_id_counter + j) )
        portal_id_counter += i+1 # will be last value of the inner loop, i.e. len(split)

      # pass to physics class
      self.physicsClass.set_portals(portals)

    
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

      elif line == "[tmx_map]":
        tmx_fn = process_file_name( f.parse_lines() )
        self.load_tmx_map(tmx_fn)
      
        
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
          
        elif type == 'sound':
          line = f.parse_lines()
          if line == 'clear':
            self.worldClass.sounds.clear()
            line = f.parse_lines()
          file_name = process_file_name(line)
          name = f.parse_lines()
          soundObj = pygame.mixer.Sound(file_name)
          self.worldClass.sounds[name] = soundObj

        elif type == 'music':
          line = f.parse_lines()
          if line == 'clear':
            self.worldClass.music.clear()
            line = f.parse_lines()
          file_name = process_file_name(line)
          name = f.parse_lines()
          self.worldClass.music[name] = file_name

        elif type == 'childGameObjects':
          self.worldClass.load_child_objects(f, self.factories)
      
        elif type == 'tiles':
          line = f.parse_lines()
          if line == 'clear':
            clear = True
            line = f.parse_lines()
          else:
            clear = False
          img_fn = process_file_name(line)
          name = f.parse_lines()
          gamegid = self.worldClass.tileArt.gamegids[name]
          self.worldClass.load_tiles(img_fn, gamegid, 16, 16, clear=clear)
          count = 0
          while line != '[end]':
            line = f.parse_lines()
            splitted = line.split(',') # csv
            for str1 in splitted:
              try: 
                collide = bool(int(str1))
              except:
                continue
              self.worldClass.tileArt.tiles[gamegid + count].can_collide = collide
              count += 1
              
      #restart loop, get next line
      line=f.parse_lines()
