
from config       import *
from utils        import *
import attack
import gameObjects
import particles


class Factory(object):
  # generic factory class
  def __init__(self, creator):
    self.creator = creator
    self.values = {}
    
  def create(self, **kwargs):
    self.values.update(kwargs)
    created = self.creator(**self.values)
    return created

class Factory2(object):
  # generic factory class
  def __init__(self, creator):
    self.creator = creator
    self.values = {}
    
  def create(self):
    created = self.creator()
    # set the values
    for key in self.values:
      try:
        setattr(created, key, self.values[key]) #equivalent to self.{key} = value
      except:
        pdb.set_trace()
    
    return created


class GameObjectFactory(Factory):
  # factory class for creating game objects
  def __init__(self):
    super().__init__(gameObjects.GameObject) #check syntax
    
  def create(self, x, y):
    kwargs = {}
    kwargs["x"] = x
    kwargs['y'] = y
    kwargs['old_x'] = x
    kwargs['old_y'] = y
    created = super().create(**kwargs)
    return created

class DamageObjFactory(Factory):
  # factory class for creating damage objects
    def __init__(self):
        super().__init__(attack.DamageObj) #check syntax

class ParticleObjFactory(Factory):
  # factory class for creating damage objects
    def __init__(self):
        super().__init__(particles.ParticleObj) #check syntax
    
    def create(self, x, y):
        kwargs = {}
        kwargs["x"] = x
        kwargs['y'] = y
        kwargs['old_x'] = x
        kwargs['old_y'] = y
        created = super().create(**kwargs)
        return created



class GhostParticleFactory(ParticleObjFactory):
  def __init__(self):
    super().__init__()
    self.values['objectType'] = 'Ghost1' # for drawing purposes
    self.values['update_rate'] = 0.25
    self.values['duration'] = 7.0 * self.values['update_rate'] + 0.1
    self.values['width']      = 1.0
    self.values['height']     = 1.0
    self.values['artWidth']      = 1.0
    self.values['artHeight']     = 1.0
    self.values['pixelWidth'] = 16 # size of the sprite image, depends on image size, shouldn't change
    self.values['pixelHeight'] = 16 # size of the sprite image, depends on image size, shouldn't change

    
  def create(self, x, y):
    object = super().create(x, y)
    # setup
    object.setSpriteStatus(visible=True, has_sprite=True)
    object.animation.update_rate = self.values['update_rate']
    return object

class BloodParticleFactory(GhostParticleFactory):
  def __init__(self):
    super().__init__()
    self.values['objectType'] = 'Blood1' # for drawing purposes
    self.values['update_rate'] = 0.15
    self.values['duration'] = 6.0 * self.values['update_rate'] + 0.1
    self.values['width']      = 1.0
    self.values['height']     = 1.0
    self.values['artWidth']      = 1.0
    self.values['artHeight']     = 1.0
    self.values['pixelWidth'] = 16 # size of the sprite image, depends on image size, shouldn't change
    self.values['pixelHeight'] = 16 # size of the sprite image, depends on image size, shouldn't change
