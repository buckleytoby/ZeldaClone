

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

  def __init__(self, parent):
    self.parent = parent
    self.dx = 0.0
    self.dy = 0.0

  def get_position(self):
    out = self.parent.position
    return out
  position = property(get_position)
  
  def getAction(self):
    dv = np.zeros(2)
    me = self.position
    if 'player_xy' in DATA:
      target = np.array(DATA['player_xy'])
      vector = target - me
      if not np.allclose(vector, np.zeros(2)):
        unit_direction = vector / np.linalg.norm(vector)
        dv = self.parent.max_velocity * unit_direction

    out = {'dv': dv}
    #out = {'dv': np.array([self.dx, self.dy])}
    return out