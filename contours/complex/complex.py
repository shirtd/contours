import numpy as np
import numpy.linalg as la
from itertools import combinations

from ..util import stuple, tqit


class Element:
    def __init__(self, atoms, dim, **data):
        self.dim, self.data = dim, data
        self.__atoms = stuple(atoms)
    def __iter__(self):
        yield from self.__atoms
    def __len__(self):
        return len(self.__atoms)
    def __index__(self):
        return list(self.__atoms)
    def __getitem__(self, i):
        if i < len(self):
            return self.__atoms[i]
    def __call__(self, key):
        if key in self.data:
            return self.data[key]
    def key(self):
        return (self.dim, self.__atoms)
    def __hash__(self):
        return hash(self.key())
    def __eq__(self, other):
        return hash(self) == hash(other)
    def __lt__(self, other):
        return (self.dim, self.__atoms) < (other.dim, other.__atoms)

class Cell(Element):
    def __repr__(self):
        return '{%d; %s}' % (self.dim, ' '.join(map(str, self)))

class Simplex(Element):
    def __init__(self, vertices, **data):
        Element.__init__(self, vertices, len(vertices)-1, **data)
    def key(self):
        return Element.key(self)[1]
    def __repr__(self):
        return '[%s]' % ' '.join(map(str, self))

class Complex:
    def __init__(self, dim):
        self.dim = dim
        self.__elements = {d : [] for d in range(dim+1)}
        self.__map, self.__faces, self.__cofaces = {}, {}, {}
    def add(self, cell, faces):
        k = hash(cell)
        if k in self.__map:
            return cell
        self.__elements[cell.dim].append(cell)
        self.__map[k] = cell
        self.__faces[k] = set()
        self.__cofaces[k] = set()
        for f in faces:
            fk = hash(f)
            self.__faces[k].add(fk)
            self.__cofaces[fk].add(k)
        return cell
    def faces(self, c):
        return [self.__map[f] for f in self.__faces[hash(c)]]
    def cofaces(self, c):
        return [self.__map[f] for f in self.__cofaces[hash(c)]]
    def items(self):
        yield from self.__elements.items()
    def keys(self):
        yield from self.__elements.keys()
    def values(self):
        yield from self.__elements.values()
    def __getitem__(self, key):
        if isinstance(key, int):
            key = (key,)
        return self.__map[hash(key)]
    def __call__(self, dim):
        if dim in self.__elements:
            return self.__elements[dim]
        return set()
    def __len__(self):
        return len(self.__map)
    def __iter__(self):
        yield from self.__map.values()
    def __contains__(self, key):
        return hash(key) in self.__map
    def get_sequence(self, key, reverse=False, filter=None):
        r = -1 if reverse else 1
        return sorted(self if filter is None else filter(self), key=lambda s: (r * s(key), s))
    def closure(self, s):
        return {s}.union({f for t in self.faces(s) for f in self.closure(t)})
    def __repr__(self):
        return ''.join(['%d:\t%d elements\n' % (d, len(self(d))) for d in range(self.dim+1)])
    def sublevels(self, sample, key='sub', verbose=False):
        for s in tqit(self, verbose, 'sub'):
            s.data[key] = sample(s).max()
    def superlevels(self, sample, key='sup', verbose=False):
        for s in tqit(self, verbose, 'sup'):
            s.data[key] = sample(s).min()
    def lips_sub(self, subsample):
        for p, s in zip(self.P, self(0)):
            s.data['max'] = min(f + subsample.config['lips']*la.norm(p - q) for q, f, c in zip(subsample, subsample.function, constants))
            s.data['min'] = max(f - subsample.config['lips']*la.norm(p - q) for q, f, c in zip(subsample, subsample.function, constants))
        for s in self(1)+self(2):
            s.data['max'] = max(self(0)[v].data['max'] for v in s)
            s.data['min'] = max(self(0)[v].data['min'] for v in s)

class CellComplex(Complex):
    def add_new(self, c, dim, faces, **data):
        return self.add(Cell(c, dim, **data), faces)

class SimplicialComplex(Complex):
    def face_it(cls, s):
        dim = len(s)-1
        if dim:
            for i in range(dim+1):
                yield s[:i]+s[i+1:]
    def add_new(self, s, faces, **data):
        return self.add(Simplex(s, **data), faces)
    def lips(self, sample, constant, invert_min=False):
        for s in self(0):
            s.data['max'] = s.data['min'] = sample(s[0])
        for s in self(1):
            d = la.norm(sample[s[0]] - sample[s[1]])
            s.data['max'] = max(sample(v) for v in s) + constant * d / 2
            s.data['min'] = min(sample(v) for v in s) - constant * d / 2
        for s in self(2):
            s.data['max'] = max(self[e].data['max'] for e in combinations(s,2))
            s.data['min'] = (max if invert_min else min)(self[e].data['min'] for e in combinations(s,2))

class DualComplex(CellComplex):
    def __init__(self, K, B, verbose=False, desc='voronoi'):
        self.K, self.B = K, B
        CellComplex.__init__(self, K.dim)
        self.__dmap, self.__pmap = {}, {}
        self.__imap = {t : i for i,t in enumerate(K(K.dim))}
        it = (s for d in reversed(range(self.dim+1)) for s in K(d))
        for s in tqit(it, verbose, desc, len(K)):
            if not s in B:
                self.add_dual(K, s)
    def get_vertices(self, K, s):
        if s.dim < self.dim:
            return {v for f in K.cofaces(s) for v in self.get_vertices(K, f)}
        return {self.__imap[s]}
    def add_dual(self, K, s):
        dim = self.dim - s.dim
        vs = self.get_vertices(K, s)
        faces = [self.dual(f) for f in K.cofaces(s)]
        ds = self.add_new(vs, dim, faces, **s.data)
        self.__dmap[s], self.__pmap[ds] = ds, s
        return ds
    def dual(self, s):
        return self.__dmap[s]
    def primal(self, ds):
        return self.__pmap[ds]
    def sublevels(self, sample, key='sub', verbose=False):
        for s in tqit(self, verbose, 'sub'):
            s.data[key] = sample(self.primal(s)).min()
    def superlevels(self, sample, key='sup', verbose=False):
        for s in tqit(self, verbose, 'sup'):
            s.data[key] = sample(self.primal(s)).max()

# class DelaunayComplex(SimplicialComplex):
#     def __init__(self, P):
#         SimplicialComplex.__init__(self, P.shape[-1])
#         self.P = P
#         self.circumcenters = {}
#         delaunay = Delaunay(P)
#         for s in delaunay.simplices:
#             self.add_closure(stuple(s))
#     def add_closure(self, s):
#         if len(s) == 1:
#             return self.add_new(s, [], alpha=0)
#         c = self.get_circumcenter(s)
#         self.circumcenters[s] = c
#         alpha = la.norm(self.P[s[0]] - c) ** 2
#         faces = list(self.face_it(s))
#         for i,f in enumerate(faces):
#             if not f in self:
#                 self.add_closure(f)
#             if len(f) > 1:
#                 fc = self.circumcenters[f]
#                 if (la.norm(self.P[i] - fc) ** 2 < self[f]('alpha')
#                         and alpha < self[f]('alpha')):
#                     self[f].data['alpha'] = alpha
#         return self.add_new(s, faces, alpha=alpha)
#     def get_circumcenter(self, s):
#         dim, p = len(s)-1, self.P[list(s)]
#         return (tet_circumcenter(p) if dim == 3
#             else tri_circumcenter(p) if dim == 2
#             else p.sum(0) / 2 if dim == 1 else None)
#     # def get_alpha(self, s):
#     #     dim, p = len(s)-1, self.P[list(s)]
#     #     return (tet_circumradius(p) if dim == 3
#     #         else tri_circumradius(p) if dim == 2
#     #         else la.norm(diff(p)) if dim == 1
#     #         else 0) ** 2 / 4
