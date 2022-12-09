from contours.util import diff, identity, reduce, tqdm, np

# TODO  row and column relative indices
#       unpairs contains death indices, pairs contains birth indices

class Reduction:
    def __init__(self, filt, relative, coh, pivot, map, dual):
        self.relative, self.coh, self.dim = relative, coh, filt.dim
        self.__sequence = filt.get_range(relative, coh)
        self.__n = len(filt) - len(relative)
        if map is not None:
            rmap = {v : k for k,v in map.items()}
            self.pivot_map = {i : filt.index(rmap[s]) for i,s in enumerate(pivot)}
        else:
            self.pivot_map = {i : filt.index(s) for i,s in enumerate(pivot)}
        self.unpairs, self.pairs, self.copairs = set(self), {}, {}
        self.D = filt.get_matrix(self, coh, pivot, map, dual)
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
        # TODO (I)
        if self.pivot_map[b] in self.unpairs:
            self.unpairs.remove(self.pivot_map[b])
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
                low = self.D[i].get_pivot(self.relative)#, self.pivot_map)
                while self.__paired(low):
                    self.D[i] += self.D[self.__pair(low)]
                    low = self.D[i].get_pivot(self.relative)#, self.pivot_map)
                if low is not None:
                    self[low] = i

class Diagram(Reduction):
    def __init__(self, filt, relative=set(), coh=False, pivot=None, map=None, dual=False, clearing=False, verbose=False, domap=False):
        pivot = filt if pivot is None else pivot
        Reduction.__init__(self, filt, relative, coh, pivot, map, dual)
        self.reduce(clearing, verbose)
        # res = self.get_diagram(K, F, pivot)
        # if domap:
        #     self.diagram, self.fmap = res
        # else:
        #     self.diagram, self.fmap = res, None
    def __call__(self, i):
        if i in self.fmap:
            return self.fmap[i]
        return None
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
    def get_diagram(self, filt, pivot=None, smoothing=None, domap=False):
        pivot = filt if pivot is None else pivot
        fmap, dgms = {}, [[] for d in range(self.dim+1)]
        for i, j in self.items():
            b = pivot.complex[pivot[i]]
            d = filt.complex[filt[self[i]]]
            fmap[i] = [b(pivot.key), d(filt.key)][::(-1 if filt.reverse else 1)]
            if smoothing is not None:
                fmap[i] = smoothing(fmap[i])
            if fmap[i][0] < fmap[i][1]:
                dgms[b.dim].append(fmap[i])
        for i in self.unpairs:
            b = filt.complex[filt[i]]
            fmap[i] = [b(pivot.key) if smoothing is None else b(pivot.key), np.inf]
            dgms[b.dim].append(fmap[i])
        dgms = [np.array(sorted(filter(lambda p: p[0] < p[1], d), key=lambda p: p[0])) for d in dgms]
        # dgms = list(map(np.array, dgms))
        if domap:
            return dgms, fmap
        return dgms
    # def element_pair(self, K, F, i):
    #     return [K[F[i]], K[F[self[i]]]]
    # def element_diagram(self, K, F):
    #     it = map(lambda i: self.element_pair(K, F, i), self)
    #     return partition(lambda L,p: insert(L, p[0].dim, p), it, self.dim+1)
    # def key_pair(self, K, key, p):
    #     return np.array([K[p[0]](key), np.inf if p[1] is None else K[p[1]](key)])
    # def get_diagram(self, K, F):
    #     f = lambda d: sorted(d, key=partial(self.key_pair, K, F.key))
    #     edgm = map(f, self.element_diagram(K, F)
    #     dgm = [np.vstack(map(partial(self.key_pair, K, F.key), d)) for d in edgm]
