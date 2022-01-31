

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
  
  def get_action(self, elapsed_time):
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
        unit_direction = math_utils.divide_vector(vector, np.linalg.norm(vector))
    return unit_direction, dist

  def get_dv(self):
    dv = np.zeros(2)
    unit_direction, dist = self.get_dir_to_move()
    if not np.allclose(unit_direction, 0.0):
      dv = self.parent.max_velocity * unit_direction

    return dv, dist

  def get_action(self, elapsed_time):
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
    
    self.elapsed_time = 0.0
    self.update_rate = 1.0
    self.old_dv = np.zeros(2)
    self.old_dist = 0.0

  def reset_wait(self):
    self.wait = False

  def get_action(self, elapsed_time):
    cbs = []
    
    # only update at rate
    self.elapsed_time += elapsed_time
    if self.elapsed_time > self.update_rate:
      self.elapsed_time -= self.update_rate
      # update dv
      dv, dist = self.get_dv()
      self.old_dv = dv
      self.old_dist = dist
    else:
      dv = self.old_dv
      dist = self.old_dist

    # decide to attack
    if self.wait:
      out = {'dv': dv}
    else:
      out = {'dv': dv}
      # attack if close enough
      if dist < self.dist_threshold:
        cbs.append("attack")

        # trigger cool-down
        self.wait = True
        threading.Timer(self.cooldown, self.reset_wait).start()

    return out, cbs

class Avoider(Basic):
  def __init__(self, *args):
    super().__init__(*args)
    self.dist_tol = 5.0
    self.dist_multiplier = 1.0
    self.dist_threshold = 1.5
    
    self.elapsed_time = 0.0
    self.update_rate = 0.1
    self.old_dv = np.zeros(2)

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
          # mult = np.clip( math_utils.zero_protection_divide(self.dist_multiplier, dist_to_dmg), -1.0, 1.0)
          # mult = np.clip( math_utils.divide_vector(self.dist_multiplier, dist_to_dmg), -1.0, 1.0)
          # direction += mult * math_utils.normalize(com_vector)
          direction += math_utils.normalize(com_vector)
          # print("direction: {}".format(direction))

    out = math_utils.normalize(direction)
    return out
    
  def get_dv(self):
    dv = np.zeros(2)
    unit_direction = self.get_avoid_dir()
    if not np.allclose(unit_direction, 0.0):
      dv = self.parent.max_velocity * unit_direction
    return dv

  def get_action(self, elapsed_time):
    # only update at rate
    self.elapsed_time += elapsed_time
    if self.elapsed_time > self.update_rate:
      print("time: {}".format(self.elapsed_time))
      self.elapsed_time -= self.update_rate
      # update dv
      dv = self.get_dv()
      self.old_dv = dv
    else:
      dv = self.old_dv
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
          # mult = np.clip( math_utils.vector_divide(self.dist_multiplier, dist_to_dmg), -1.0, 1.0)
          # direction += mult * math_utils.normalize(com_vector)
          direction += math_utils.normalize(com_vector)
          # print("direction: {}".format(direction))

    out = math_utils.normalize(direction)
    return out

class Boss1Phase1(Basic):
  # move from side to side, firing ball on chains
  def __init__(self, *args):
    super().__init__(*args)
    self.wait = False
    self.b_move = True
    self.attack_cooldown = 0.87
    self.move_cooldown = 10.0
    self.dist_threshold = 1.5

    # TODO: don't trigger until boss is activated
    self.toggle_move()

  def reset_wait(self):
    self.wait = False

  def toggle_move(self): 
    self.b_move = not self.b_move
    threading.Timer(self.move_cooldown, self.toggle_move).start()

  def get_dv(self):
    if self.b_move: # move right
      dv = np.array([1, 0]) * self.parent.max_velocity
    else: # move left
      dv = np.array([-1, 0]) * self.parent.max_velocity
    return dv

  def get_action(self, elapsed_time):
    cbs = []
    dv = self.get_dv()

    out = {'dv': dv}
    if not self.wait:
      cbs.append("attack")

      # trigger cool-down
      self.wait = True
      threading.Timer(self.attack_cooldown, self.reset_wait).start()

    return out, cbs

class Boss1Phase2(Basic_Attacker):
  # chase player around
  def __init__(self, *args):
    super().__init__(*args)
    self.cooldown = 0.79
    self.dist_threshold = 15.0
    self.max_dist_threshold = 20.0
    
class Boss1Phase3(Basic_Attacker):
  # fire spread of straight projectiles
  def __init__(self, *args):
    super().__init__(*args)
    self.dist_threshold = 15.0
    self.max_dist_threshold = 25.0

  def get_dv(self):
    obj_target = utils.get_trigger_area('boss1center')
    if obj_target:
      target = obj_target.rect.center
      unit_dir = math_utils.dir_to_target(self.position, target)
      dist = np.linalg.norm(target - self.position)
      if dist > 0.1:
        dv = unit_dir * self.parent.max_velocity
      else:
        dv = np.zeros(2)
        dist = 0.0
    else:
      dv = np.zeros(2)
      dist = 0.0

    return dv, dist

class Boss1Meta(Basic):
  # manage Boss AI's and switch between them
  def __init__(self, *args):
    super().__init__(*args)

    self.AIs = [Boss1Phase1(*args),
                Boss1Phase2(*args),
                Boss1Phase3(*args),
                ]
    self.health_cutoffs = [67, 33]

    self.active_ai = self.AIs[0]
    self.b_phase2 = False
    self.b_phase3 = False

  def update(self):
    percent = 100.0 * self.parent.attacker.health / self.parent.attacker.max_health
    if not self.b_phase2 and percent < self.health_cutoffs[0]:
      self.b_phase2 = True
      self.active_ai = self.AIs[1]
    elif not self.b_phase3 and percent < self.health_cutoffs[1]:
      self.b_phase3 = True
      self.active_ai = self.AIs[2]
      # change weapon
      self.parent.inventory.use_item("Boss1Weapon2")


  def get_action(self, elapsed_time):
    self.update()
    return self.active_ai.get_action()
    