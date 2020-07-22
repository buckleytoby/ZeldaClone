
from config       import *

def zero_protection_divide(n, d):
    return n / d if not np.isclose(d, 0.0, 1e-4, 1e-5) else np.zeros_like(n)

def normalize(vec):
    return zero_protection_divide(vec, np.linalg.norm(vec))