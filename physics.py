

from config       import *


class Physics(object):
  #physics object for the map
  # 
  # input a handle to static objects and moving mobs
  # each object must contain x, y, width, height, and mass attributes
  #
  def __init__(self):
    self.force = 50 #N
    self.gameObjects = None
    self.gameObjectsARR = None
      
  def update(self, timeElapsed, gameObjects):
    dt = timeElapsed
    
    for key in gameObjects:
      gameObject = gameObjects[key]
      dx, dy = gameObject.AI.getAction()
      gameObject.animation.updateSprite(dx, dy)
      gameObject.x += dt * dx
      gameObject.y += dt * dy
    
      