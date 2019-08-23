

from config       import *
import threading


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



class Basic(object):
  def __init__(self, parent):
    self.parent = parent
    self.dx = 0.0
    self.dy = 0.0

  def get_position(self):
    out = self.parent.position
    return out
  position = property(get_position)
  
  def get_action(self):
    """ non-action base function """
    dv = np.zeros(2)
    out = {'dv': dv}
    cbs = []
    return out, cbs

class Follower(Basic):
  """ follows the player """
  def __init__(self, *args):
    super().__init__(*args)
    self.dist_threshold = 2.0

  def get_dv(self):
    dv = np.zeros(2)
    dist = 0.0
    me = self.position
    if 'player_xy' in DATA:
      target = np.array(DATA['player_xy'])
      vector = target - me
      dist = np.linalg.norm(vector)
      if  dist > self.dist_threshold:
        unit_direction = vector / np.linalg.norm(vector)
        dv = self.parent.max_velocity * unit_direction

    return dv, dist

  def get_action(self):
    dv, dist = self.get_dv()
    out = {'dv': dv}
    cbs = []
    return out, cbs

class Basic_Attacker(Follower):
  """ follows the player and attacks when near """
  def __init__(self, *args):
    super().__init__(*args)
    self.wait = False
    self.cooldown = 2.0
    self.dist_threshold = 1.5

  def reset_wait(self):
    self.wait = False

  def get_action(self):
    cbs = []
    dv, dist = self.get_dv()

    if self.wait:
      out = {'dv': np.zeros(2)}
    else:
      out = {'dv': dv}
      # attack if close enough
      if dist < self.dist_threshold:
        cbs.append("attack")

        # trigger cool-down
        threading.Timer(self.cooldown, self.reset_wait).start()

    return out, cbs