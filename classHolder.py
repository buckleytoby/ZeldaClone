
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
    # load config
    self.loadConfigFile()
    
    
  def writeScreen(self):
    self.mapClass.writeScreen(self.gameObjects)
    
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
      elif line == '[mobs]':
        while line != '[end]':
          if line == 'player':
            x = float(f.parse_lines())
            y = float(f.parse_lines())
            self.playerClass.gameObject = soldierFactory.create(x, y)
          elif line == 'soldier':
            x = float(f.parse_lines())
            y = float(f.parse_lines())
            self.mobs.append( soldierFactory.create(x, y) )
          
          line = f.parse_lines()
        
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
          self.worldClass.loadGameObjects(fileName, f)
      
        elif type == 'tiles':
          line=f.parse_lines()
          self.worldClass.loadTiles(line, 16, 16)
            
          
      elif line == '[header]':
        width = int(f.parse_lines()[6:])
        height = int(f.parse_lines()[7:])
        self.mapClass.init(width, height)
        
      elif line == '[layer]':
        line=f.parse_lines()
        type = line.split('=')[1] #get the word after '='
        f.parse_lines()
        mapMatrix = np.empty((width, height), dtype='int') #syntax is wrong
        for j in range(0, height):
          dlist=parse_data(f.parse_lines())
          for i in range(0, width):
            mapMatrix[i][j]=int(dlist[i])-1 #Tiled is 1 indexed
        self.mapclass.setMap(type, mapMatrix)
        
        
        
        
        if type == 'staticObjects':
          f.parse_lines()
          for j in range(0,int1):
            dlist=parse_data(f.parse_lines())
            for i in range(0,int0):
              class1.statmap[i][j]=int(dlist[i])-1 #Tiled is 1 indexed
        
        elif type == 'gameObjects':
          f.parse_lines()
          for j in range(0, height):
            dlist=parse_data(f.parse_lines())
            for i in range(0, width):
              objtype=int(dlist[i])-1
              if objtype==-1:
                continue
              #instantiate mobs
              if objtype==0: #player
                x = float(i)
                y = float(j)
                self.playerClass.gameObject = soldierFactory.create(x, y)
                self.playerClass.gameObject.objectType = 'Player'
                mob = playerclass
                
              if objtype==1: #soldier
                x = float(i)
                y = float(j)
                mob = soldierFactory.create(x, y)
              self.mobs[mob.id]=mob
              
      #restart loop, get next line
      line=f.parse_lines()
