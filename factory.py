
from config       import *
from utils        import *
import attack
import gameObjects


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