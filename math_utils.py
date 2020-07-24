
from config       import *

def zero_protection_divide(n, d):
    return n / d if not np.isclose(d, 0.0, 1e-4, 1e-5) else np.zeros_like(n)

def normalize(vec):
    return zero_protection_divide(vec, np.linalg.norm(vec))

# # # @profile
def eucl_dist(vec1, vec2):
    # dist = np.sum( np.abs( vec1 - vec2) )
    dist = scSpatial.distance.cityblock(vec1, vec2)
    return dist