

from config       import *
import threading
import attack
import utils
import math_utils

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
    self.attack_threshold = 2.0
    self.max_dist_threshold = 7.5

  def get_dir_to_move(self):
    dist = 9999.0
    unit_direction = np.zeros(2)
    me = self.position
    if 'player_xy' in DATA:
      target = np.array(DATA['player_xy'])
      vector = target - me
      dist = np.linalg.norm(vector)
      if  dist > self.attack_threshold and dist < self.max_dist_threshold:
        unit_direction = math_utils.zero_protection_divide(vector, np.linalg.norm(vector))
    return unit_direction, dist

  def get_dv(self):
    dv = np.zeros(2)
    unit_direction, dist = self.get_dir_to_move()
    if not np.allclose(unit_direction, 0.0):
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

class Avoider(Basic):
  def __init__(self, *args):
    super().__init__(*args)
    self.dist_tol = 5.0
    self.dist_multiplier = 1.0
    self.dist_threshold = 1.5

  def get_avoid_dir(self):
    direction = np.zeros(2)

    # force-field away from incoming attacks
    gos = utils.get_game_objects()
    for key in gos:
      go = gos[key]
      # different team
      if go.team_id != self.parent.team_id:
        # calc dist to parent
        com_vector = go.com_vector(self.parent)
        dist_to_dmg = go.dist_to_other(self.parent)

        if dist_to_dmg > self.dist_tol:
          continue
        else:
          # normalize, inversely proportional 
          mult = np.clip( math_utils.zero_protection_divide(self.dist_multiplier, dist_to_dmg), -1.0, 1.0)
          direction += mult * math_utils.normalize(com_vector)
          # print("direction: {}".format(direction))

    out = math_utils.normalize(direction)
    return out
    
  def get_dv(self):
    dv = np.zeros(2)
    unit_direction = self.get_avoid_dir()
    if not np.allclose(unit_direction, 0.0):
      dv = self.parent.max_velocity * unit_direction
    return dv

  def get_action(self):
    dv = self.get_dv()
    out = {'dv': dv}
    cbs = []
    return out, cbs

class AvoiderAttacker(Basic_Attacker, Avoider):
  """ follows the player while avoiding attacks """

  def get_dir_to_move(self):
    """ from game-objects handle, get CG of all attacks

    """
    direction, dist = super().get_dir_to_move()
    direction += self.get_avoid_dir()
    unit_direction = math_utils.normalize(direction)
    return unit_direction, dist

    
class DmgAvoiderAttacker(AvoiderAttacker):

  def get_avoid_dir(self):
    direction = np.zeros(2)

    # force-field away from incoming attacks
    gos = utils.get_game_objects()
    for key in gos:
      go = gos[key]
      # different team
      if go.type == "damage" and go.team_id != self.parent.team_id:
        # calc dist to parent
        com_vector = go.com_vector(self.parent)
        dist_to_dmg = go.dist_to_other(self.parent)

        if dist_to_dmg > self.dist_tol:
          continue
        else:
          # normalize, inversely proportional 
          mult = np.clip( math_utils.zero_protection_divide(self.dist_multiplier, dist_to_dmg), -1.0, 1.0)
          direction += mult * math_utils.normalize(com_vector)
          # print("direction: {}".format(direction))

    out = math_utils.normalize(direction)
    return out