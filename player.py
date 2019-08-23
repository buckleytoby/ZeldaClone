
from config       import *
import AI
from utils        import *


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

  def get_footprint_rect(self):
    """ get pygame Rect of the object's footprint. i.e. the portion that can be collided with.
    """
    lt = self.getLocation()
    wh = [screenTileWidth, screenTileHeight]
    x, y = [lt[0], lt[0] + wh[0]], [lt[1], lt[1] + wh[1]]
    rect = PatchExt([x, y]) # xxyy_limits' a sequence of two pairs: [[x_low, x_high], [y_low, y_high]]
    #rect = pygame.Rect(lt, wh) # Rect(left, top, width, height) -> Rect
    return rect
  rect = property(get_footprint_rect)

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
                        pygame.K_RCTRL: 'attack',
                        }

  def get_action(self, key):
    if key in self.convertDict:
      #print(self.convertDict[key])
      return self.convertDict[key]
    else:
      return ''
      
  def getRealTimeAction(self, status):
    actions = []
    for key in self.convertDict:
      if status[key]: actions.append(self.convertDict[key])
    return actions

class Player(AI.Basic):
  def __init__(self, *args, **kwargs):
    #default values
    self.gameObject = None
    self.screenClass = Screen()
    self.keyboard = Keyboard()

    self.cbs_to_call = []
    
  def setGameObject(self, object):
    self.parent = object
    self.gameObject = object
    self.gameObject.objectType = 'Player'
    self.gameObject.spriteType = 'Player'

    # over-ride AI
    self.gameObject.AI = self
    
  def update(self, events):
    #convert keyboard+mouse events into actions
    dx = 0; dy = 0
    actions = []
    for event in events:
      if event.type == pygame.KEYDOWN:
        action = self.keyboard.get_action(event.key)
        if action not in actions:
          actions.append(action)
        if action is 'interact': pass
        if action is 'exit':     pass
        if action is 'edit':
          #turn on edit mode
          print('edit mode')
        if action is 'attack': self.cbs_to_call.append(action)
        
      elif event.type == pygame.QUIT: sys.exit()
    # real-time events
    status = pygame.key.get_pressed()
    realTimeActions = self.keyboard.getRealTimeAction(status)
    for realTimeActions in realTimeActions:
      if realTimeActions is 'left':  dx -= 1
      if realTimeActions is 'right': dx += 1
      if realTimeActions is 'up':    dy -= 1
      if realTimeActions is 'down':  dy += 1
      
    # movement
    dx *= round(self.gameObject.max_velocity)
    dy *= round(self.gameObject.max_velocity)
    if abs(dx) > 0.0 and abs(dy) > 0.0: #moving diagonally
      dx *= 0.707106
      dy *= 0.707106
    self.dx = dx
    self.dy = dy
    self.dt = 0
    
    return actions
  
  def get_action(self):
    out = {'dv': np.array([self.dx, self.dy])}
    cbs = self.cbs_to_call
    # clear cbs
    self.cbs_to_call = []
    return out, cbs
    
    
    
    
