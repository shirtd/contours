from contours.complex.chains import Chain, CoChain
from contours.util import insert, partition


class Filtration:
    def __init__(self, K, key, reverse=False, filter=None):
        self.sequence = K.get_sequence(key, reverse)
        self.dim, self.key, self.reverse = K.dim, key, reverse
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
    def sort_faces(self, K, i, pivot=None, map=None, dual=False):
        pivot = self if pivot is None else pivot
        if dual:
            return sorted([pivot.index(f if map is None else map[f]) for f in K.cofaces(self[i])])
        return sorted([pivot.index(f if map is None else map[f]) for f in K.faces(self[i])])
    def sort_cofaces(self, K, i, pivot=None, map=None, dual=False):
        pivot = self if pivot is None else pivot
        if dual:
            return sorted([pivot.index(f if map is None else map[f]) for f in K.faces(self[i])], reverse=True)
        return sorted([pivot.index(f if map is None else map[f]) for f in K.cofaces(self[i])], reverse=True)
    def as_chain(self, K, i, pivot=None, map=None, dual=False):
        return Chain({i}, self.sort_faces(K, i, pivot, map, dual))
    def as_cochain(self, K, i, pivot=None, map=None, dual=False):
        return CoChain({i}, self.sort_cofaces(K, i, pivot, map, dual))
    def get_chains(self, K, rng, pivot=None, map=None, dual=False):
        return {i : self.as_chain(K, i, pivot, map, dual) for i in rng}
    def get_cochains(self, K, rng, pivot=None, map=None, dual=False):
        return {i : self.as_cochain(K, i, pivot, map, dual) for i in rng}
    def get_matrix(self, K, rng, coh=False, pivot=None, map=None, dual=False):
        return (self.get_cochains if coh else self.get_chains)(K, rng, pivot, map, dual)

# class ImageFiltration(Filtration):
#     def __init__(self, K, key, map, reverse=False, filter=None):
#         self.domian, self.codomain, self.map = domain, codomain, map
#         Filtration.__init__(self, K, key, reverse, filter)
#     def __call__(self, s):
#         return self.map[s]
#     def sort_faces(self, K, i, pivot=None):
#         pivot = self if pivot is None else pivot
#         return sorted([pivot.index(self(f)) for f in K.faces(self[i])])
#     def sort_cofaces(self, K, i, pivot=None):
#         pivot = self if pivot is None else pivot
#         return sorted([pivot.index(self(f)) for f in K.cofaces(self[i])], reverse=True)
#     # TODO !!
#     # def get_matrix(self, K, rng, coh=False, pivot=None):
#     #     return (self.get_cochains if coh else self.get_chains)(K, rng, pivot)
