
from config       import *
from utils        import *
import factory
import attack
import weapons
import AI
  
  
class SoldierFactory(factory.GameObjectFactory):
  def __init__(self):
    super(SoldierFactory, self).__init__()
    self.values['width']      = 1.0
    self.values['height']     = 1.0
    self.values['artWidth']      = 1.0
    self.values['artHeight']     = 1.5
    self.values['mass']       = 100.0 # kg
    self.values['pixelWidth'] = 16 # size of the sprite image, depends on image size, shouldn't change
    self.values['pixelHeight'] = 24 # size of the sprite image, depends on image size, shouldn't change
    self.values['max_velocity'] = 3.0 #m/s
    self.values['objectType'] = 'Soldier'
    self.values['type'] = "character"
    self.values['team_id'] = 1
    self.ai_class = AI.DmgAvoiderAttacker

  
  def create(self, x, y):
    self.values['attacker'] = attack.Attacker(weapons.soldierWeapon1FCT) # want unique instance
    object = super(SoldierFactory, self).create(x, y)

    # set AI type
    object.AI = self.ai_class(object)
    # object.AI = AI.Basic(object)

    # callbacks
    getattr(object, 'callbacks')['attack'] = object.attacker.attack

    # setup
    object.setSpriteStatus(visible=True, has_sprite=True)
    return object

class PlayerFactory(SoldierFactory):
  def __init__(self):
    super(PlayerFactory, self).__init__()
    self.values['max_velocity'] = 6.0 #m/s
    self.values['artWidth']      = 1.0
    self.values['artHeight']     = 1.5
    self.values['team_id'] = 0

  def create(self, x, y):
    # self.values['attacker'] = attack.Attacker(weapons.playerWeapon1FCT) # want unique instance
    self.values['attacker'] = attack.Attacker(weapons.weapons_list[0]) # want unique instance
    object = super(SoldierFactory, self).create(x, y)

    # set health
    object.attacker.health = 200.0

    # callbacks
    getattr(object, 'callbacks')['attack'] = object.attacker.attack

    # setup
    object.setSpriteStatus(visible=True, has_sprite=True)
    return object


class MiniSoldierFactory(SoldierFactory):
  def __init__(self):
    super().__init__()
    factor = 0.75
    self.values['width']      = 1.0 * factor
    self.values['height']     = 1.0 * factor
    self.values['artWidth']      = 1.0 * factor
    self.values['artHeight']     = 1.5 * factor
    self.values['mass']       = 100.0 # kg
    self.values['max_velocity'] = 3.0 / factor #m/s
    self.values['objectType'] = 'MiniSoldier'
    self.ai_class = AI.AvoiderAttacker


class MegaSoldierFactory(SoldierFactory):
  def __init__(self):
    super().__init__()
    factor = 4.0
    self.values['width']      = 1.0 * factor
    self.values['height']     = 1.0 * factor
    self.values['artWidth']      = 1.0 * factor
    self.values['artHeight']     = 1.5 * factor
    self.values['mass']       = 100.0 # kg
    self.values['max_velocity'] = 3.0 / factor #m/s
    self.values['objectType'] = 'MegaSoldier'
    self.ai_class = AI.DmgAvoiderAttacker

class ArcherFactory(factory.GameObjectFactory):
  def __init__(self):
    super().__init__()
    self.values['width']      = 1.0
    self.values['height']     = 1.0
    self.values['artWidth']      = 1.0
    self.values['artHeight']     = 1.5
    self.values['mass']       = 100.0 # kg
    self.values['pixelWidth'] = 16 # size of the sprite image, depends on image size, shouldn't change
    self.values['pixelHeight'] = 24 # size of the sprite image, depends on image size, shouldn't change
    self.values['max_velocity'] = 3.0 #m/s
    self.values['objectType'] = 'Archer' # for drawing purposes
    self.values['type'] = "character"
    self.values['team_id'] = 1
    self.ai_class = AI.DmgAvoiderAttacker
  
  def create(self, x, y):
    self.values['attacker'] = attack.Attacker(weapons.arrow3FCT) # want unique instance
    object = super().create(x, y)

    # set AI type
    object.AI = self.ai_class(object)
    object.AI.dist_threshold = 5.5
    # object.AI = AI.Basic(object)

    # callbacks
    getattr(object, 'callbacks')['attack'] = object.attacker.attack

    # setup
    object.setSpriteStatus(visible=True, has_sprite=True)
    return object