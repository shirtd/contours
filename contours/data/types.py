import numpy as np

class Function:
    def __init__(self, function, cuts, colors):
        self.function  = function
        self.cuts, self.colors = cuts, colors
    def __call__(self, i):
        return self.function[i]
    def __len__(self):
        return len(self.function)
    def get_cut(self, f):
        for i, (a,b) in enumerate(zip(self.cuts[:-1], self.cuts[1:])):
            if a <= f < b:
                return i
        return 0

class PointCloud:
    def __init__(self, points):
        self.points = points
    def __getitem__(self, i):
        return self.points[i]
    def __iter__(self):
        yield from self.points
    def plot(self, ax, visible=True, **kwargs):
        p = ax.scatter(self[:,0], self[:,1], **kwargs)
        p.set_visible(visible)
        return p
