
import utils
from config       import *
import attack
import math_utils

class Physics(object):
  #physics object for the map
  # 
  # input a handle to static objects and moving mobs
  # each object must contain x, y, width, height, and mass attributes
  #
  def __init__(self, player):
    self.playerClass = player
    self.force = 50 #N
    self.gravity = 9.81 # m/s^2
    self.gameObjects = None
    self.gameObjectsARR = None
    self.portal_tree = None
    self.portals = None
    self.portals_rects = []
    self.previous_active_gos = None
    self.go_tree = None

  def set_portals(self, portals):
    # gen pygame rects
    self.portals = portals
    self.portals_rects = [portal.rect for portal in self.portals]
    [portal.update_rect() for portal in self.portals]
    # self.portal_tree = utils.QuadTree(portals)

  def check_portals(self, gameObject):
    if self.portal_tree: # protect against None
      # hits = self.portal_tree.hit(gameObject.pygame_rect)
      hit_idx = gameObject.rect.collidelist(self.portals_rects)
      if hit_idx >= 0:
        self.portals[hit_idx].activate(gameObject, self.portals) # teleport!

  def get_gos_from_quadtree(self, tree, pygame_rect):
    # get rect for the active screen, expanded by a bit
    hits = self.go_tree.hit(pygame_rect)
    active_gos = {go.id: go for go in hits}
    return active_gos

  def make_go_quadtree(self, game_objects):
    # collect all rects
    go_list = [game_objects[key] for key in game_objects]

    # calc all pygame rects -- needed for now because quadtree uses pygame rects
    [game_objects[key].update_rect() for key in game_objects]

    # use a quadtree
    go_tree = utils.QuadTree(go_list, depth=10)
    return go_tree

  # @profile
  def get_active_game_objects(self, gameObjects, new_game_objects):
    # update quadtree only with gos that may have moved last frame
    if self.previous_active_gos:
      [self.previous_active_gos[key].update_rect() for key in self.previous_active_gos]
      self.go_tree.update(self.previous_active_gos)
    else:
      self.go_tree = self.make_go_quadtree(gameObjects)
      
    if len(new_game_objects) > 0:
      [new_game_objects[key].update_rect() for key in new_game_objects]
      self.go_tree.add(new_game_objects)
      new_game_objects.clear()

    # update DATA
    DATA["game_object_tree"] = self.go_tree

    # get rect for the active screen, expanded by a bit
    screen = self.playerClass.screenClass.get_footprint_rect().scale(0.15)
    active_gos = self.get_gos_from_quadtree(self.go_tree, screen)
    self.previous_active_gos = active_gos
    return active_gos

  # def get_active_game_objects2(self, gameObjects):
  #   # lazy and poor man's "on-screen" check ... need to replace this with a proper quadtree (at-least do 16-tile chunks)
  #   out = {}
  #   player_xy = DATA["player_xy"]
  #   for key in gameObjects:
  #     gameObject = gameObjects[key]
  #     # if gameObject.objectType == 'Player':
  #     if math_utils.eucl_dist(player_xy, gameObject.position) < 20:
  #       out[key] = gameObject
  #   return out

  def passive_update(self, dt, game_objects):
    # mana
    for id in game_objects:
      go = game_objects[id]
      if hasattr(go, "attacker"):
        if go.attacker.mana_regen > 0.0 and go.attacker.mana < go.attacker.max_mana:
          val = np.min([go.attacker.mana + go.attacker.mana_regen * dt, go.attacker.max_mana])
          go.attacker.mana = val

      
  # @profile
  def update(self, timeElapsed, all_game_objects, new_game_objects, worldClass, mapType):
    """ 
    Step 1: everybody moves
    Step 2: resolve all collisions
    Step 3: static-object collision prevention
    """
    dt = timeElapsed
    
    vel_dict = {}

    # get only game objects that are on screen
    gameObjects = self.get_active_game_objects(all_game_objects, new_game_objects)
    if not gameObjects:
      return

    # passive update
    self.passive_update(timeElapsed, gameObjects)

    # first, update each game-objects location
    for key in gameObjects:
      gameObject = gameObjects[key]



      #gameObject.update(timeElapsed)
      action, cbs = gameObject.AI.get_action(timeElapsed)
      vel_dict[gameObject.id] = np.zeros(2) #action['dv']
      dx, dy = action['dv']

      # add on pre-existing momentum, deteriorated by friction
      dv = 5. * gameObject.velocity # simplified this equation: ( gameObject.momentum / gameObject.mass) * gameObject.unit_velocity

      dx += dv[0]
      dy += dv[1]

      gameObject.dx = dx; gameObject.dy = dy

      gameObject.x += dt * dx
      gameObject.y += dt * dy

      # call cbs
      for cb in cbs:
        if cb in gameObject.callbacks:
          gameObject.callbacks[cb](go=gameObject)

    # second, resolve all collisions with gameObjects
    vel_residual = self.collision_resolution(vel_dict, timeElapsed, gameObjects)
    # vel_residual2 = self.collision_resolution2(vel_dict, timeElapsed, gameObjects)

    # third, add residual delta
    for key in gameObjects:
      gameObject = gameObjects[key]

      dx, dy = vel_residual[gameObject.id]

      gameObject.x += dt * dx
      gameObject.y += dt * dy

      # must be last: check collision against static objects
      indices = gameObject.get_overlap_tiles()
      for ij in indices:
        if worldClass.can_tile_collide(mapType, ij):
          i, j = ij
          rect = worldClass.maps[mapType].get_rect(i, j)
          
          dx = gameObject.dx
          dy = gameObject.dy

          # pdb.set_trace()
          
          if gameObject.moveable and gameObject.collide(rect):
            if isinstance(gameObject, attack.DamageObj) and gameObject.die_on_impact:
              gameObject.die()
            # pdb.set_trace()
            # see which direction is less distance to move
            
            # got pushed
            xf1 = rect.left - gameObject.width
            xf2 = rect.right
            yf1 = rect.top - gameObject.height
            yf2 = rect.bottom
            dist1 = np.abs(gameObject.x - xf1)
            dist2 = np.abs(gameObject.x - xf2)
            dist3 = np.abs(gameObject.y - yf1)
            dist4 = np.abs(gameObject.y - yf2)
            argmin = np.argmin([dist1, dist2, dist3, dist4])
            if argmin == 0: gameObject.x = xf1
            if argmin == 1: gameObject.x = xf2
            if argmin == 2: gameObject.y = yf1
            if argmin == 3: gameObject.y = yf2

      # real update
      gameObject.update(timeElapsed)

      # portals
      # TODO: make check_portals only check GOs on screen?
      # self.check_portals(gameObject)

      # update gameObject in the quadtree
      # TODO

  def momentum_trade(self, go1, go2):
    """ momentum (represented as delta-v) imparted ON go2 BY go1
    """

    # force field away from center-of-mass, scaled by receiving object's mass & friction
    dv2 = go1.com_vector(go2) * go1.mass / go2.mass * (1.0 - go2.friction)

    # TODO: calculate required dv to align rect edges

    # calculate momentum and rebound, scaled by friction
    dv2 += go1.momentum * go1.unit_velocity / go2.mass * go2.friction # array
    
    return dv2

  
  def collision_resolution(self, vel_dict, timeElapsed, gameObjects):
    """ take a potentially collision-filled map and resolve collisions
    such that no active object is in-collision """
    # try updating first
    [gameObjects[key].update_rect() for key in gameObjects]
    self.go_tree.update(gameObjects)
    
    for key in gameObjects:
      # compute the resolution for go1 by summing up the impacts of all GO's it interacts with
      go1 = gameObjects[key]
      if not go1.collideable:
        continue
      dv1 = 0.0
      other_gos = self.get_gos_from_quadtree(self.go_tree, go1.rect)
      for key2 in other_gos:
        go2 = other_gos[key2]
        # sanity check
        if go1.id == go2.id:
          continue
        if go2.collideable: # don't need to check go1.collide(go2) because we already know that from the quadtree search
          # resolve if damage-object
          if isinstance(go2, attack.DamageObj):
            dv1 += self.damage(do=go2, go=go1)
          # resolve if game-objects are moveable
          if go1.moveable and go2.can_transfer_momentum:
            dv1 += self.momentum_trade(go2, go1)
          # add to vel arr
      vel_dict[go1.id] += dv1
    return vel_dict

  def collision_resolution2(self, vel_dict, timeElapsed, gameObjects):
    """ take a potentially collision-filled map and resolve collisions
    such that no active object is in-collision

    resolution components felt by obj 1:
    2's push on 1
    #1's friction resistance to 2's push on 1
    """
    # matrix of deltas
    num_objs = len(gameObjects)
    
    # upper triangular indices, starting 1 right from main diagonal, ensures no repeats
    # TODO: this is awful, because it cross checks EVERY single object on screen, which could be many many objects if using particles or w/e. So use the previously computed quadtree instead!
    i1, i2 = np.triu_indices(num_objs, 1)
    keys = gameObjects.keys()

    for c1, c2 in zip(i1, i2):
      go1 = gameObjects[list(keys)[c1]]
      go2 = gameObjects[list(keys)[c2]]

      # sanity check
      if go1.id == go2.id:
        continue

      if go1.collideable and go2.collideable and go1.collide(go2):
        dv1 = 0.0
        dv2 = 0.0

        # resolve if damage-object
        if isinstance(go1, attack.DamageObj):
          # go1 is imparting damage on go2, therefore go2 receives delta-v
          dv2 += self.damage(do=go1, go=go2)
        if isinstance(go2, attack.DamageObj):
          dv1 += self.damage(do=go2, go=go1)

        # resolve if game-objects are moveable
        if go1.moveable and go2.can_transfer_momentum:
          dv1 += self.momentum_trade(go2, go1)
        if go2.moveable and go1.can_transfer_momentum:
          dv2 += self.momentum_trade(go1, go2)

        # add to vel arr
        vel_dict[go1.id] += dv1
        vel_dict[go2.id] += dv2
    
    return vel_dict

  def damage(self, do=None, go=None):
    """ apply damage to game object
    do: damage-object
    go: game-object to take damage
    """
    dv = 0.0

    # friendly-fire off
    if not do.team_id == go.team_id:
      # remove damage object
      if do.die_on_impact: do.die()

      # confirm go can take damage
      if hasattr(go, "attacker"):
        hit = go.attacker.receive_damage(go, do)

        # blowback
        if hit:
          dv = self.momentum_trade(do, go)
          # print("dv: {}".format(dv))

          # sound fx
          if hasattr(go, "hitSoundFX"):
            tup = utils.make_sound_msg(go.hitSoundFX)
            MESSAGES.put(tup)

    return dv

