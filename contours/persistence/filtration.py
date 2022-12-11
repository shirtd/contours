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
        try:
            return self.imap[hash(s)]
        except KeyError as e:
            print(s)
            raise e
    def get_range(self, R=set(), coh=False):
        it = reversed(list(enumerate(self))) if coh else enumerate(self)
        f = lambda L,ix: L if ix[0] in R else insert(L, ix[1].dim, ix[0])
        return partition(f, it, self.dim+1)[::(1 if coh else -1)]
    def sort_faces(self, i, pivot=None):
        pivot = self if pivot is None else pivot
        return sorted([pivot.index(f) for f in self.complex.faces(self[i])])
    def sort_cofaces(self, i, pivot=None):
        pivot = self if pivot is None else pivot
        return sorted([pivot.index(f) for f in self.complex.cofaces(self[i])], reverse=True)
    def get_chains(self, rng, pivot=None):
        return {i : Chain({i}, self.sort_faces(i, pivot)) for i in rng}
    def get_cochains(self, rng, pivot=None):
        return {i : CoChain({i}, self.sort_cofaces(i, pivot)) for i in rng}
    def get_matrix(self, rng, coh=False, pivot=None):
        return (self.get_cochains if coh else self.get_chains)(rng, pivot)

class ImageFiltration(Filtration):
    def __init__(self, domain, codomain, map=None, dual=False, reverse=False, filter=None):
        self.domain, self.codomain, self.dual = domain, codomain, dual
        self.map = {s : s for s in domain} if map is None else map
        self.inverse = {v : k for k,v in self.map.items()}
        filt = lambda s: s in self.inverse and (True if filter is None else filter(s))
        Filtration.__init__(self, codomain.complex, codomain.key, reverse, filt)
    def __call__(self, s, *args, **kwargs):
        return s if self.map is None else self.map[s]
    def sort_faces(self, i, *args, **kwargs):
        if self.dual:
            return sorted([self.domain.index(self(f)) for f in self.complex.cofaces(self[i])])
        return sorted([self.domain.index(self(f)) for f in self.complex.faces(self[i])])
    def sort_cofaces(self, i, *args, **kwargs):
        if self.dual:
            return sorted([self.domain.index(self(f)) for f in self.complex.faces(self[i])], reverse=True)
        return sorted([self.domain.index(self(f)) for f in self.complex.cofaces(self[i])], reverse=True)
