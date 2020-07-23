
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
  def __init__(self):
    self.force = 50 #N
    self.gravity = 9.81 # m/s^2
    self.gameObjects = None
    self.gameObjectsARR = None

  def get_active_game_objects(self, gameObjects):
    # lazy and poor man's "on-screen" check
    out = {}
    for key in gameObjects:
      gameObject = gameObjects[key]
      if math_utils.eucl_dist(DATA["player_xy"], gameObject.center_of_mass) < 20:
        out[key] = gameObject
    return out
      
  def update(self, timeElapsed, all_game_objects, worldClass, mapType):
    """ 
    Step 1: everybody moves
    Step 2: resolve all collisions
    Step 3: static-object collision prevention
    """
    dt = timeElapsed
    
    vel_dict = {}

    # get only game objects that are on screen
    gameObjects = self.get_active_game_objects(all_game_objects)

    # first, update each game-objects location
    for key in gameObjects:
      gameObject = gameObjects[key]



      #gameObject.update(timeElapsed)
      action, cbs = gameObject.AI.get_action()
      vel_dict[gameObject.id] = np.zeros(2) #action['dv']
      dx, dy = action['dv']

      # add on pre-existing momentum, deteriorated by friction
      dv = 5. * ( gameObject.momentum / gameObject.mass) * gameObject.unit_velocity

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

    # third, add residual delta
    for key in gameObjects:
      gameObject = gameObjects[key]

      dx, dy = vel_residual[gameObject.id]

      gameObject.x += dt * dx
      gameObject.y += dt * dy

      # must be last: check collision against static objects
      indices = gameObject.get_overlap_tiles()
      for i, j in indices:
        if worldClass.can_tile_collide(mapType, [i, j]):
          rect = worldClass.maps[mapType].get_rect(i, j)
          
          dx = gameObject.dx
          dy = gameObject.dy

          # pdb.set_trace()
          
          if gameObject.intersect(rect):
            # pdb.set_trace()
            # see which direction is less distance to move
            
            if True: #np.abs(dx) < 1e-6 and np.abs(dy) < 1e-6:
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
            else:
              xf = 9999.0
              yf = 9999.0
              if dx > 0: # Moving right; Hit the left side of the wall
                xf = rect.left - gameObject.width
              elif dx < 0: # Moving left; Hit the right side of the wall
                xf = rect.right
              if dy > 0: # Moving down; Hit the top side of the wall
                yf = rect.top - gameObject.height
              elif dy < 0: # Moving up; Hit the bottom side of the wall
                yf = rect.bottom
              dist_x = np.abs(gameObject.x - xf)
              dist_y = np.abs(gameObject.y - yf)
              if dist_x < dist_y:
                gameObject.x = xf
              else:
                gameObject.y = yf

          # real update
      gameObject.update(timeElapsed)

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
    such that no active object is in-collision

    resolution components felt by obj 1:
    2's push on 1
    #1's friction resistance to 2's push on 1
    """
    # matrix of deltas
    num_objs = len(gameObjects)
    
    # upper triangular indices, starting 1 right from main diagonal, ensures no repeats
    i1, i2 = np.triu_indices(num_objs, 1)
    keys = gameObjects.keys()

    for c1, c2 in zip(i1, i2):
      go1 = gameObjects[list(keys)[c1]]
      go2 = gameObjects[list(keys)[c2]]

      # sanity check
      if go1.id == go2.id:
        continue

      if go1.intersect(go2):
        dv1 = 0.0
        dv2 = 0.0

        # resolve if damage-object
        if isinstance(go1, attack.DamageObj):
          # go1 is imparting damage on go2, therefore go2 receives delta-v
          dv2 += self.damage(do=go1, go=go2)
        if isinstance(go2, attack.DamageObj):
          dv1 += self.damage(do=go2, go=go1)

        # resolve if game-objects are moveable
        if go1.moveable and go2.moveable:
          dv1 += self.momentum_trade(go2, go1)
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
      # confirm go can take damage
      if hasattr(go, "attacker"):
        hit = go.attacker.receive_damage(go, do.power)

        # blowback
        if hit:
          dv = self.momentum_trade(do, go)
          # print("dv: {}".format(dv))

    return dv

