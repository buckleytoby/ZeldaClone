from config       import *
from utils        import *
import utils
import factory
import attack
import weapons
import AI
import inventory
import gameObjects


# defaultAI = AI.DmgAvoiderAttacker
defaultAI = AI.Basic 
  
class ItemFactory(factory.GameObjectFactory):
  def __init__(self):
    super().__init__()
    self.values['type'] = "item"
    self.values['moveable'] = False
    self.ai_class = defaultAI
    self.item = inventory.Item

  def item_maker(self, item_object, go):
      # fcn to make the item
      pass
  
  def create(self, x, y):
    object = super().create(x, y)

    # set the item maker
    object.item_maker = self.item_maker

    # set AI type
    object.AI = self.ai_class(object)
    # object.AI = AI.Basic(object)

    # setup
    object.setSpriteStatus(visible=True, has_sprite=True)
    return object

class PotionFactory(ItemFactory):
  def __init__(self):
    super().__init__()
    self.values['objectType'] = 'Potion'
    self.values['width']      = 1.0
    self.values['height']     = 1.0
    self.values['artWidth']      = 1.0
    self.values['artHeight']     = 1.0
    self.values['pixelWidth'] = 16 # size of the sprite image, depends on image size, shouldn't change
    self.values['pixelHeight'] = 16 # size of the sprite image, depends on image size, shouldn't change

  def item_maker(self, item_object, go):
      # item depends on which game object picks it up
      return inventory.Potion(50.0)

class KeyFactory(ItemFactory):
  def __init__(self):
    super().__init__()
    self.values['objectType'] = 'GoldKey'
    self.values['width']      = 1.0
    self.values['height']     = 1.0
    self.values['artWidth']      = 1.0
    self.values['artHeight']     = 1.0
    self.values['pixelWidth'] = 16 # size of the sprite image, depends on image size, shouldn't change
    self.values['pixelHeight'] = 16 # size of the sprite image, depends on image size, shouldn't change

  def item_maker(self, item_object, go):
      # connect key to door
      return inventory.GoldKey(item_object.door_id)

class Gate(gameObjects.GameObject):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.collide_cooldown = utils.Cooldown(5.0, self.print_fcn)
    self.door_id = -1

  def collide_callback(self, other):
    # check if other has key
    if hasattr(other, "inventory") and other.inventory.has_item("GoldKey") and other.inventory.items["GoldKey"].door_id == self.door_id:
      other.inventory.use_item("GoldKey")
    else:
      # if not, print message
      self.collide_cooldown.start()

  def print_fcn(self, **kwargs):
    print("Gate requires a key.")
    return True

class GateFactory(ItemFactory):
  def __init__(self):
    super().__init__()
    self.creator = Gate
    self.values['type'] = "game_object"
    self.values['objectType'] = 'Gate'
    self.values['width']      = 1.0
    self.values['height']     = 1.0
    self.values['artWidth']      = 1.0
    self.values['artHeight']     = 1.0
    self.values['pixelWidth'] = 16 # size of the sprite image, depends on image size, shouldn't change
    self.values['pixelHeight'] = 16 # size of the sprite image, depends on image size, shouldn't change
    
    self.values['moveable'] = False # if the object can be moved
    self.values['collideable'] = True # if the object can be collided with
    self.values['mass'] = 500.0


potionFactory = PotionFactory()
goldKeyFactory = KeyFactory()
gateFactory = GateFactory()