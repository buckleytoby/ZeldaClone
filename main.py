

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
    self.screen = screen
    
    # title screen
    config = r'/home/offworld5/Fun/ZeldaClone/config/title.txt'
    self.title = ClassHolder(config)
    self.title.worldClass = TitleScreen()
    # load config
    self.title.loadConfigFile()
    
    # main game
    config = r'/home/offworld5/Fun/ZeldaClone/config/main.txt'
    self.main = ClassHolder(config)
    # load config
    self.main.loadConfigFile()
    
    # group all holders
    self.holders = [self.title,
                    self.main]
                    
    # set initial holder
    self.holder = self.title
      
  def update(self, seconds, events):
    # update game with keyboard events
    actions = self.holder.playerClass.update(events)

    # update physics with time passage
    self.holder.physicsClass.update(seconds, self.holder.gameObjects)

    # update screen
    self.holder.playerClass.screenClass.update(self.holder.playerClass.gameObject.x, self.holder.playerClass.gameObject.y)
    
    # check for high-level player actions
    if 'interact' in actions and self.holder == self.title:
      self.holder = self.main
    
    if 'exit' in actions:
      # save & exit
      sys.exit()
    
  def writeScreen(self):
    self.holder.writeScreen()
    




clock=pygame.time.Clock()
FPS=30
seconds=0.0
milli=0.0

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

ipics=0


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
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
