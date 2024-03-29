

from config       import *
from utils        import *
from world        import *
from player       import *
from gameObjects  import *
from physics      import *
from classHolder  import *
from AI           import *
from debug        import *
import weapons


# -----------------------------------------------


debug_mode = True
Done = False # global




# -----------------------------------------------
    
    
    
class MasterClass(object):
  #use this class to actually specify specifics for the game / levels, later can replace hard-coded with text input
  def __init__(self, screen):
    """ initialize the game and set up the classes
    """
    self.screen = screen

    # make debugger
    if debug_mode:
      self.debugger = Debug(self)
    
    # title screen
    prefix = r'[GAME_ROOT]' # raw string
    config = os.path.join(prefix, "config", "lvl1.txt")
    lvl1 = ClassHolder(config)
    
    # load config
    lvl1.loadConfigFile()
    # bake the map
    lvl1.worldClass.bake_tiles()

    # play background music
    if SOUND_ON:
      lvl1.CHANGE_MUSIC("song1")
    
    # main game
    config = os.path.join(prefix, "config", "main.txt")
    # self.main = ClassHolder(config)
    # load config
    # self.main.loadConfigFile()
    
    # group all holders
    self.holders = [lvl1,
                    "n/a"]
                    
    # set initial holder
    self.set_holder(self.holders[0])

  def set_holder(self, holder):
    """ update holder, and update DATA """
    self.holder = holder
    DATA["game_objects_ref"] = self.holder.gameObjects
    DATA["trigger_areas_ref"] = self.holder.trigger_areas
    DATA["factories_ref"] = self.holder.factories
    print("# game objects: {}".format(len(DATA["game_objects_ref"]))) # DEBUG
    DATA["player_xy"] = self.holder.playerClass.gameObject.center_of_mass
      
  # @profile
  def update(self, seconds, events):
    """ update each part of the game's engine
    """
    # update debug box
    if debug_mode:
      self.debugger.update()

    # update holder
    self.holder.update()
    # update game with keyboard events
    actions = self.holder.playerClass.update(events)

    # process actions
    self.process_actions(actions)

    # update physics with time passage
    self.holder.physicsClass.update(seconds, self.holder.gameObjects, self.holder.new_game_objects, self.holder.worldClass, 'staticObjects')

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
      global Done
      Done = True # global
      print("Exit")

    if 'interact' in actions:
      # gather gameobjects within reach
      rect = self.holder.playerClass.gameObject.reach_rect.convert_to_pygame_rect()
      hits = self.holder.physicsClass.go_tree.hit(rect)
      gos = {go.id: go for go in hits}
      
      for id in gos:
        go = self.holder.gameObjects[id]
        # use doors
        if go.type == "door":
          pass

        # pick up items
        elif go.type == "item":
          # make item
          item = go.item_maker(go, self.holder.playerClass.gameObject)

          # add item
          self.holder.playerClass.gameObject.inventory.add_item(item)

          # destroy go
          die(go)

      # if self.holder == self.title:
      #   pass
        # self.holder = self.main

    if 'switch_weapon' in actions:
      # switch weapon
      self.holder.playerClass.next_weapon()
      print("Switched to: {}".format( self.holder.playerClass.gameObject.attacker.weapon.name ) )

    if 'use_object' in actions:
      pass

  def close_game(self):
    if debug_mode:
        self.debugger.finish()

# @profile
def main():
  # init the clock
  clock = pygame.time.Clock()
  FPS = 30
  seconds = 0.0
  milli = 0.0

  # init pygame

  # os.environ['SDL_VIDEO_WINDOW_POS'] = '800,50'
  os.environ['SDL_VIDEO_CENTERED'] = '1'
  pygame.init()
  #logo=pygame.image.load("logo filename")
  #pygame.display.set_icon(logo)
  pygame.display.set_caption('Ephiro') #Eponymous Hero -> EpHero -> Ephiro
  screen=pygame.display.set_mode([int(i) for i in scrsize])
  World.screen = screen

  # instantiate starting classes
  master = MasterClass(screen)

  # ----------------------------------------------------------------------
  # main loop:
  while not Done:
    screen.fill((0,0,0)) #black background
    
    #update game world
    seconds = clock.tick(FPS) / 1000.0
    # force each update to be 1 / FPS seconds, so that lag doesn't send objects flying
    seconds = 1.0 / FPS
    master.update(seconds, pygame.event.get())
    
    #write screen
    master.writeScreen()

    #display screen
    pygame.display.flip()
    
  master.close_game()

  # close down pygame, tkinter and then exit
  pygame.quit()
  sys.exit()
  
  
if __name__ == "__main__":
  main()
  print("Main Thread Done")
  
  
  
  
  
  
  
  
  
  
  
  
  
  
