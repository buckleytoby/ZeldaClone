
from config       import *
from AI           import *


class Screen(object):
  #class to deal with screen-scrolling n shit
  def __init__(self):
    self.screenLocationX = 0.0
    self.screenLocationY = 0.0
    self.offsetX = -1.0 * screenTileWidth / 2.0
    self.offsetY = -1.0 * screenTileHeight / 2.0
  
  def update(self, x, y):
    screenLocation = np.array([x + self.offsetX, y + self.offsetY])

    self.screenLocationX, self.screenLocationY = screenLocation.tolist()
  
  def getLocation(self):
    return (self.screenLocationX, self.screenLocationY)

class Keyboard(object):
  #specify conversion from keyboard event to player action
  def __init__(self):
    self.convertDict = {pygame.K_LEFT:   'left',
                        pygame.K_RIGHT:  'right',
                        pygame.K_UP:     'up',
                        pygame.K_DOWN:   'down',
                        pygame.K_SPACE:  'interact',
                        pygame.K_ESCAPE: 'exit',
                        pygame.QUIT:     'exit',
                        pygame.K_e:      'edit',
                        pygame.K_RSHIFT: 'attack',
                        }

  def getAction(self, key):
    if key in self.convertDict:
      print(self.convertDict[key])
      return self.convertDict[key]
    else:
      return ''
      
  def getRealTimeAction(self, status):
    actions = []
    for key in self.convertDict:
      if status[key]: actions.append(self.convertDict[key])
    return actions

class Player(object):
  def __init__(self):
    #default values
    self.gameObject = None
    self.screenClass = Screen()
    self.keyboard = Keyboard()

    self.callbacks = {}
    self.callbacks['attack'] = self.attack

  def attack(self):
    pass
    
  def setGameObject(self, object):
    self.gameObject = object
    self.gameObject.objectType = 'Player'
    self.gameObject.spriteType = 'Player'
    self.gameObject.AI = self
    
  def update(self, events):
    #convert keyboard+mouse events into actions
    dx = 0; dy = 0
    actions = []
    callCallbacks = []
    for event in events:
      if event.type==pygame.KEYDOWN:
        action = self.keyboard.getAction(event.key)
        if action not in actions:
          actions.append(action)
        if action is 'interact': pass
        if action is 'exit':     pass
        if action is 'edit':
          #turn on edit mode
          print('edit mode')
        if action is 'attack': callCallbacks.append(action)
        
      elif event.type==pygame.QUIT: sys.exit()
    # real-time events
    status = pygame.key.get_pressed()
    realTimeActions = self.keyboard.getRealTimeAction(status)
    for realTimeActions in realTimeActions:
      if realTimeActions is 'left':  dx -= 1
      if realTimeActions is 'right': dx += 1
      if realTimeActions is 'up':    dy -= 1
      if realTimeActions is 'down':  dy += 1
      
    # movement
    dx *= round(self.gameObject.velocity)
    dy *= round(self.gameObject.velocity)
    if abs(dx) == abs(dy) == 1: #moving diagonally
      dx *= 0.707106
      dy *= 0.707106
    self.dx=dx
    self.dy=dy
    self.dt = 0
    # callbacks
    for callback in callCallbacks:
      self.callbacks[callback]()
    
    
    self.screenClass.update(self.gameObject.x, self.gameObject.y)
    return actions
    
  def getAction(self):
    return (self.dx, self.dy)
    
    
    
    
