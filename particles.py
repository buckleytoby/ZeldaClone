from config       import *
from utils        import *
import gameObjects
import threading
import factory


class ParticleObj(gameObjects.GameObject):
    """ generic particle object
    """
    PARAMS = ["parent_id", "rect", "duration"]
    def __init__(self, **kwargs):
        # particle specific params
        self.parent_id = None
        self.duration = None
        self.dead = False
        self.die_on_impact = False # against tiles or go's

        # internal usage
        self.t0 = 0.0
        self.update_rate = 0.1
        self._started = False
        self._done = False

        kwargs["moveable"] = False
        super().__init__(**kwargs)
        #
    
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
            # BUG: is update getting called for this obj in physics too? idk...
            # self.update(dt) # in parent game obj

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