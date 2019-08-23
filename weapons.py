
from config       import *
from utils        import *
import factory
import AI


        
class SoldierWeapon1FCT(factory.DamageObjFactory):
    """ factory for creating damage object for soldier-weapon-1
    Requires soldier position, heading, power
    """
    def __init__(self, **kwargs):
        self.w = 0.85 # width of hitbox
        self.h = 0.85 # height of hitbox
        self.ox = 0.75 # offset of hitbox (to center)
        self.oy = 0.0 # offset of hitbox (to center)
        self.duration = 0.3
        self.power = 21.0
        self.name = "SoldierWeapon1"

        super().__init__()
        self.__dict__.update(kwargs)

    def make(self, go):
        """ make the object. Origin of rect is in center 
        ltf = local transform (i.e. from the parent to the child)
        """
        # required attributes
        parent_tf = go.get_center_tf()
        heading = get_heading(parent_tf)

        # calc transform
        child_ltf = m2d.Transform(heading, [self.ox, self.oy])
        center_tf = parent_tf * child_ltf
        center = center_tf.pos.array
        size = [self.w, self.h]
        xxyy = center_to_limits((center , size))

        rect = PatchExt(xxyy)

        # make the object -- this includes sending a reference to the go-list
        made = self.create(
            rect=rect, 
            parent_id=go.id, 
            duration=self.duration, 
            objectType=self.name,
            power=self.power)

        # DEBUG
        made.setSpriteStatus(visible=True)
        # pdb.set_trace()
        return made

soldierWeapon1FCT = SoldierWeapon1FCT()
playerWeapon1FCT = SoldierWeapon1FCT(
                    name="PlayerWeapon1",
                    power=51.0,
                    ox = 1.0
                    )