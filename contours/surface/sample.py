from scipy.spatial import KDTree
import matplotlib.pyplot as plt
import numpy as np
import os, json

from ..config import COLOR, KWARGS
from ..data import Data, DataFile, Function, PointCloud
from ..util import lmap, format_float
from ..complex import RipsComplex, DelaunayComplex, VoronoiComplex
from ..persistence import Diagram, Filtration
from ..util.grid import lipschitz_grid
from ..util.geometry import coords_to_meters, greedysample
from ..plot import init_surface, plot_balls, init_barcode, plot_barcode


OOPS=2


class Sample(Function, PointCloud):
    def __init__(self, points, function, cuts, colors, pad, parent):
        Function.__init__(self, function, cuts, colors)
        PointCloud.__init__(self, points)
        self.pad, self.parent = pad, parent
    def get_data(self):
        return np.vstack([self.points.T, self.function]).T
    def get_levels(self):
        cuts = [int(a+(b-a)/2) for a,b in zip(self.cuts[:-1], self.cuts[1:])]
        return [x for t in zip(self.cuts, cuts) for x in t] + [self.cuts[-1]]
    def plot(self, ax, visible=True, plot_color=False, **kwargs):
        if plot_color:
            kwargs['color'] = [self.colors[self.get_cut(f)] for f in self.function]
        return PointCloud.plot(self, ax, visible, **kwargs)

class MetricSample(Sample):
    def __init__(self, points, function, radius, extents, cuts, colors, pad=0, lips=1., parent='test'):
        Sample.__init__(self, points, function, cuts, colors, pad, parent)
        self.extents, self.radius = extents, radius
    def init_plot(self):
        return init_surface(self.extents, self.pad)
    def get_tag(self, args):
        return  f"sample{len(self)}_{format_float(self.radius)}"\
                f"{'-cover' if args.cover else '-union' if args.union else ''}"\
                f"{'-color' if args.color else ''}"\
                f"{'-surf' if args.surf else ''}"
    # TODO redundant
    def plot_cover(self, ax, plot_colors=False, radii=None, radius=None, color=COLOR['red'], zorder=0, **kwargs):
        radii = [self.radius if radius is None else radius for _ in self] if radii is None else radii
        balls = []
        for p,f,r in zip(self.points, self.function, radii):
            cut = self.get_cut(f)
            c = self.colors[cut] if plot_colors else color
            s = plt.Circle(p, r, color=c, zorder=zorder+cut, **kwargs)
            balls.append(s)
            ax.add_patch(s)
        return balls
    def get_rips(self, noim=False, verbose=True):
        radius = self.radius * (1 if noim else 2/np.sqrt(3))
        return RipsComplex(self.points, radius, verbose=verbose)
    def get_delaunay(self, alpha=2e4, verbose=True):
        filter = None if alpha is None else (lambda f: f < alpha)
        return DelaunayComplex(self.points, self.radius, filter, verbose=verbose)
    def get_voronoi(self, alpha=2e4, verbose=True):
        delaunay = self.get_delaunay(alpha, verbose)
        return VoronoiComplex(delaunay, delaunay.get_boundary(), verbose=verbose)
    def plot_complex(self, ax, complex, plot_colors=False, key='sub', color=COLOR['red'], **kwargs):
        if plot_colors:
            kwargs['tri_colors'] = [self.colors[self.get_cut(t.data[key])] for t in complex(2)]
        else:
            kwargs['color'] = color
        return complex.plot(ax, **kwargs)


class MetricSampleData(MetricSample, Data):
    def __init__(self, data, radius, parent, folder, config):
        config['radius'], config['parent'] = radius, parent
        name = f'{parent}-sample{len(data)}-{format_float(radius)}'
        Data.__init__(self, data, name, os.path.join(folder, 'samples'), config=config)
        MetricSample.__init__(self, data[:,:2], data[:,2], **config)
    def smooth(self, p):
        return [p[0]+self.config['lips']*self.radius/OOPS, p[1]-self.config['lips']*self.radius/OOPS]
    def plot_complex_filtration(self, complex, config, tag=None, show=True, save=True, folder='figures', plot_colors=False, dpi=300, hide={}, subsample=None):
        fig, ax = self.init_plot()
        if not (subsample is None or 'subsample' in hide):
            subsample.plot(ax, plot_color=plot_colors, **KWARGS['subsample'])
            if plot_colors:
                subsample.plot(ax, zorder=10, s=10, facecolor='none', edgecolor='black', lw=0.3)
        do_color = {'min' : False if not 'max' in hide else plot_colors, 'max' : plot_colors, "sub" : plot_colors}
        # do_color = {'min' : plot_colors, 'max' : plot_colors, "sub" : plot_colors}
        complex_plt = {k : self.plot_complex(ax, complex, do_color[k], k, **v) for k,v in config.items() if not k in hide}
        for i, t in enumerate(self.get_levels()):
            for d, S in complex.items():
                for s in S:
                    for k, v in complex_plt.items():
                        if s.data[k] <= t and s in v[d]:
                            v[d][s].set_visible(not config[k]['visible'])
            if show:
                plt.pause(0.5)
            if save:
                self.save_plot(folder, dpi, f"{tag}{format_float(t)}")
        plt.close(fig)
    def plot_cover_filtration(self, tag=None, show=True, save=True, folder='figures', plot_colors=False, dpi=300, **kwargs):
        fig, ax = self.init_plot()
        self.plot(ax, **KWARGS['sample'])
        offset_plt = self.plot_cover(ax, plot_colors, visible=False, **kwargs)
        for i, t in enumerate(self.get_levels()):
            for j,f in enumerate(self.function):
                if f <= t:
                    offset_plt[j].set_visible(True)
            if show:
                plt.pause(0.5)
            if save:
                self.save_plot(folder, dpi, f"{tag}{format_float(t)}")
        plt.close(fig)
    def plot_lips_filtration(self, config, tag=None, show=True, save=True, folder='figures', plot_colors=False, dpi=300, hide={}, **kwargs):
        fig, ax = self.init_plot()
        self.plot(ax, **KWARGS['sample'])
        offset_plt = {  'max' : self.plot_cover(ax, plot_colors, self.function/self.config['lips'], **config['max']),
                        'min' : self.plot_cover(ax, plot_colors, self.function/self.config['lips'], **config['min'])}
        for i, t in enumerate(self.get_levels()):
            for j,f in enumerate(self.function):
                fs = {'max' : (t - f) / self.config['lips'], 'min' : (f - t) / self.config['lips']}
                for k,v in offset_plt.items():
                    v[j].set_radius(fs[k] if fs[k] > 0 else 0)
            if show:
                plt.pause(0.5)
            if save:
                self.save_plot(folder, dpi, f"lips-{tag}{format_float(t)}")
        plt.close(fig)
    def get_barcode(self, complex, smooth=True, key='sub', pivot_key=None):
        pivot_key = key if pivot_key is None else pivot_key
        filt = Filtration(complex, key)
        if complex.thresh > self.radius:
            pivot = Filtration(complex, pivot_key, filter=lambda s: s['dist'] <= self.radius)
        else:
            pivot = Filtration(complex, pivot_key)
        hom =  Diagram(complex, filt, pivot=pivot, verbose=True)
        return hom.get_diagram(complex, filt, pivot, self.smooth if smooth else None)
    # def get_lips_sub_barcode(self, complex, smooth=True):
    #     filt = Filtration(complex, 'min')
    #     if complex.thresh > self.radius:
    #         pivot = Filtration(complex, 'max', filter=lambda s: s['dist'] <= self.radius)
    #     else:
    #         pivot = Filtration(complex, 'max')
    #     hom =  Diagram(complex, filt, pivot=pivot, verbose=True)
    #     return hom.get_diagram(complex, filt, pivot, self.smooth if smooth else None)
    # def plot_barcode(self, rips, show=False, save=False, folder='./', _color=None, dpi=300, smooth=True, sep='_', relative=False, **kwargs):
    #     fig, ax = init_barcode()
    #     filt = Filtration(rips, 'sub')
    #     if rips.thresh > self.radius:
    #         pivot = Filtration(rips, 'sub', filter=lambda s: s['dist'] <= self.radius)
    #     else:
    #         pivot = Filtration(rips, 'sub')
    #     hom =  Diagram(rips, filt, pivot=pivot, verbose=True)
    #     dgms = hom.get_diagram(rips, filt, pivot, self.smooth if smooth else None)
    #     barode_plt = plot_barcode(ax, dgms[1], self.cuts, self.colors, **kwargs)
    #     tag = f"barcode{'-relative' if relative else ''}"
    #     if not smooth:
    #         tag += '-nosmooth'
    #     if save: self.save_plot(folder, dpi, tag, sep)
    #     if show: plt.show()
    #     plt.close(fig)
    #     return dgms
    # def plot_lips_barcode(self, rips, show=False, save=False, folder='./', _color=None, dpi=300, smooth=True, sep='_', relative=False, **kwargs):
    #     fig, ax = init_barcode()
    #     filt = Filtration(rips, 'min')
    #     if rips.thresh > self.radius:
    #         pivot = Filtration(rips, 'max', filter=lambda s: s['dist'] <= self.radius)
    #     else:
    #         pivot = Filtration(rips, 'max')
    #     hom =  Diagram(rips, filt, pivot=pivot, verbose=True)
    #     dgms = hom.get_diagram(rips, filt, pivot, self.smooth if smooth else None)
    #     barode_plt = plot_barcode(ax, dgms[1], self.cuts, self.colors, **kwargs)
    #     tag = f"barcode{'-relative' if relative else ''}-lips"
    #     if not smooth:
    #         tag += '-nosmooth'
    #     if save: self.save_plot(folder, dpi, tag, sep)
    #     if show: plt.show()
    #     plt.close(fig)
    #     return dgms
    # def plot_lips_sub_barcode(self, rips, subsample, show=False, save=False, folder='./', _color=None, dpi=300, smooth=True,  sep='_', relative=False, **kwargs):
    #     fig, ax = init_barcode()
    #     filt = Filtration(rips, 'min')
    #     if rips.thresh > self.radius:
    #         pivot = Filtration(rips, 'max', filter=lambda s: s['dist'] <= self.radius)
    #     else:
    #         pivot = Filtration(rips, 'max')
    #     hom =  Diagram(rips, filt, pivot=pivot, verbose=True)
    #     dgms = hom.get_diagram(rips, filt, pivot, self.smooth if smooth else None)
    #     barode_plt = plot_barcode(ax, dgms[1], self.cuts, self.colors, **kwargs)
    #     tag = f"barcode{'-relative' if relative else ''}-lips-sub{len(subsample)}"
    #     if not smooth:
    #         tag += '-nosmooth'
    #     if save: self.save_plot(folder, dpi, tag, sep)
    #     if show: plt.show()
    #     plt.close(fig)
    #     return dgms

class MetricSampleFile(MetricSampleData, DataFile):
    def __init__(self, file_name, json_file=None, radius=None):
        if json_file is None:
            json_file = f'{os.path.splitext(file_name)[0]}.json'
        DataFile.__init__(self, file_name, json_file)
        data, config = self.load_data(), self.load_json()
        radius = config['radius'] if radius is None else radius
        parent, folder = config['parent'], os.path.dirname(file_name)
        MetricSampleData.__init__(self, data, radius, parent, folder, config)
