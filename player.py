
from config       import *
import AI
from utils        import *
import weapons
import math_utils

global Done

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

    # update global DATA
    DATA["screen_location"] = screenLocation
  
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
    self.keyboard_convertDict = {pygame.K_a:   'left',
                        pygame.K_d:  'right',
                        pygame.K_w:     'up',
                        pygame.K_s:   'down',
                        pygame.K_SPACE:  'interact',
                        pygame.K_ESCAPE: 'exit',
                        pygame.QUIT:     'exit',
                        pygame.K_e:      'edit',
                        pygame.K_RCTRL: 'attack',
                        pygame.K_1:     'use_item1',
                        1:   'attack',
                        2:   'use_item1',
                        3:   'switch_weapon',
                        4:   'switch_weapon',
                        5:   'switch_weapon',
                        }
    # https://stackoverflow.com/questions/34287938/how-to-distinguish-left-click-right-click-mouse-clicks-in-pygame 

  def get_action(self, key):
    if key in self.keyboard_convertDict:
      #print(self.keyboard_convertDict[key])
      return self.keyboard_convertDict[key]
    else:
      return ''
      
  def getRealTimeAction(self, status):
    actions = []
    for key in self.keyboard_convertDict:
      if status[key]: actions.append(self.keyboard_convertDict[key])
    return actions

class Logitech():
  A = 0
  LB = 4
  RB = 5

class Joystick(Keyboard):
  def __init__(self):
    pygame.joystick.init()
    self.joystick = pygame.joystick.Joystick(0)
    self.joystick.init()

    self.keyboard_convertDict = {Logitech.A:  '',
                        Logitech.LB:     'attack',
                        Logitech.RB:  'interact',
                        }

    self.action_to_button = dict([[v,k] for k,v in self.keyboard_convertDict.items()])

  def continuous_attack(self):
    if self.joystick.get_button(self.action_to_button["attack"]):
      return True

  def get_direction(self):
    """ axis 0 and 1, already normalized from [-1.0, 1.0]
    """
    xdir = self.joystick.get_axis(0)
    ydir = self.joystick.get_axis(1)
    #
    dir = np.array([xdir, ydir])
    dir[np.abs(dir) < 0.1] = 0.0
    return dir


class Player(AI.Basic):
  def __init__(self, *args, **kwargs):
    #default values
    self.gameObject = None
    self.screenClass = Screen()
    self.keyboard = Keyboard()
    try:
      self.joystick = Joystick()
      self.use_joystick = True
    except:
      self.joystick = None
      self.use_joystick = False
    self.weapon_idx = 3

    self.cbs_to_call = []

  def next_weapon(self):
      self.weapon_idx += 1
      self.weapon_idx %= len(weapons.weapons_list)
      self.gameObject.attacker.change_weapon( weapons.weapons_list[self.weapon_idx] )
    
  def setGameObject(self, object):
    self.parent = object
    self.gameObject = object
    self.gameObject.objectType = 'Player'

    # over-ride AI
    self.gameObject.AI = self
    
  def update(self, events):
    #convert keyboard+mouse events into actions
    dx = 0; dy = 0
    actions = []
    for event in events:
      if event.type == pygame.KEYDOWN:
        action = self.keyboard.get_action(event.key)
      elif event.type == pygame.JOYBUTTONDOWN:
        # with members: joy (which joystick), button
        action = self.joystick.get_action(event.button)
      elif event.type == pygame.MOUSEBUTTONDOWN:
        action = self.keyboard.get_action(event.button)
      else:
        action = ""
      #
      if action not in actions:
        actions.append(action)
      if action is 'interact':
        pass


      if action is 'exit':     Done = True
      if action is 'edit':
        #turn on edit mode
        print('edit mode')
      if action == "use_item1": self.gameObject.inventory.use_item("Potion")
      if action is 'attack': self.cbs_to_call.append(action)
        
    # real-time events -- meaning, keys that are continuously held down
    status = pygame.key.get_pressed()
    status_mouse = pygame.mouse.get_pressed()
    if self.use_joystick:
      movement = self.joystick.get_direction()
      # scale by squaring, for more sensitivity at smaller joystick values
      movement = np.multiply(movement, np.abs(movement))
      dx = movement[0]
      dy = movement[1]

      # continuous weapon
      if self.gameObject.attacker.weapon.is_continuous and "attack" not in self.cbs_to_call:
        if self.joystick.continuous_attack(): self.cbs_to_call.append("attack")
    else:
      realTimeActions = self.keyboard.getRealTimeAction(status)
      for aa in realTimeActions:
        if aa == 'left':  dx -= 1
        if aa == 'right': dx += 1
        if aa == 'up':    dy -= 1
        if aa == 'down':  dy += 1
      if abs(dx) > 0.0 and abs(dy) > 0.0: #moving diagonally
        dx *= 0.707106
        dy *= 0.707106

      # continuous weapon
      if self.gameObject.attacker.weapon.is_continuous and "attack" not in self.cbs_to_call:
        # keys = [i for i in range(3) if status_mouse[i]]
        # action = self.keyboard.get_action(event.button)
        if status_mouse[0]: 
          self.cbs_to_call.append("attack")
      
    # scale to max velocity
    dx *= self.gameObject.max_velocity
    dy *= self.gameObject.max_velocity
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
    
    
    
    
