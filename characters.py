
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
    self.values['artWidth']      = 1.0 * 2.0
    self.values['artHeight']     = 1.5 * 2.0
    self.values['mass']       = 100.0 # kg
    self.values['pixelWidth'] = 16 # size of the sprite image
    self.values['pixelHeight'] = 24 # size of the sprite image
    self.values['max_velocity'] = 2.0 #m/s
    self.values['objectType'] = 'Soldier'

  
  def create(self, x, y):
    self.values['attacker'] = attack.Attacker(weapons.soldierWeapon1FCT) # want unique instance
    object = super(SoldierFactory, self).create(x, y)

    # set AI type
    object.AI = AI.Basic_Attacker(object)
    # object.AI = AI.Basic(object)

    # callbacks
    getattr(object, 'callbacks')['attack'] = object.attacker.attack

    # setup
    object.setSpriteStatus(visible=True, has_sprite=True, spriteType='Soldier')
    return object

class PlayerFactory(SoldierFactory):
  def __init__(self):
    super(PlayerFactory, self).__init__()
    self.values['max_velocity'] = 6.0 #m/s
    self.values['artWidth']      = 1.0
    self.values['artHeight']     = 1.5

  def create(self, x, y):
    self.values['attacker'] = attack.Attacker(weapons.playerWeapon1FCT) # want unique instance
    object = super(SoldierFactory, self).create(x, y)

    # callbacks
    getattr(object, 'callbacks')['attack'] = object.attacker.attack

    # setup
    object.setSpriteStatus(visible=True, has_sprite=True, spriteType='Soldier')
    return object