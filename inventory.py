from config       import *
from utils        import *
from collections import defaultdict

class Item():
    def __init__(self, use):
        # @param use: fcn reference
        self.use = use
        self.count = 1

class Inventory():
    def __init__(self):
        self.items = {} # default item count: 0
        self.hotkeys = {}

    def add_item(self, item):
        print("Adding item: {}".format(item.name))
        if item.name in self.items:
            self.items[item.name].count += 1
        else:
            self.items[item.name] = item
    
    def use_item(self, name):
        item = self.items[name]
        if item.count > 0:
            item.use()
            item.count -= 1

    def set_hotkey(self, key, name):
        self.hotkeys[key] = name


class Potion(Item):
    # potion
    def __init__(self, parent, amount):
        # @param parent: gameObject who carries this item
        # @param amount: amount to heal parent by
        super().__init__(self.use_fcn)
        self.parent = parent
        self.amount = amount
        self.name = "Potion"

    def use_fcn(self):
        # increase parent's health by amount, but no more than max health
        val = np.min([self.parent.attacker.health + self.amount, self.parent.attacker.max_health])
        self.parent.attacker.health = val

        print(self.parent.objectType+" used potion")

        # play sound
        pass
