from config       import *
from utils        import *
import weapons
from collections import defaultdict

class Item():
    def __init__(self, use):
        # @param use: fcn reference
        self.use = use
        self.count = 1

class Ability():
    # same as an Item but 
    def __init__(self, use):
        # @param use: fcn reference
        self.use = use
        self.count = 1

class Inventory():
    def __init__(self, parent):
        self.parent = parent
        self.items = {} # default item count: 0
        self.hotkeys = {}

    def add_item(self, item):
        print("Adding item: {}".format(item.name))
        if item.name in self.items:
            self.items[item.name].count += 1
        else:
            self.items[item.name] = item
    
    def use_item(self, name):
        if name in self.items:
            item = self.items[name]
            if item.count > 0:
                item.use(self.parent)
                item.count -= 1

    def set_hotkey(self, key, name):
        self.hotkeys[key] = name

    def has_item(self, name):
        if name not in self.items or self.items[name].count < 1:
            return False
        else:
            return True


class Potion(Item):
    # potion
    def __init__(self, amount):
        # @param parent: gameObject who carries this item
        # @param amount: amount to heal parent by
        super().__init__(self.use_fcn)
        self.amount = amount
        self.name = "Potion"

    def use_fcn(self, parent):
        # increase parent's health by amount, but no more than max health
        val = np.min([parent.attacker.health + self.amount, parent.attacker.max_health])
        parent.attacker.health = val

        print(parent.objectType+" used potion")

        # play sound
        pass

class GoldKey(Item):
    # potion
    def __init__(self, door_id):
        # @param parent: gameObject who carries this item
        # @param amount: amount to heal parent by
        super().__init__(self.use_fcn)
        self.door_id = door_id
        self.name = "GoldKey"

    def use_fcn(self, parent):
        print(parent.objectType+" used {}".format(self.name))
        # find doors within reach
        rect = parent.reach_rect.convert_to_pygame_rect()
        gos = get_game_objects()
        go_tree = DATA["game_object_tree"]
        hits = go_tree.hit(rect)
        gos = {go.id: go for go in hits}
        
        for id in gos:
            go = gos[id]
            if not hasattr(go, "door_id"):
                continue

            # if id matches, unlock the door by destroying the GO
            if self.door_id == go.door_id:
                MESSAGES.put(make_del_msg(go))

class Boss1Weapon1(Item):
    def __init__(self):
        super().__init__(self.use_fcn)
        self.name = "Boss1Weapon1"

    def use_fcn(self, parent):
        parent.attacker.change_weapon(weapons.ballOnChainFCT)

class Boss1Weapon2(Item):
    def __init__(self):
        super().__init__(self.use_fcn)
        self.name = "Boss1Weapon2"

    def use_fcn(self, parent):
        parent.attacker.change_weapon(weapons.spreadShotBoss1Phase3)