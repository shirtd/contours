from itertools import combinations
import numpy.linalg as la
import dionysus as dio
import numpy as np
import diode

from ..complex.complex import Complex, SimplicialComplex, DualComplex
from ..util.geometry import circumcenter, circumradius
from ..util.topology import in_bounds, to_path
from ..util.grid import local_lips
from ..util import stuple, tqit


class EmbeddedComplex(Complex):
    def __init__(self, P):
        self.P = P
        Complex.__init__(self, P.shape[-1])
    def get_boundary(self, bounds):
        out = {s for s in self(self.dim) if not self.in_bounds(s, bounds)}
        return {f for s in out for f in self.closure(s)}
    def in_bounds(self, s, bounds):
        pass

class DelaunayComplex(SimplicialComplex, EmbeddedComplex):
    def __init__(self, P, verbose=False, desc='delaunay'):
        EmbeddedComplex.__init__(self, P)
        for s,f in tqit(diode.fill_alpha_shapes(P, True), verbose, desc):
            s = stuple(s)
            faces = set(self.face_it(s))
            self.add_new(s, faces, alpha=f)
    def in_bounds(self, s, bounds):
        return in_bounds(circumcenter(self.P[s]), bounds)

class VoronoiComplex(DualComplex, EmbeddedComplex):
    def __init__(self, K, B=set(), verbose=False):
        P = circumcenter(K.P[K(K.dim)])
        EmbeddedComplex.__init__(self, P)
        DualComplex.__init__(self, K, B, verbose)
        self.nbrs = {i : set() for i,_ in enumerate(self(0))}
        for e in self(1):
            if len(e) == 2:
                self.nbrs[e[0]].add(e[1])
                self.nbrs[e[1]].add(e[0])
    def orient_face(self, s):
        return to_path({v for v in s}, self.nbrs)
    def in_bounds(self, s, bounds):
        return all(in_bounds(self.P[v], bounds) for v in s)

class RipsComplex(SimplicialComplex, EmbeddedComplex):
    def __init__(self, P, thresh, dim=2, verbose=False, desc='rips'):
        self.thresh = thresh
        EmbeddedComplex.__init__(self, P)
        for x in tqit(dio.fill_rips(P, dim, thresh), verbose, desc):
            s = stuple(x)
            faces = set(self.face_it(s))
            self.add_new(s, faces, dist=x.data)
    def in_bounds(self, s, bounds):
        return True
    def to_dict(self):
        return {d : self(d) for d in range(3)}
    def sublevels(self, sample, key='f', verbose=False):
        for s in tqit(self, verbose, 'sub'):
            s.data[key] = sample(s).max()
    def superlevels(self, sample, key='f', verbose=False):
        for s in tqit(self, verbose, 'sup'):
            s.data[key] = sample(s).min()
    def lips(self, sample, constant, invert_min=False):
        for s in self(0):
            s.data['max'] = s.data['min'] = sample(s[0])
        for s in self(1):# + self(2):
            s.data['max'] = max(sample(v) for v in s) + constant * s.data['dist'] / 2
            s.data['min'] = min(sample(v) for v in s) - constant * s.data['dist'] / 2
        # for s in self(1):
        #     sf = sample(s[0]) + sample(s[1])
        #     sd = constant * s.data['dist']
        #     s.data['max'] = (sf + sd) / 2
        #     s.data['min'] = (sf - sd) / 2
        for s in self(2):
            s.data['max'] = max(self[e].data['max'] for e in combinations(s,2))
            s.data['min'] = (max if invert_min else min)(self[e].data['min'] for e in combinations(s,2))
    def lips_sub(self, subsample, local=False):
        if local:
            constants = subsample.constants
        else:
            constants = np.ones(len(subsample)) * subsample.config['lips']
        for p, s in zip(self.P, self(0)):
            s.data['max'] = min(f + c*la.norm(p - q) for q, f, c in zip(subsample, subsample.function, constants))
            s.data['min'] = max(f - c*la.norm(p - q) for q, f, c in zip(subsample, subsample.function, constants))
        for s in self(1)+self(2):
            s.data['max'] = max(self(0)[v].data['max'] for v in s)
            s.data['min'] = max(self(0)[v].data['min'] for v in s)
