from functools import reduce
from tqdm import tqdm
import numpy as np


def identity(x):
    return x

def diff(p):
    return p[1] - p[0]

def stuple(l, *args, **kw):
    return tuple(sorted(l, *args, **kw))

def lmap(f, l):
    return list(map(f,l))

def grid_coord(coords, n):
    return [coords//n, coords%n]

def format_float(f):
    return np.format_float_scientific(f, trim='-') if int(f) != f else str(int(f))

def scale(x):
    return (x - x.min()) / (x.max() - x.min())

def tqit(it, verbose=False, desc=None, n=None):
    return tqdm(it, desc=desc, total=n) if verbose else it

def insert(l, i, x):
    l[i] += [x]
    return l

def partition(f, l, n):
    return reduce(f, l, [[] for _ in range(n)])
