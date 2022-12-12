from contours.complex.chains import Chain, CoChain
from contours.util import insert, partition
import numpy as np


class Filtration:
    def __init__(self, complex, key, reverse=False, filter=None):
        self.complex, self.key, self.dim, self.reverse = complex, key, complex.dim, reverse
        self.sequence = complex.get_sequence(key, reverse, filter)
        self.imap = {hash(s) : i for i, s in enumerate(self)}
    def __len__(self):
        return len(self.sequence)
    def __iter__(self):
        yield from self.sequence
    def __getitem__(self, i):
        return self.sequence[i]
    def index(self, s):
        return self.imap[hash(s)]
    def get_range(self, R=set(), coh=False):
        it = reversed(list(enumerate(self))) if coh else enumerate(self)
        f = lambda L,ix: L if ix[0] in R else insert(L, ix[1].dim, ix[0])
        return partition(f, it, self.dim+1)[::(1 if coh else -1)]
    def get_column(self, i, coh=False):
        return self.complex.cofaces(self[i]) if coh else self.complex.faces(self[i])
    def sort_column(self, i, coh=False):
        return sorted(map(self.index, self.get_column(i, coh)), reverse=coh)
    def get_matrix(self, rng, coh=False):
        return {i : (CoChain if coh else Chain)({i}, self.sort_column(i, coh)) for i in rng}
    def get_birth(self, i=None):
        return -np.inf if i is None else self[i](self.key)
    def get_death(self, j=None):
        return np.inf if j is None else self[j](self.key)
    def get_interval(self, i, j=None):
        if self.reverse:
            return [self.get_birth(j), self.get_death(i)]
        return [self.get_birth(i), self.get_death(j)]
    def get_dim(self, i):
        return self[i].dim

class ImageFiltration(Filtration):
    def __init__(self, domain, codomain, map=None, dual=False, reverse=False, filter=None):
        self.domain, self.codomain, self.dual = domain, codomain, dual
        self.map = {s : s for s in domain} if map is None else map
        self.inverse = {v : k for k,v in self.map.items()}
        filt = lambda s: s in self.inverse and (True if filter is None else filter(s))
        Filtration.__init__(self, codomain.complex, codomain.key, reverse, filt)
    def __call__(self, s):
        return s if self.map is None else self.map[s]
    def get_column(self, i, coh=False):
        if self.dual:
            return self.complex.faces(self[i]) if coh else self.complex.cofaces(self[i])
        return Filtration.get_column(self, i, coh)
    def sort_column(self, i, coh=False):
        return sorted([self.domain.index(self.inverse[f]) for f in self.get_column(i, coh)], reverse=coh)
    def get_birth(self, i=None):
        return -np.inf if i is None else self.domain[i](self.domain.key)
    def get_dim(self, i):
        return self.domain[i].dim
