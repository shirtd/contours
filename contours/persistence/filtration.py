from contours.complex.chains import Chain, CoChain
from contours.util import insert, partition


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
    def sort_faces(self, i, pivot=None, map=None, dual=False):
        pivot = self if pivot is None else pivot
        if dual:
            return sorted([pivot.index(f if map is None else map[f]) for f in self.complex.cofaces(self[i])])
        return sorted([pivot.index(f if map is None else map[f]) for f in self.complex.faces(self[i])])
    def sort_cofaces(self, i, pivot=None, map=None, dual=False):
        pivot = self if pivot is None else pivot
        if dual:
            return sorted([pivot.index(f if map is None else map[f]) for f in self.complex.faces(self[i])], reverse=True)
        return sorted([pivot.index(f if map is None else map[f]) for f in self.complex.cofaces(self[i])], reverse=True)
    def as_chain(self, i, pivot=None, map=None, dual=False):
        return Chain({i}, self.sort_faces(i, pivot, map, dual))
    def as_cochain(self, i, pivot=None, map=None, dual=False):
        return CoChain({i}, self.sort_cofaces(i, pivot, map, dual))
    def get_chains(self, rng, pivot=None, map=None, dual=False):
        return {i : self.as_chain(i, pivot, map, dual) for i in rng}
    def get_cochains(self, rng, pivot=None, map=None, dual=False):
        return {i : self.as_cochain(i, pivot, map, dual) for i in rng}
    def get_matrix(self, rng, coh=False, pivot=None, map=None, dual=False):
        return (self.get_cochains if coh else self.get_chains)(rng, pivot, map, dual)

class ImageFiltration(Filtration):
    def __init__(self, domain, codomain, map=None, dual=False, reverse=False, filter=None):
        self.domain, self.codomain, self.map, self.dual = domain, codomain, map, dual
        Filtration.__init__(self, codomain.complex, codomain.key, reverse, filter)
    def __call__(self, s):
        return s if self.map is None else self.map[s]
    def sort_faces(self, i):
        if self.dual:
            return sorted([self.domain.index(self(f)) for f in self.complex.cofaces(self[i])])
        return sorted([self.domain.index(self(f)) for f in self.complex.faces(self[i])])
    def sort_cofaces(self, i):
        if self.dual:
            return sorted([self.domain.index(self(f)) for f in self.complex.faces(self[i])], reverse=True)
        return sorted([self.domain.index(self(f)) for f in self.complex.cofaces(self[i])], reverse=True)
    # TODO !!
    # def get_matrix(self, K, rng, coh=False, pivot=None):
    #     return (self.get_cochains if coh else self.get_chains)(K, rng, pivot)
