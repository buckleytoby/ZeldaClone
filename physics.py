

from config       import *


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
      
  def update(self, timeElapsed, gameObjects):
    dt = timeElapsed
    
    vel_dict = {}

    # first, update each game-objects location
    for key in gameObjects:
      gameObject = gameObjects[key]

      #gameObject.update(timeElapsed)
      action = gameObject.AI.getAction()
      vel_dict[gameObject.id] = np.zeros(2) #action['dv']
      dx, dy = action['dv']
      gameObject.dx = dx; gameObject.dy = dy

      gameObject.animation.updateSprite(dx, dy)
      gameObject.x += dt * dx
      gameObject.y += dt * dy

      # check collision against static objects
      ###for key in static_objects:
      ###  static_object = static_objects[key]
      """
      if self.rect.colliderect(wall.rect):
        if dx > 0: # Moving right; Hit the left side of the wall
            self.rect.right = wall.rect.left
        if dx < 0: # Moving left; Hit the right side of the wall
            self.rect.left = wall.rect.right
        if dy > 0: # Moving down; Hit the top side of the wall
            self.rect.bottom = wall.rect.top
        if dy < 0: # Moving up; Hit the bottom side of the wall
            self.rect.top = wall.rect.bottom
      """

    # second, resolve all collisions with gameObjects
    vel_residual = self.collision_resolution(vel_dict, timeElapsed, gameObjects)

    # third, add residual delta
    for key in gameObjects:
      gameObject = gameObjects[key]

      dx, dy = vel_residual[gameObject.id]
      #gameObject.animation.updateSprite(dx, dy)
      gameObject.x += dt * dx
      gameObject.y += dt * dy

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
      go1 = gameObjects[keys[c1]]
      go2 = gameObjects[keys[c2]]

      # sanity check
      if go1.id == go2.id:
        continue

      if go1.rect.colliderect(go2.rect):
        # force field away from center-of-mass
        dv1 = go2.com_vector(go1) * go2.mass / 30.0
        dv2 = go1.com_vector(go2) * go1.mass / 30.0

        # TODO: calculate required dv to align rect edges

        # calculate momentum and rebound, scaled by friction
        dv1 += go2.momentum * go2.unit_velocity / go1.mass * go1.friction # array
        dv2 += go1.momentum * go1.unit_velocity / go2.mass * go2.friction # array
        #

        # add to vel arr
        vel_dict[go1.id] += dv1
        vel_dict[go2.id] += dv2
    
    return vel_dict