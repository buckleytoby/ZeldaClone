

from config       import *
from utils        import *
from world        import *
from player       import *
from gameObjects  import *
from physics      import *
from classHolder  import *
from AI           import *

    
    
    
class MasterClass(object):
  #use this class to actually specify specifics for the game / levels, later can replace hard-coded with text input
  def __init__(self, screen):
    """ initialize the game and set up the classes
    """
    self.screen = screen
    
    # title screen
    prefix = r'[GAME_ROOT]' # raw string
    config = os.path.join(prefix, "config", "title.txt")
    self.title = ClassHolder(config)
    self.title.worldClass = TitleScreen()
    # load config
    self.title.loadConfigFile()
    
    # main game
    config = os.path.join(prefix, "config", "main.txt")
    self.main = ClassHolder(config)
    # load config
    self.main.loadConfigFile()
    
    # group all holders
    self.holders = [self.title,
                    self.main]
                    
    # set initial holder
    self.holder = self.title
      
  def update(self, seconds, events):
    """ update each part of the game's engine
    """
    # update holder
    self.holder.update()
    # update game with keyboard events
    actions = self.holder.playerClass.update(events)

    # process actions
    self.process_actions(actions)

    # update physics with time passage
    self.holder.physicsClass.update(seconds, self.holder.gameObjects, self.holder.worldClass, 'staticObjects')

    # update screen
    self.holder.playerClass.screenClass.update(self.holder.playerClass.gameObject.x, self.holder.playerClass.gameObject.y)

    # add to data stream
    DATA["player_xy"] = self.holder.playerClass.position
    DATA["game_time"] = pygame.time.get_ticks() / 1000.0
    
  def writeScreen(self):
    """ write the user screen
    """
    self.holder.writeScreen()

  def process_actions(self, actions):
    """ process player actions
    """
    
    if 'exit' in actions:
      # save & exit
      sys.exit()

    if 'interact' in actions:
      if self.holder == self.title:
        pass
        # self.holder = self.main

    if 'use_object' in actions:
      # if not in front of anything, use weapon
      if True:
        self.holder.playerClass.attack()

    




clock = pygame.time.Clock()
FPS = 30
seconds = 0.0
milli = 0.0

#init
os.environ['SDL_VIDEO_WINDOW_POS'] = '800,50'
pygame.init()
#logo=pygame.image.load("logo filename")
#pygame.display.set_icon(logo)
pygame.display.set_caption('Ephiro') #Eponymous Hero -> EpHero -> Ephiro
screen=pygame.display.set_mode([int(i) for i in scrsize])
World.screen = screen

# instantiate starting classes
master = MasterClass(screen)

ipics = 0


#main loop:
while 1:
  screen.fill((0,0,0)) #black background
  
  #update game world
  seconds=clock.tick(FPS)/1000.0
  master.update(seconds, pygame.event.get())
  
  #write screen
  master.writeScreen()

  #pygame.image.save(screen, 'pics\image'+str(ipics)+'.png')
  ipics += 1
  #display screen
  pygame.display.flip() 
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
