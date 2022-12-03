from scipy.spatial import KDTree
import matplotlib.pyplot as plt
import numpy as np
import os, json

from ..config import COLOR, KWARGS
from ..data import Data, DataFile, Function, PointCloud
from ..util import lmap, format_float
from ..complex import RipsComplex
from ..persistence import Diagram, Filtration
from ..util.grid import lipschitz_grid
from ..util.geometry import coords_to_meters, greedysample
from ..plot import get_sample, init_surface, plot_rips, plot_points, plot_balls, init_barcode, plot_barcode


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
    # TODO
    # def plot(self, ax, plot_color=False, **kwargs)
    #     if plot_color:
    #         kwargs['color'] = [self.colors[self.get_cut(f)] for f in self.function]
    #     return PointCloud.plot(self, ax, **kwargs)
    def plot(self, ax, visible=True, plot_color=False, **kwargs):
        if plot_color:
            kwargs['color'] = [self.colors[self.get_cut(f)] for f in self.function]
        return PointCloud.plot(self, ax, visible, **kwargs)

class MetricSample(Sample):
    def __init__(self, points, function, constants, radius, extents, cuts, colors, pad=0, lips=1., parent='test'):
        Sample.__init__(self, points, function, cuts, colors, pad, parent)
        self.constants, self.extents, self.radius = constants, extents, radius
    def init_plot(self):
        return init_surface(self.extents, self.pad)
    def get_tag(self, args):
        return  f"sample{len(self)}_{format_float(self.radius)}"\
                f"{'-cover' if args.cover else '-union' if args.union else ''}"\
                f"{'-color' if args.color else ''}"\
                f"{'-surf' if args.surf else ''}"
    def plot_cover(self, ax, plot_colors=False, color=COLOR['red'], zorder=0, radius=None, **kwargs):
        balls = []
        radius = self.radius if radius is None else radius
        # kwargs['edgecolor'] = 'none'
        for p,f in zip(self.points, self.function):
            cut = self.get_cut(f)
            c = self.colors[cut] if plot_colors else color
            # s = plt.Circle(p, radius, facecolor=c, zorder=zorder+cut, **kwargs)
            s = plt.Circle(p, radius, color=c, zorder=zorder+cut, **kwargs)
            balls.append(s)
            ax.add_patch(s)
        return balls
    # TODO redundant
    def plot_balls(self, ax, radii, plot_colors=False, color=COLOR['red'], zorder=0, **kwargs):
        balls = []
        kwargs['edgecolor'] = 'none'
        for p,f,r in zip(self.points, self.function, radii):
            cut = self.get_cut(f)
            c = self.colors[cut] if plot_colors else color
            s = plt.Circle(p, r, facecolor=c, zorder=zorder+cut, **kwargs)
            balls.append(s)
            ax.add_patch(s)
        return balls
    def plot_rips(self, ax, rips, plot_colors=False, color=COLOR['red'], key=None, **kwargs):
        if plot_colors:
            if key is None:
                kwargs['tri_colors'] = [self.colors[self.get_cut(self(t).max())] for t in rips(2)]
            else:
                kwargs['tri_colors'] = [self.colors[self.get_cut(t.data[key])] for t in rips(2)]
        else:
            kwargs['color'] = color
        return plot_rips(ax, rips, **kwargs)
    def plot_voronoi(self, ax, complex, plot_colors=False):
        return {e : ax.plot(complex.P[e[0],0], complex.P[e[1],1]) for e in complex(1)}


class MetricSampleData(MetricSample, Data):
    def __init__(self, data, radius, parent, folder, config):
        config['radius'], config['parent'] = radius, parent
        name = f'{parent}-sample{len(data)}-{format_float(radius)}'
        Data.__init__(self, data, name, os.path.join(folder, 'samples'), config=config)
        MetricSample.__init__(self, data[:,:2], data[:,2], data[:,3], **config)
    def smooth(self, p):
        return [p[0]+self.config['lips']*self.radius/OOPS, p[1]-self.config['lips']*self.radius/OOPS]
    def plot_rips_filtration(self, rips, config, tag=None, show=True, save=True,
                            folder='figures', plot_colors=False, dpi=300, subsample=None, hide={}):
        fig, ax = self.init_plot()
        if subsample is None and not 'sample' in hide:
            self.plot(ax, **KWARGS['sample'])
        else:
            if not 'sample' in hide:
                self.plot(ax, **KWARGS['supsample'])
            if not 'subsample' in hide:
                subsample.plot(ax, plot_color=plot_colors, **KWARGS['subsample'])
                if plot_colors:
                    subsample.plot(ax, zorder=10, s=10, facecolor='none', edgecolor='black', lw=0.3)
        ######
        #     plot_colors = False
        # rips_plt = {k : self.plot_rips(ax, rips, plot_colors, **v) for k,v in config.items() if not k in hide}
        do_color = {'min' : False if not 'max' in hide else plot_colors, 'max' : plot_colors, "f" : plot_colors}
        rips_plt = {k : self.plot_rips(ax, rips, do_color[k], **v) for k,v in config.items() if not k in hide}
        for i, t in enumerate(self.get_levels()):
            for d in (1,2):
                for s in rips(d):
                    for k, v in rips_plt.items():
                        if s.data[k] <= t:
                            v[d][s].set_visible(not config[k]['visible'])
            if show:
                plt.pause(0.5)
            if save:
                self.save_plot(folder, dpi, f"{tag}{format_float(t)}")
        plt.close(fig)
    def plot_cover_filtration(self, tag=None, show=True, save=True,
                            folder='figures', plot_colors=False, dpi=300, **kwargs):
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
    def plot_lips_filtration(self, config, tag=None, show=True, save=True,
                            folder='figures', plot_colors=False, dpi=300, **kwargs):
        fig, ax = self.init_plot()
        self.plot(ax, **KWARGS['sample'])
        offset_plt = {  'max' : self.plot_balls(ax, self.function/self.config['lips'], plot_colors, **config['max']),
                        'min' : self.plot_balls(ax, self.function/self.config['lips'], plot_colors, **config['min'])}
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
    def plot_barcode(self, rips, show=False, save=False, folder='./', _color=None, dpi=300, smooth=True, sep='_', relative=False, **kwargs):
        fig, ax = init_barcode()
        filt = Filtration(rips, 'f')
        if rips.thresh > self.radius:
            pivot = Filtration(rips, 'f', filter=lambda s: s['dist'] <= self.radius)
        else:
            pivot = Filtration(rips, 'f')
        hom =  Diagram(rips, filt, pivot=pivot, verbose=True)
        dgms = hom.get_diagram(rips, filt, pivot, self.smooth if smooth else None)
        barode_plt = plot_barcode(ax, dgms[1], self.cuts, self.colors, **kwargs)
        tag = f"barcode{'-relative' if relative else ''}"
        if not smooth:
            tag += '-nosmooth'
        if save: self.save_plot(folder, dpi, tag, sep)
        if show: plt.show()
        plt.close(fig)
        return dgms
    def plot_lips_barcode(self, rips, show=False, save=False, folder='./', _color=None, dpi=300, smooth=True, sep='_', relative=False, **kwargs):
        fig, ax = init_barcode()
        filt = Filtration(rips, 'min')
        if rips.thresh > self.radius:
            pivot = Filtration(rips, 'max', filter=lambda s: s['dist'] <= self.radius)
        else:
            pivot = Filtration(rips, 'max')
        hom =  Diagram(rips, filt, pivot=pivot, verbose=True)
        dgms = hom.get_diagram(rips, filt, pivot, self.smooth if smooth else None)
        barode_plt = plot_barcode(ax, dgms[1], self.cuts, self.colors, **kwargs)
        tag = f"barcode{'-relative' if relative else ''}-lips"
        if not smooth:
            tag += '-nosmooth'
        if save: self.save_plot(folder, dpi, tag, sep)
        if show: plt.show()
        plt.close(fig)
        return dgms
    def plot_lips_sub_barcode(self, rips, subsample, show=False, save=False, folder='./', _color=None, dpi=300, smooth=True,  sep='_', relative=False, **kwargs):
        fig, ax = init_barcode()
        filt = Filtration(rips, 'min')
        if rips.thresh > self.radius:
            pivot = Filtration(rips, 'max', filter=lambda s: s['dist'] <= self.radius)
        else:
            pivot = Filtration(rips, 'max')
        hom =  Diagram(rips, filt, pivot=pivot, verbose=True)
        dgms = hom.get_diagram(rips, filt, pivot, self.smooth if smooth else None)
        barode_plt = plot_barcode(ax, dgms[1], self.cuts, self.colors, **kwargs)
        tag = f"barcode{'-relative' if relative else ''}-lips-sub{len(subsample)}"
        if not smooth:
            tag += '-nosmooth'
        if save: self.save_plot(folder, dpi, tag, sep)
        if show: plt.show()
        plt.close(fig)
        return dgms

class MetricSampleFile(MetricSampleData, DataFile):
    def __init__(self, file_name, json_file=None, radius=None):
        if json_file is None:
            json_file = f'{os.path.splitext(file_name)[0]}.json'
        DataFile.__init__(self, file_name, json_file)
        data, config = self.load_data(), self.load_json()
        radius = config['radius'] if radius is None else radius
        parent, folder = config['parent'], os.path.dirname(file_name)
        MetricSampleData.__init__(self, data, radius, parent, folder, config)
