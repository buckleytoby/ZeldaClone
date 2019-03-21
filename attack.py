
from config       import *
from utils        import *
from gameObjects  import *


class DamageObj(GameObject):
    """ generic damage object
    """
    def __init__(self, parent_id, rect, duration):
        self.parent_id = parent_id
        self.rect = rect.copy()
        self.duration = duration

        # 
        self.t0 = 0.0
    
    def start(self):


class DamageObjFactory(DamageObj):
    def __init__(self):
        super(PlayerFactory, self).__init__()
        self.values['max_velocity'] = 6.0 #m/s
        self.values['artWidth']      = 1.0
        self.values['artHeight']     = 1.5