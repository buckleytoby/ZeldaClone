from config       import *
from utils        import *
import factory
import attack
import weapons
import AI
import inventory


# defaultAI = AI.DmgAvoiderAttacker
defaultAI = AI.Basic 
  
class ItemFactory(factory.GameObjectFactory):
  def __init__(self):
    super().__init__()
    self.values['type'] = "item"
    self.values['moveable'] = False
    self.ai_class = defaultAI
    self.item = inventory.Item

  def item_maker(self):
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

  def item_maker(self, go):
      # item depends on which game object picks it up
      return inventory.Potion(50.0)

potionFactory = PotionFactory()