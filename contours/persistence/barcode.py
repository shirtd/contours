from contours.util import diff, identity, reduce, tqdm, np
from contours.persistence import ImageFiltration

# TODO  row and column relative indices
#       unpairs contains death indices, pairs contains birth indices

class Reduction:
    def __init__(self, filt, relative, coh):
        self.relative, self.coh, self.dim = relative, coh, filt.dim
        self.__sequence = filt.get_range(relative, coh)
        self.__n = len(filt) - len(relative)
        # # TODO (I)
        # if isinstance(filt, ImageFiltration):
        #     self.pivot_map = {i : filt.index(filt.inverse[s]) for i,s in enumerate(pivot)}
        self.unpairs, self.pairs, self.copairs = set(self), {}, {}
        self.D = filt.get_matrix(self, coh)
    def __iter__(self):
        for seq in self.__sequence:
            yield from seq
    def __len__(self):
        return self.__n
    def __setitem__(self, b, d):
        if self.coh:
            b, d = d, b
        self.pairs[b] = d
        self.copairs[d] = b
        # # TODO (I)
        # if self.pivot_map[b] in self.unpairs:
        #     self.unpairs.remove(self.pivot_map[b])
        if d in self.unpairs:
            self.unpairs.remove(d)
    def __pair(self, low):
        pairs = self.copairs if self.coh else self.pairs
        return pairs[low] if low in pairs else None
    def __paired(self, low):
        return low is not None and low in (self.copairs if self.coh else self.pairs)
    def reduce(self, clearing=False, verbose=False, desc='persist'):
        for i in (tqdm(self, total=len(self), desc=desc) if verbose else self):
            if not (clearing and self.__paired(i)):
                low = self.D[i].get_pivot(self.relative)
                while self.__paired(low):
                    self.D[i] += self.D[self.__pair(low)]
                    low = self.D[i].get_pivot(self.relative)
                if low is not None:
                    self[low] = i

class Barcode(Reduction):
    def __init__(self, filt, relative=set(), coh=False, clearing=False, verbose=False):
        Reduction.__init__(self, filt, relative, coh)
        self.reduce(clearing, verbose)
    def __getitem__(self, i):
        return self.pairs[i] if i in self.pairs else None
    def __contains__(self, i):
        return i is not None and i in self.pairs
    def items(self):
        yield from self.pairs.items()
    def keys(self):
        yield from self.pairs.keys()
    def values(self):
        yield from self.pairs.values()
    def is_relative(self, i):
        return i in self.relative
    def get_barcode(self, filt, smoothing=None):
        smoothing = (lambda l: l) if smoothing is None else smoothing
        barcode = [[] for d in range(self.dim+1)]
        for i, j in self.items():
            barcode[filt.get_dim(i)].append(smoothing(filt.get_interval(i, j)))
        for i in self.unpairs:
            barcode[filt[i].dim].append(smoothing(filt.get_interval(i)))
        return [np.array(sorted(filter(lambda p: p[0] < p[1], d), key=lambda p: p[0])) for d in barcode]
