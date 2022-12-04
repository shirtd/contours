from itertools import combinations
from scipy.spatial import Delaunay, Voronoi
import numpy.linalg as la
import dionysus as dio
import numpy as np
import diode

from ..complex.complex import Complex, SimplicialComplex, DualComplex
from ..util.geometry import circumcenter, circumradius
from ..plot import plot_vertex, plot_edge, plot_poly
from ..util.topology import in_bounds, to_path
from ..util.grid import local_lips
from ..config import COLOR
from ..util import stuple, tqit


class EmbeddedComplex(Complex):
    def __init__(self, P):
        self.P = P
        Complex.__init__(self, P.shape[-1])
    def orient_face(self, s):
        return s
    def plot_vertices(self, ax, visible=True, **kwargs):
        return {v : plot_vertex(ax, self.P[v[0]], visible, **kwargs) for v in self(0)}
    def plot_edges(self, ax, visible=True, **kwargs):
        return {e : plot_edge(ax, self.P[e], visible, **kwargs) for e in self(1)}
    def plot_polys(self, ax, visible=True, color_list=None, color=COLOR['red'], **kwargs):
        color_list = [color for _ in self(2)] if color_list is None else color_list
        return {t : plot_poly(ax, self.P[self.orient_face(t)], visible, color=c, **kwargs) for t,c in zip(self(2),color_list)}
    def plot(self, ax, color=COLOR['red'], edge_color=COLOR['black'], visible=True, fade=[1, 0.3, 0.15], zorder=1, alpha=1, s=9, tri_colors=None, edge_colors=None, lw=0.1):
        edge_kw = {'color' : edge_color} if edge_colors is None else {'color_list' : edge_colors}
        tri_kw = {'color' : color} if tri_colors is None else {'color_list' : tri_colors}
        return {0 : self.plot_vertices(ax, visible, alpha=alpha*fade[0], zorder=zorder+2, s=s, color='black'),
                1 : self.plot_edges(ax, visible, alpha=alpha*fade[1], zorder=zorder+1, lw=lw, **edge_kw),
                2 : self.plot_polys(ax, visible, alpha=alpha*fade[2], zorder=zorder, **tri_kw)}
    def get_boundary(self, bounds):
        out = {s for s in self(self.dim) if not self.in_bounds(s, bounds)}
        return {f for s in out for f in self.closure(s)}
    def in_bounds(self, s, bounds):
        pass

class DelaunayComplex(SimplicialComplex, EmbeddedComplex):
    def __init__(self, P, thresh=None, filter=None, verbose=False, desc='delaunay'):
        self.thresh = thresh
        EmbeddedComplex.__init__(self, P)
        for s,f in tqit(diode.fill_alpha_shapes(P, True), verbose, desc):
            if filter is None or filter(f):
                s = stuple(s)
                faces = set(self.face_it(s))
                for t in faces:
                    if not t in self:
                        self.add_new(t, set(self.face_it(s)), alpha=f)
                self.add_new(s, faces, alpha=f)
    def in_bounds(self, s, bounds):
        return in_bounds(circumcenter(self.P[s]), bounds)

class VoronoiComplex(DualComplex, EmbeddedComplex):
    def __init__(self, K, B=set(), verbose=False):
        self.thresh = K.thresh
        P = circumcenter(K.P[K(K.dim)])
        EmbeddedComplex.__init__(self, P)
        DualComplex.__init__(self, K, B, verbose)
        self.nbrs = {i : set() for i,_ in enumerate(self(0))}
        for e in self(1):
            if len(e) == 2:
                if e[0] in self.nbrs and e[1] in self.nbrs:
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
        for x in tqit(dio.fill_rips(P, dim, 2*thresh), verbose, desc):
            s = stuple(x)
            faces = set(self.face_it(s))
            self.add_new(s, faces, dist=x.data)
    def in_bounds(self, s, bounds):
        return True
    def to_dict(self):
        return {d : self(d) for d in range(3)}
