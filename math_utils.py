
from config       import *

def divide_vector(n, d):
    # assume n and d are both 2-long and positive vectors
    if np.sum(d) < 1e-3:
        return np.zeros_like(n)
    else:
        return n / d

def zero_protection_divide(n, d):
    return n / d if not np.isclose(d, 0.0, 1e-4, 1e-5) else np.zeros_like(n)

def normalize(vec):
    return divide_vector(vec, np.linalg.norm(vec))

# # # @profile
def eucl_dist(vec1, vec2):
    # dist = np.sum( np.abs( vec1 - vec2) )
    dist = scSpatial.distance.cityblock(vec1, vec2)
    return dist

def dir_to_target(me, target):
    vector = target - me
    unit_direction = divide_vector(vector, np.linalg.norm(vector))
    return unit_direction