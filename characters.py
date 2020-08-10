
from config       import *
from utils        import *
import factory
import attack
import weapons
import AI
import inventory
import particles


defaultAI = AI.DmgAvoiderAttacker
# defaultAI = AI.Basic 
  
  
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
    self.values['max_velocity'] = 2.0 #m/s
    self.values['objectType'] = 'Soldier'
    self.values['type'] = "character"
    self.values['team_id'] = 1
    self.values['hitSoundFX'] = 'grunt1'
    self.values['deathSoundFX'] = 'death1'
    self.values['damage_objects'] = ['Explosion']
    self.values['death_objects'] = ['Blood1', 'Ghost1']
    self.values['weapon'] = weapons.soldierWeapon1FCT
    self.ai_class = defaultAI

  
  def create(self, x, y):
    self.values['attacker'] = attack.Attacker(self.values['weapon']) # want unique instance
    object = super().create(x, y)

    # set health
    if 'health' in self.values: object.attacker.set_health(self.values['health'])

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
    self.values['max_velocity'] = 4.0 #m/s
    self.values['artWidth']      = 1.0
    self.values['artHeight']     = 1.5
    self.values['team_id'] = 0
    self.values['weapon'] = weapons.playerWeapon1FCT

  def create(self, x, y):
    # self.values['attacker'] = attack.Attacker(weapons.playerWeapon1FCT) # want unique instance
    self.values['attacker'] = attack.Attacker(self.values['weapon']) # want unique instance
    object = super().create(x, y)

    # set health
    object.attacker.set_health(200.0)
    object.attacker.mana_regen = 10.0 # mana per second

    # give an inventory
    object.inventory = inventory.Inventory(object)

    # give 5 small health potions
    potion = inventory.Potion(50.0)
    potion.count = 5
    object.inventory.add_item(potion)

    # callbacks
    getattr(object, 'callbacks')['attack'] = object.attacker.attack

    # setup
    object.setSpriteStatus(visible=True, has_sprite=True)
    return object


class MiniSoldierFactory(SoldierFactory):
  def __init__(self):
    super().__init__()
    factor = 0.75
    self.values['width']      *= factor
    self.values['height']     *= factor
    self.values['artWidth']      *= factor
    self.values['artHeight']     *= factor
    self.values['mass']       = 100.0 # kg
    self.values['max_velocity'] = 3.0 / factor #m/s
    self.values['objectType'] = 'MiniSoldier'
    self.ai_class = defaultAI


class MegaSoldierFactory(SoldierFactory):
  factor = 4.0
  def __init__(self):
    super().__init__()
    self.values['width']      *= self.factor
    self.values['height']     *= self.factor
    self.values['artWidth']      *= self.factor
    self.values['artHeight']     *= self.factor
    self.values['mass']       = 100.0 * self.factor # kg
    self.values['max_velocity'] = 3.0 / self.factor #m/s
    self.values['objectType'] = 'MegaSoldier'
    self.values['death_objects'] = ['BigBlood1', 'BigGhost1']
    self.ai_class = defaultAI

class BigGhostParticleFactory(factory.GhostParticleFactory):
  def __init__(self):
    super().__init__()
    self.values['objectType'] = 'BigGhost1' # for drawing purposes
    self.values['width']      = 1.0 * MegaSoldierFactory.factor
    self.values['height']     = 1.0 * MegaSoldierFactory.factor
    self.values['artWidth']      = 1.0 * MegaSoldierFactory.factor
    self.values['artHeight']     = 1.0 * MegaSoldierFactory.factor

class BigBloodParticleFactory(factory.BloodParticleFactory):
  def __init__(self):
    super().__init__()
    self.values['objectType'] = 'BigBlood1' # for drawing purposes
    self.values['width']      = 1.0 * MegaSoldierFactory.factor
    self.values['height']     = 1.0 * MegaSoldierFactory.factor
    self.values['artWidth']      = 1.0 * MegaSoldierFactory.factor
    self.values['artHeight']     = 1.0 * MegaSoldierFactory.factor

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
    self.values['weapon'] = weapons.arrow5FCT
    self.values['hitSoundFX'] = 'grunt1'
    self.values['deathSoundFX'] = 'death1'
    self.values['damage_objects'] = ['Explosion']
    self.values['death_objects'] = ['Blood1', 'Ghost1']
    self.ai_class = defaultAI
  
  def create(self, x, y):
    self.values['attacker'] = attack.Attacker(self.values['weapon']) # want unique instance
    object = super().create(x, y)

    # set health
    if 'health' in self.values: object.attacker.set_health(self.values['health'])

    # set AI type
    object.AI = self.ai_class(object)
    object.AI.dist_threshold = 5.5
    # object.AI = AI.Basic(object)


    # callbacks
    getattr(object, 'callbacks')['attack'] = object.attacker.attack

    # setup
    object.setSpriteStatus(visible=True, has_sprite=True)
    return object

class Archer2Factory(ArcherFactory):
  def __init__(self):
    super().__init__()
    self.values['objectType'] = 'Archer2' # for drawing purposes
class Archer3Factory(ArcherFactory):
  def __init__(self):
    super().__init__()
    self.values['objectType'] = 'Archer3' # for drawing purposes
class Archer4Factory(ArcherFactory):
  def __init__(self):
    super().__init__()
    self.values['objectType'] = 'Archer4' # for drawing purposes

class BallOnChainGuyFactory(ArcherFactory):
  def __init__(self):
    super().__init__()
    self.values['objectType'] = 'Soldier' # for drawing purposes
    self.values['weapon'] = weapons.ballOnChain2FCT
    self.values['health'] = 100.0
    self.values['max_velocity'] = 1.0
    self.values['armor'] = ["projectile"]

class Boss1(MegaSoldierFactory):
  def __init__(self):
    super().__init__()
    self.values['weapon'] = weapons.ballOnChainFCT
    self.values['health'] = 300.0
    self.values['max_velocity'] = 1.0
    self.values['armor'] = ["projectile"]
    self.ai_class = AI.Boss1Meta

  
  def create(self, x, y):
    self.values['attacker'] = attack.Attacker(self.values['weapon']) # want unique instance
    object = super(SoldierFactory, self).create(x, y)

    # set health
    if 'health' in self.values: object.attacker.set_health(self.values['health'])
    
    # give an inventory
    object.inventory = inventory.Inventory(object)
    object.inventory.add_item(inventory.Boss1Weapon1())
    object.inventory.add_item(inventory.Boss1Weapon2())

    # set AI type
    object.AI = self.ai_class(object)
    # object.AI = AI.Basic(object)

    # callbacks
    getattr(object, 'callbacks')['attack'] = object.attacker.attack

    # setup
    object.setSpriteStatus(visible=True, has_sprite=True)
    return object