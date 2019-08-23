
from config       import *
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

        # internal usage
        self.t0 = 0.0
        self.update_rate = 0.1
        self._started = False
        self._done = False

        kwargs["moveable"] = False
        super().__init__(**kwargs)

        #
        self.start()
    
    def start(self):
        self._started = True

        # spin up thread
        thread = Thread(target = self.thread)
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
                self.set_done()

        # self-destruct
        self.die()

    def die(self):
        """ add self to the del list """
        tup = make_del_msg(self)
        # print(tup[1].id)
        MESSAGES.put(tup)

class Attacker(object):
    """ Attack Module Class. Held by game-object """
    def __init__(self, weapon):
        # weapon factory
        self.weapon = weapon
        self.health = 100.0
        self.disabled = False # whether can attack
        self.invincible = False # whether can get hit
        self.invincible_cooldown = 1.0
        self.attack_cooldown = 0.6

    def attack(self, **kwargs):
        if not self.disabled:
            self.weapon.make(**kwargs)
            self.attack_cooldowner()

    def attack_cooldowner(self):
        """ spool up a thread """
        self.disabled = True
        threading.Timer(self.attack_cooldown, self.reset_disabled).start()

    def invincible_cooldowner(self):
        """ spool up a thread """
        self.invincible = True
        threading.Timer(self.invincible_cooldown, self.reset_invincible).start()

    def reset_invincible(self):
        self.invincible = False

    def reset_disabled(self):
        self.disabled = False

    def receive_damage(self, go, power):
        if not self.invincible:
            self.health -= power
            print("Hit {} with {} health left".format(go.objectType, self.health))

            # die, if applicable
            if self.health < 0.0:
                die(go)

            # trigger invincibility frames
            self.invincible_cooldowner()

            # generate effects