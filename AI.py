

from config       import *


class AttackModule(object):


  def attack(self):
    face = self.animation.face
    attackBox = self.getAttackBox(face)
    enemiesInBox = self.queryGameObjects(attackBox)
    for ID in enemiesInBox:
    	self.gameObjects[ID].health -= self.power
    	vector = self.gameObjects[ID].position - self.position
    	knockbackVector = vector * self.knockback
    	self.gameObjects[ID].position -= knockbackVector





class AI(object):

  def __init__(self):
    self.dx = 0.0
    self.dy = 0.0
  
  def getAction(self):
    out = {'dv': np.array([self.dx, self.dy])}
    return out