from scipy.spatial import KDTree
import matplotlib.pyplot as plt
import numpy.linalg as la
import dionysus as dio
import numpy as np
import os

# from lips.topology.util import sfa_dio
from ..config import COLOR, KWARGS
from ..data import Data, DataFile, Function, PointCloud
from ..surface.sample import Sample, MetricSampleData
from ..plot import init_surface, init_barcode, plot_barcode
from ..util.grid import gaussian_field, down_sample, lipschitz_grid
from ..util.geometry import coords_to_meters, greedysample
# from ..util.topology import  init_barcodes
from ..util import lmap, format_float, diff


class Surface(Function, PointCloud):
    def __init__(self, surface, grid, cuts, colors, pad=0):
        Function.__init__(self, surface.flatten(), cuts, colors)
        PointCloud.__init__(self, np.vstack(lmap(lambda x: x.flatten(), grid)).T)
        self.surface, self.grid = surface, grid
        self.shape, self.pad = surface.shape, pad
        self.tree = KDTree(self.points)
    def get_data(self):
        return np.vstack([self.points.T, self.surface.flatten()]).T
    def get_barcode(self):
        filt = dio.fill_freudenthal(self.surface)
        def f(s):
            if s.dimension() == 0:
                return s.data > self.cuts[0]
            return min(self(i) for i in s) > self.cuts[0]
        filt = dio.Filtration([s for s in filt if f(s)])
        hom = dio.homology_persistence(filt)
        return init_barcode(hom, filt)
    def init_plot(self):
        return init_surface(self.extents, self.pad)
    def plot(self, ax, zorder=0, **kwargs):
        return {'surface' : ax.contourf(*self.grid, self.surface, levels=self.cuts, colors=self.colors, zorder=zorder, **kwargs),
                'contours' : ax.contour(*self.grid, self.surface, levels=self.cuts[1:], colors=self.colors[1:], zorder=zorder+1)}
    def get_radius(self, points, radius, mult=3):
        T = KDTree(points)
        data = self.get_data()[self.function > self.cuts[0]]
        radius = max(T.query(p)[0] for p in data[:,:2])
        dx = (self.grid[0].max() - self.grid[0].min()) / self.shape[0]
        dy = (self.grid[1].max() - self.grid[1].min()) / self.shape[1]
        error = np.sqrt(dx**2 + dy**2) / mult
        return int(np.ceil(radius + error))
    def greedy_sample(self, thresh, mult, seed=None, greedyfun=False, config=None, noise=None):
        data = self.get_data()[self.function > self.cuts[0]]
        if seed is None:
            seed = np.random.randint(len(data))
            print(f'SEED: {seed}')
        sample = data[greedysample(data[:,:2], mult*thresh, seed)]
        radius = self.get_radius(sample[:,:2], thresh)
        print(f'coverage radius: {radius}')
        return MetricSampleData(sample, radius, self.name, self.folder, self.config)
    def sample(self, thresh, sample=None, config=None):
        fig, ax = self.init_plot()
        surf_plt = self.plot(ax, **KWARGS['surf'])
        data = self.get_data()
        tree = KDTree(data[:,:2])
        if sample is None:
            points = []
        else:
            thresh = sample.radius if thresh is None else thresh
            sample.plot(ax, color='black', zorder=10, s=5)
            sample.plot_cover(ax, alpha=0.3, color='gray', zorder=2, radius=thresh)
            points = sample.get_data().tolist()
        def onclick(e):
            l = tree.query(np.array([e.xdata, e.ydata]))[1]
            p = data[l].tolist() + [self.lips]
            ax.add_patch(plt.Circle(p[:2], thresh, color=COLOR['red1'], zorder=3, alpha=0.5))
            ax.scatter(p[0], p[1], c='black', zorder=4, s=5)
            plt.pause(0.01)
            points.append(p)
        cid = fig.canvas.mpl_connect('button_press_event', onclick)
        plt.show()
        fig.canvas.mpl_disconnect(cid)
        plt.close(fig)
        if len(points):
            points = np.vstack(sorted(points, key=lambda x: x[2]))
            return MetricSampleData(points, thresh, self.name, self.folder, self.config)
        return None

class ScalarField(Surface):
    def __init__(self, surface, extents, cuts, colors, pad=0, lips=None):
        self.extents, self.lips = extents, lips
        dx = np.linspace(*extents[0], surface.shape[1])
        dy = np.linspace(*extents[1], surface.shape[0])
        grid = np.stack(np.meshgrid(dx, dy))
        Surface.__init__(self, surface, grid, cuts, colors, pad)

class ScalarFieldData(ScalarField, Data):
    def __init__(self, name, folder, surface, extents, cuts, colors, pad=0, lips=None):
        config = {'extents' : extents, 'cuts' : cuts, 'colors' : colors, 'pad' : pad, 'lips' : lips}
        ScalarField.__init__(self, surface, **config)
        Data.__init__(self, surface, name, folder, config)
    def save(self, config=None):
        if self.lips is None:
            self.config['lips'] = lipschitz_grid(self.surface, self.grid, self.cuts[0])
        Data.save(self, self.surface.tolist())

class USGSScalarFieldData(ScalarFieldData):
    def __init__(self, file_name, cuts, colors, pad=0, downsample=None, lips=None):
        name = os.path.basename(os.path.splitext(file_name)[0])
        folder = os.path.join(os.path.dirname(file_name), name)
        print(f'loading {file_name}')
        surface = np.loadtxt(file_name, skiprows=6)
        if downsample is not None:
            surface = down_sample(surface, downsample)
            name += str(downsample)
        extents = self.get_extents(file_name)
        ScalarFieldData.__init__(self, name, folder, surface, extents, cuts, colors, pad, lips)
    def get_extents(self, file_name):
        with open(file_name, 'r') as f:
            cols, rows = (int(f.readline().split()[1]), int(f.readline().split()[1]))
            x0, y0 = (float(f.readline().split()[1]), float(f.readline().split()[1]))
            step = float(f.readline().split()[1])
        x1, y1 = x0 + cols*step, y0 + rows*step
        xd = coords_to_meters(x0, y0, x1, y0)
        yd = coords_to_meters(x0, y0, x0, y1)
        return np.array([[0, xd], [0, yd]])

class GaussianScalarFieldData(ScalarFieldData):
    def __init__(self, name, folder, resolution, downsample, cuts, colors, gauss_args, extents, pad=0, lips=None, scale=None):
        resolution0 = int(resolution * diff(extents[0]) / diff(extents[1]))
        grid = np.meshgrid(np.linspace(*extents[0], resolution0), np.linspace(*extents[1], resolution))
        surface = gaussian_field(grid[0], grid[1], gauss_args)
        if scale is not None:
            surface *= scale
            grid *= scale
            pad *= scale
            cuts = (scale*np.array(cuts)).tolist()
            extents = (scale*np.array(extents)).tolist()
        if downsample is not None:
            surface = down_sample(surface, downsample)
            name += str(downsample)
        ScalarFieldData.__init__(self, name, folder, surface, extents, cuts, colors, pad, lips)

class ScalarFieldFile(ScalarFieldData, DataFile):
    def __init__(self, file_name, json_file=None):
        if json_file is None:
            json_file = f'{os.path.splitext(file_name)[0]}.json'
        DataFile.__init__(self, file_name, json_file)
        name, folder = os.path.splitext(self.file)[0], os.path.dirname(file_name)
        ScalarFieldData.__init__(self, name, folder, self.load_data(), **self.load_json())
