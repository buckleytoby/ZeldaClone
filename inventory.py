from config       import *
from utils        import *
from collections import defaultdict

class Item():
    def __init__(self, use):
        # @param use: fcn reference
        self.use = use
        self.count = 0

class Inventory():
    def __init__(self):
        self.items = defaultdict(int) # default item count: 0
        self.hotkeys = {}

    def add_item(self, name):
        self.items[name] += 1
    
    def use_item(self, name):
        item = self.items[name]
        if item.count > 0:
            item.use()
            item.count -= 1

    def set_hotkey(self, key, name):
        self.hotkeys[key] = name