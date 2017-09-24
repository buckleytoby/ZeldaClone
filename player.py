
from config       import *



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
                        pygame.K_e:      'edit'}

  def getAction(key):
    if event.key in self.keyboard.convertDict:
      return self.convertDict[key]
    else:
      return ''

class Player(object):
  def __init__(self):
    #default values
    self.gameObject = None
    self.keyboard = Keyboard()
    
  def update(self, events):
    #convert keyboard+mouse events into actions
    actions = []
    dx = 0; dy = 0
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
        if action is 'left':  dx -= 1
        if action is 'right': dx += 1
        if action is 'up':    dy -= 1
        if action is 'down':  dy += 1
          
            
      elif event.type==pygame.QUIT: sys.exit()
      
    dx *= round(self.gameObject.velocity*self.dt)
    dy *= round(self.gameObject.velocity*self.dt)
    if abs(dx) == abs(dy) == 1: #moving diagonally
      dx *= 0.707106
      dy *= 0.707106
    self.dx=dx
    self.dy=dy
    self.dt = 0
    
    
    self.animationClass.updateSprite(dx, dy)
    return actions
    
    
    
    