
from config       import *
from utils        import *
import factory
import AI
import attack

weapons_list = []
        
class SoldierWeapon1FCT(factory.DamageObjFactory):
    """ factory for creating damage object for soldier-weapon-1
    Requires soldier position, heading, power
    """
    def __init__(self, **kwargs):
        self.name = "SoldierWeapon1"
        self.w = 0.85 # width of hitbox
        self.h = 0.85 # height of hitbox
        self.ox = 0.75 # offset of hitbox (to center)
        self.oy = 0.0 # offset of hitbox (to center)
        self.duration = 0.2
        self.power = 21.0
        self.mass = 2000.0 # determines weapon blow-back
        self.cooldown = 0.6
        self.is_continuous = False

        super().__init__()
        self.__dict__.update(kwargs)

    def make_rect(self, go):
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

        return rect

    def make(self, go):
        """ make the object. Origin of rect is in center 
        ltf = local transform (i.e. from the parent to the child)
        """
        # make the object -- this includes sending a reference to the go-list
        made = self.create(
            rect = self.make_rect(go), 
            parent_id = go.id,
            team_id = go.team_id,
            duration = self.duration,
            objectType = self.name,
            power = self.power,
            mass = self.mass)

        # DEBUG
        made.setSpriteStatus(visible=True)
        # pdb.set_trace()
        return made

soldierWeapon1FCT = SoldierWeapon1FCT()
playerWeapon1FCT = SoldierWeapon1FCT(
                    name="PlayerWeapon1",
                    power=34.0,
                    ox = 1.0,
                    h = 1.5,
                    )

weapons_list.append( soldierWeapon1FCT )
weapons_list.append( playerWeapon1FCT )

class StraightLine(AI.Basic):
    # def __init__(self, *args):
    #     super().__init__(*args)


    def get_action(self):
        """ get direction from heading and project velocity in that direction
        """
        direction = self.parent.get_heading_unit_direction()
        dv = self.parent.max_velocity * direction
        out = {'dv': dv}
        cbs = []
        return out, cbs


class StraightProjectile(attack.DamageObj):

    def __init__(self, **kwargs):
        """
        Must over-write AI, and set a constant heading
        """
        assert( "heading" in kwargs )
        super().__init__(**kwargs)
        self.AI = StraightLine(self)

class Arrow1FCT(SoldierWeapon1FCT):
    def __init__(self, **kwargs):
        super().__init__()

        self.name = "Arrow1"
        self.w = 0.5 # width of hitbox
        self.h = 0.5 # height of hitbox
        self.ox = 0.75 # offset of hitbox (to center)
        self.oy = 0.0 # offset of hitbox (to center)
        self.duration = 1.0
        self.power = 34.0
        self.mass = 2000.0 # determines weapon blow-back
        self.max_velocity = 5.0
        self.cooldown = 0.1
        self.is_continuous = True

        self.__dict__.update(kwargs)

        # reset creator
        self.creator = StraightProjectile

    def make(self, go):
        """ make the object. Origin of rect is in center 
        ltf = local transform (i.e. from the parent to the child)
        """
        # make the object -- this includes sending a reference to the go-list
        made = self.create(
            rect = self.make_rect(go), 
            parent_id = go.id,
            team_id = go.team_id,
            duration = self.duration,
            objectType = self.name,
            power = self.power,
            mass = self.mass,
            heading = go.heading,
            max_velocity = self.max_velocity)

        # DEBUG
        made.setSpriteStatus(visible=True)
        # pdb.set_trace()
        return made

arrow1FCT = Arrow1FCT()
arrow2FCT = Arrow1FCT(name="Arrow2",
                      max_velocity = 15.0,
                      )
arrow3FCT = Arrow1FCT(name="Arrow3",
                      cooldown = 1.0,
                      w = 1.5, # width of hitbox
                      h = 1.5 # height of hitbox
                      )
arrow4FCT = Arrow1FCT(name="Arrow4",
                      cooldown = 0.25,
                      w = 1.5, # width of hitbox
                      h = 1.5 # height of hitbox
                      )
arrow5FCT = Arrow1FCT(name="Arrow5",
                      cooldown = 1.0,
                      w = 0.5, # width of hitbox
                      h = 0.5 # height of hitbox
                      )

weapons_list.append( arrow1FCT )
weapons_list.append( arrow2FCT )
weapons_list.append( arrow3FCT )
weapons_list.append( arrow4FCT )
weapons_list.append( arrow5FCT )