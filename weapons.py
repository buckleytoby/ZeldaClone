
from config       import *
from utils        import *
import math_utils
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
        self.art_name = self.name
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
        
        # set values
        self.values['can_transfer_momentum'] = False
        self.values['artWidth']      = self.w
        self.values['artHeight']     = self.h
        self.values['pixelWidth'] = 16 # size of the sprite image, depends on image size, shouldn't change
        self.values['pixelHeight'] = 24 # size of the sprite image, depends on image size, shouldn't change
        

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
            objectType = self.art_name,
            power = self.power,
            mass = self.mass,
            die_on_impact = False,
            )

        # DEBUG
        made.setSpriteStatus(visible=True, has_sprite=False)
        # pdb.set_trace()
        return made

soldierWeapon1FCT = SoldierWeapon1FCT()
playerWeapon1FCT = SoldierWeapon1FCT(
                    name="PlayerWeapon1",
                    power=34.0,
                    ox = 1.0,
                    h = 1.5,
                    w = 1.5,
                    )

weapons_list.append( soldierWeapon1FCT )
weapons_list.append( playerWeapon1FCT )

class StraightLine(AI.Basic):
    # def __init__(self, *args):
    #     super().__init__(*args)


    def get_action(self, elapsed_time):
        """ get direction from heading and project velocity in that direction
        """
        direction = self.parent.get_heading_unit_direction()
        dv = self.parent.max_velocity * direction
        out = {'dv': dv}
        cbs = []
        return out, cbs


class StraightProjectile(attack.DamageObj): # this is also a game object (inheritance)

    def __init__(self, **kwargs):
        """
        Must over-write AI, and set a constant heading
        """
        assert( "heading" in kwargs )
        kwargs["dmg_type"] = "projectile"
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
        self.mana_cost = 0.0
        self.is_continuous = True
        self.soundFX = "pew1"

        self.__dict__.update(kwargs)
        
        # set values
        self.values['artWidth']      = self.w
        self.values['artHeight']     = self.h
        self.values['pixelWidth'] = 16 # size of the sprite image, depends on image size, shouldn't change
        self.values['pixelHeight'] = 16 # size of the sprite image, depends on image size, shouldn't change
        
        # reset creator
        self.creator = StraightProjectile

    def make(self, go):
        """ make the object. Origin of rect is in center 
        ltf = local transform (i.e. from the parent to the child)
        """
        # check mana
        if self.mana_cost > 0 and go.attacker.mana >= self.mana_cost:
            go.attacker.mana -= self.mana_cost

            # make the object -- this includes sending a reference to the go-list
            made = self.create(
                rect = self.make_rect(go), 
                parent_id = go.id,
                team_id = go.team_id,
                duration = self.duration,
                objectType = self.name,
                power = self.power,
                mass = self.mass,
                heading = go.projectile_heading,
                max_velocity = self.max_velocity)

            # DEBUG
            made.setSpriteStatus(visible=True, has_sprite=True)

            # sound fx
            tup = make_sound_msg(self.soundFX)
            MESSAGES.put(tup)

            # pdb.set_trace()
            return made
        else:
            return None

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
                      h = 1.5, # height of hitbox
                      mana_cost = 20.0,
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

class SpreadShot(Arrow1FCT):
    # multi-directional spread shot, centered on target
    def __init__(self, **kwargs):
        super().__init__()
        self.name = "SpreadShot"

        self.nb_projectiles = 3
        self.spread_angle = np.deg2rad(90.0)

        self.__dict__.update(kwargs)
        assert(self.nb_projectiles > 1)

    def make(self, go):
        """ make the object. Origin of rect is in center 
        ltf = local transform (i.e. from the parent to the child)
        """
        # check mana
        if self.mana_cost <= 0 or go.attacker.mana >= self.mana_cost:
            go.attacker.mana -= self.mana_cost

            heading = go.projectile_heading
            for i in range(self.nb_projectiles):
                angle = heading + self.spread_angle * ( -0.5 + float(i) / (self.nb_projectiles - 1))


                # make the object -- this includes sending a reference to the go-list
                made = self.create(
                    rect = self.make_rect(go), 
                    parent_id = go.id,
                    team_id = go.team_id,
                    duration = self.duration,
                    objectType = self.name,
                    power = self.power,
                    mass = self.mass,
                    heading = angle,
                    max_velocity = self.max_velocity)

                # DEBUG
                made.setSpriteStatus(visible=True, has_sprite=True)

            # sound fx
            tup = make_sound_msg(self.soundFX)
            MESSAGES.put(tup)

            # pdb.set_trace()
            return made
        else:
            return None

spreadShot = SpreadShot()
spreadShotBoss1Phase3 = SpreadShot(name = "SpreadShotBoss1Phase3",
                                   nb_projectiles = 12,
                                   spread_angle = np.deg2rad(360.0),
                                    )

weapons_list.append(spreadShot)
weapons_list.append(spreadShotBoss1Phase3)



class BallOnChain(AI.Basic):
    # circular motion around caster

    def get_action(self, elapsed_time):
        """ get direction from heading and project velocity in that direction
        """
        pivot_pt = self.parent.go_position() # recall, the parent for the AI is the DamageObj
        pos = self.parent.get_center()
        orient = m2d.Orientation(np.pi / 2.0) # 90 deg turn
        vec = (orient * m2d.Vector(pos-pivot_pt)).array
        unit = math_utils.normalize(vec)
        
        dv = self.parent.max_velocity * unit
        out = {'dv': dv}
        cbs = []
        return out, cbs

class BallOnChainProjectile(attack.DamageObj): # this is a game object (inherited)

    def __init__(self, **kwargs):
        """
        Must over-write AI, and set a constant heading
        """
        super().__init__(**kwargs)
        self.AI = BallOnChain(self)

class BallOnChainFCT(Arrow1FCT):
    def __init__(self, **kwargs):
        super().__init__()

        self.name = "BallOnChain1"
        self.w = 1.0 # width of hitbox
        self.h = 1.0 # height of hitbox
        self.ox = 0.75 # offset of hitbox (to center)
        self.oy = 0.0 # offset of hitbox (to center)
        self.duration = 2.0
        self.power = 34.0
        self.mass = 2000.0 # determines weapon blow-back
        self.max_velocity = 10.0
        self.cooldown = 0.2
        self.is_continuous = True

        self.__dict__.update(kwargs)
        
        # set values
        self.values['artWidth']      = self.w
        self.values['artHeight']     = self.h
        self.values['pixelWidth'] = 16 # size of the sprite image, depends on image size, shouldn't change
        self.values['pixelHeight'] = 16 # size of the sprite image, depends on image size, shouldn't change

        # reset creator
        self.creator = BallOnChainProjectile

    def make(self, go):
        """ @param go: the game object which is calling this make fcn
        make the object. Origin of rect is in center 
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
            go_position = go.get_center,
            max_velocity = self.max_velocity)

        # DEBUG
        made.setSpriteStatus(visible=True, has_sprite=True)

        # sound fx
        tup = make_sound_msg(self.soundFX)
        MESSAGES.put(tup)

        # pdb.set_trace()
        return made


ballOnChainFCT = BallOnChainFCT()
weapons_list.append( ballOnChainFCT )

ballOnChain2FCT = BallOnChainFCT(name="BallOnChain2",
                      cooldown = 2.0,
                      )

weapons_list.append( ballOnChain2FCT )