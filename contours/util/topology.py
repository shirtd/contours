from functools import partial, reduce
from itertools import combinations
from multiprocessing import Pool
import numpy.linalg as la
import dionysus as dio
from tqdm import tqdm
import pickle as pkl
import numpy as np
import sys, time, gc

def dio_diagram(D):
    return [np.array([[p.birth, p.death] for p in d]) if len(d) else np.ndarray((0,2)) for d in D]

def init_diagrams(hom, filt):
    return dio_diagram(dio.init_diagrams(hom, filt))

def in_rng(c, I, open=False):
    return ((I[0] < c < I[1]) if open
        else (I[0] <= c <= I[1]))

def in_bounds(p, bounds, open=False):
    return all(map(lambda cI: in_rng(cI[0],cI[1],open), zip(p, bounds)))

def is_boundary(p, d, l):
    return not all(d < c < u - d for c,u in zip(p, l))

def to_path(vertices, nbrs):
    V = vertices.copy()
    cur = V.pop()
    path = [cur]
    while len(V):
        s = nbrs[cur].intersection(V)
        if len(s):
            cur = s.pop()
            path.append(cur)
            V.remove(cur)
        else:
            path = path[::-1]
            cur = path[-1]
    return path

def sfa_dio(f, min_cut=None, inf=-0.1, relative=False):
    filt = dio.fill_freudenthal(f)
    def _filter(s):
        if s.dimension() == 0:
            return s.data > min_cut
        return min(f.flatten()[i] for i in s) > min_cut
    if min_cut is None:
        hom = dio.homology_persistence(filt)
    elif relative:
        rel = dio.Filtration([s for s in filt if s.data <= min_cut])
    else:
        filt = dio.Filtration([s for s in filt if _filter(s)])
        hom = dio.homology_persistence(filt)
    dgms = dio.init_diagrams(hom, filt)
    return [np.array([[p.birth, p.death if p.death < np.inf else inf] for p in d]) if len(d) else np.ndarray((0,2)) for d in dgms]

# def to_path(vertices, nbrs):
#     V = vertices.copy()
#     cur = V.pop()
#     path = [cur]
#     while len(V):
#         cur = nbrs[cur].intersection(V).pop()
#         path.append(cur)
#         V.remove(cur)
#     return path
