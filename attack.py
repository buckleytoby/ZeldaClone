
from config       import *
import utils
from utils        import *
import gameObjects
import threading


class DamageObj(gameObjects.GameObject):
    """ generic damage object
    """
    PARAMS = ["parent_id", "rect", "duration"]
    def __init__(self, **kwargs):
        # dmg-obj specific params
        self.parent_id = None
        self.duration = None
        self.power = 0.0
        self.dead = False
        self.die_on_impact = True # against tiles or go's
        self.dmg_type = "pure"

        # internal usage
        self.t0 = 0.0
        self.update_rate = 0.1
        self._started = False
        self._done = False

        kwargs["moveable"] = False
        kwargs["type"] = "damage"
        super().__init__(**kwargs)

        #
        self.start()
    
    def start(self):
        self._started = True

        # spin up thread
        thread = Thread(target = self.thread, daemon = True)
        thread.start()

        # add self to game-objects
        tup = make_gen_msg(self)
        MESSAGES.put(tup)

    def set_done(self):
        self._done = True

    def thread(self):
        """ independent countdown thread """

        t0 = get_game_time()
        tt = t0
        while not self._done:
            dt = get_game_time() - tt
            self.update(dt) # in parent game obj

            # sleep
            time.sleep(self.update_rate)

            # exit condition
            tt = get_game_time()
            if (tt - t0) > self.duration:
                # print("dt: {}".format(tt-t0))
                self.set_done()

        # self-destruct
        self.die()

    def die(self):
        if not self.dead:
            self.dead = True
            """ add self to the del list """
            tup = make_del_msg(self)
            # print(tup[1].id)
            MESSAGES.put(tup)

class Attacker(object):
    """ Attack Module Class. Held by game-object """
    def __init__(self, weapon):
        # weapon factory
        self.change_weapon(weapon)
        self.health = 50.0
        self.max_health = self.health
        self.mana = 100.0
        self.max_mana = self.mana
        self.mana_regen = 0.0
        self.disabled = False # whether can attack
        self.invincible = False # whether can get hit
        self.invincible_cooldown = 0.5

    def set_health(self, health):
        self.health = health
        self.max_health = self.health

    def change_weapon(self, weapon):
        self.weapon = weapon
        self.attack_cooldown = self.weapon.cooldown

    def attack(self, **kwargs):
        if not self.disabled:
            obj = self.weapon.make(**kwargs) # returns the made object if succesful, otherwise None
            if obj:
                self.attack_cooldowner()

    def attack_cooldowner(self):
        """ spool up a thread """
        self.disabled = True
        self.attack_cooldown_timer = daemon_timer(self.attack_cooldown, self.reset_disabled)
        # BUG?: this is real time and not pygame time

    def invincible_cooldowner(self):
        """ spool up a thread """
        self.invincible = True
        daemon_timer(self.invincible_cooldown, self.reset_invincible)

    def reset_invincible(self):
        self.invincible = False

    def reset_disabled(self):
        self.disabled = False

    def spawn_objects(self, go, spawn_name):
        if hasattr(go, spawn_name):
            factories = get_factories()
            for name in getattr(go, spawn_name):
                obj = factories[name].create(go.x, go.y)

    def receive_damage(self, go, do):
        """ return True if damage was received """
        if not self.invincible:
            # check armor against projectiles
            if not (hasattr(go, "armor") and do.dmg_type in go.armor):

                self.health -= do.power
                print("Hit {} with {} health left".format(go.objectType, self.health))
                self.spawn_objects(go, "damage_objects")

                # die, if applicable
                if self.health < 0.0:
                    die(go)

                    # make go invisible so it's not drawn on the next frame
                    go.visible = False

                    self.spawn_objects(go, "death_objects")

                # trigger invincibility frames
                self.invincible_cooldowner()

                # generate effects

                return True

        return False