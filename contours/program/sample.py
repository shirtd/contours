import matplotlib.pyplot as plt
import numpy as np
import os, sys

from contours.config import KWARGS, GAUSS_ARGS

from contours.plot import init_barcode, plot_barcode
from contours.surface import USGSScalarFieldData, GaussianScalarFieldData, ScalarFieldFile
from contours.surface.sample import MetricSampleFile
from ..util import lmap, format_float


class RunSample:
    def __init__(self, parser):
        parser.parse_args(namespace=self.__class__)
    def get_tag(self, subsample=None, suffix=''):
        tag = f"{self.mode}{'-noim' if self.noim else ''}"
        if subsample is not None:
            tag += f"-sub{len(subsample)}"
        if self.lips:
            tag += f"-lips{'-max' if self.nomin else '-min' if self.nomax else ''}"
        tag += '-color' if self.color else ''
        return tag+suffix
    def set_args(self, sample):
        self.parent = sample.parent if self.parent is None else self.parent
        if self.mode is None:
            self.mode = ( 'graph' if self.graph else 'rips' if self.rips
                    else 'delaunay' if self.delaunay else 'voronoi' if self.voronoi
                    else 'union' if self.union else 'cover' )
        self.folder = os.path.join(self.folder, sample.parent, sample.name)
        if self.lips:
            self.folder = os.path.join(self.folder, 'lips')
        self.folder = os.path.join(self.folder, self.mode)
    def get_config(self):
        if self.lips:
            if self.cover or self.union:
                return {'min' : {**{'visible' : not self.nomin}, **KWARGS['min'][self.mode]},
                        'max' : {**{'visible' : not self.nomax}, **KWARGS['max'][self.mode]}}
            if self.sub_file is not None:
                return {'min' : {**{'visible' : False}, **KWARGS['min'][self.mode]},
                        'max' : {**{'visible' : False}, **KWARGS['max'][self.mode]}}
            elif self.voronoi:
                return {'min' : {**{'visible' : False}, **KWARGS['max'][self.mode]},
                        'max' : {**{'visible' : False}, **KWARGS['min'][self.mode]}}
            return {'min' : {**{'visible' : True}, **KWARGS['min'][self.mode]},
                    'max' : {**{'visible' : False}, **KWARGS['max'][self.mode]}}
        return {'sub' : {**{'visible' : False}, **KWARGS[self.mode]}}
    def get_subsample(self, subsample=None):
        if self.lips and self.sub_file is not None:
            subsample = MetricSampleFile(self.sub_file)
        return subsample
    def get_complex(self, sample, subsample=None, complex=None):
        if self.rips or self.graph:
            complex = sample.get_rips(self.noim)
        elif self.delaunay:
            complex = sample.get_delaunay(self.alpha)
        elif self.voronoi:
            complex = sample.get_voronoi(self.alpha)
        if complex is not None:
            complex.sublevels(sample)
            if self.lips:
                if subsample is not None:
                    complex.lips_sub(subsample)
                else:
                    complex.lips(sample, sample.config['lips'], invert_min=self.rmin)
        return complex
    def plot_barcode(self, sample, barcode, dim=1, tag="barcode", **kwargs):
        fig, ax = init_barcode()
        barode_plt = plot_barcode(ax, barcode[dim], sample.cuts, sample.colors, **kwargs)
        if self.save:
            tag = f'{tag}-nosmooth' if self.nosmooth else tag
            sample.save_plot(self.folder, self.dpi, tag)
        if self.show:
            plt.show()
        plt.close(fig)
    def plot_contours(self, sample, complex=None, subsample=None, hide={}):
        if self.lips:
            hide = {'min'} if self.nomin else {'max'} if self.nomax else {}
        if self.cover or self.union:
            if self.lips:
                self.plot_lips_filtration(sample, hide)
            else:
                self.plot_cover_filtration(sample, **KWARGS[self.mode])
        elif complex is not None:
            self.plot_complex_filtration(sample, complex, subsample, hide)
    def plot_complex(self, sample, complex, subsample=None):
        fig, ax = sample.init_plot()
        tag = self.get_tag()
        complex_plt = sample.plot_complex(ax, complex, self.color, **KWARGS[self.mode])
        if self.save:
            sample.save_plot(self.folder, self.dpi, tag)
        if self.show:
            print('close plot to exit')
            plt.show()
    def plot_cover(self, sample):
        fig, ax = sample.init_plot()
        tag = self.get_tag()
        sample.plot(ax, **KWARGS['sample'])
        complex_plt = sample.plot_cover(ax, self.color, **KWARGS[self.mode])
        if self.save:
            sample.save_plot(self.folder, self.dpi, tag)
        if self.show:
            print('close plot to exit')
            plt.show()
    def plot_complex_filtration(self, sample, complex, subsample=None, hide={}):
        fig, ax = sample.init_plot()
        config, tag = self.get_config(), self.get_tag(subsample)
        if not (subsample is None or 'subsample' in hide):
            subsample.plot(ax, plot_color=self.color, **KWARGS['subsample'])
            if self.color:
                subsample.plot(ax, zorder=10, s=10, facecolor='none', edgecolor='black', lw=0.3)
        do_color = {'min' : False if not 'max' in hide else self.color, 'max' : self.color, "sub" : self.color}
        complex_plt = {k : sample.plot_complex(ax, complex, do_color[k], k, **v) for k,v in config.items() if not k in hide}
        for i, t in enumerate(sample.get_levels()):
            for d, S in complex.items():
                for s in S:
                    for k, v in complex_plt.items():
                        if s.data[k] <= t and s in v[d]:
                            v[d][s].set_visible(not config[k]['visible'])
            if self.show:
                plt.pause(0.5)
            if self.save:
                sample.save_plot(self.folder, self.dpi, f"{tag}{format_float(t)}")
        plt.close(fig)
    def plot_cover_filtration(self, sample, **kwargs):
        fig, ax = sample.init_plot()
        config, tag = self.get_config(), self.get_tag()
        sample.plot(ax, **KWARGS['sample'])
        offset_plt = sample.plot_cover(ax, self.color, visible=False, **kwargs)
        for i, t in enumerate(sample.get_levels()):
            for j,f in enumerate(self.function):
                if f <= t:
                    offset_plt[j].set_visible(True)
            if self.show:
                plt.pause(0.5)
            if self.save:
                sample.save_plot(self.folder, self.dpi, f"{tag}{format_float(t)}")
        plt.close(fig)
    def plot_lips_filtration(self, sample, hide={}, **kwargs):
        fig, ax = sample.init_plot()
        config, tag = self.get_config(), self.get_tag()
        sample.plot(ax, **KWARGS['sample'])
        offset_plt = {  'max' : sample.plot_cover(ax, self.color, sample.function/sample.config['lips'], **config['max']),
                        'min' : sample.plot_cover(ax, self.color, sample.function/sample.config['lips'], **config['min'])}
        for i, t in enumerate(sample.get_levels()):
            for j,f in enumerate(sample.function):
                fs = {'max' : (t - f) / sample.config['lips'], 'min' : (f - t) / sample.config['lips']}
                for k,v in offset_plt.items():
                    v[j].set_radius(fs[k] if fs[k] > 0 else 0)
            if self.show:
                plt.pause(0.5)
            if self.save:
                sample.save_plot(self.folder, self.dpi, f"lips-{tag}{format_float(t)}")
        plt.close(fig)
