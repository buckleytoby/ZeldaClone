from config       import *
import utils
import gameObjects
import threading
import factory
import particles
import AI

class GravityArc(AI.Basic):
    # def __init__(self, *args):
    #     super().__init__(*args)

    def get_action(self, elapsed_time):
        """ get direction from heading and project velocity in that direction
        """
        dv = self.parent.velocity
        dv[1] += elapsed_time * 9.81 / 2.0 # integrate "half" gravity due to perspective
        out = {'dv': dv}
        cbs = []
        return out, cbs

class ExplosionParticle(particles.ParticleObj):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)

    self.nb_updates = self.duration / self.update_rate
    self.size_delta_w = self.width / self.nb_updates
    self.size_delta_h = self.height / self.nb_updates
    self.rgb = (255, 0, 0)

    self.AI = GravityArc(self)

  def update(self, seconds):
    super().update(seconds)

    # update size
    self.width -= self.size_delta_w
    self.height -= self.size_delta_h


class ExplosionFactory(factory.ParticleObjFactory):
  """ at the origin, generate many explosion particles in different directions and sizes """
  def __init__(self, **kwargs):
      super().__init__()
      self.creator = ExplosionParticle

      # params
      self.nb_particles = 10
      self.min_particle_size = 0.25 # tiles
      self.max_particle_size = 0.5 # tiles

      # values
      self.values['max_velocity'] = 3.0
      self.values['duration'] = 1.5
      self.values['objectType'] = "Explosion"
      self.values['collideable'] = False
    
  def create(self, x, y):
    out = []

    for i in range(self.nb_particles):
      # random angle, speed, and size
      a, b = 0, 2.0 * np.pi
      heading = (b - a) * np.random.random() + a
      a, b = self.min_particle_size, self.max_particle_size
      size = (b - a) * np.random.random() + a
      a, b = 0.5 * self.values['max_velocity'], self.values['max_velocity']
      velocity = (b - a) * np.random.random() + a

      direction = (m2d.Orientation(heading) * m2d.Vector.e0).array
      dx_actual, dy_actual = velocity * direction

      xx = x + 0.1 * np.random.random()
      yy = y + 0.1 * np.random.random()

      obj = super().create(xx, yy, dx_actual = dx_actual, dy_actual = dy_actual, width = size, height = size)
      # setup
      obj.setSpriteStatus(visible=True)

      out.append(obj)

    
    # start the threads
    [obj.start() for obj in out]
    return out

explosionFactory = ExplosionFactory()