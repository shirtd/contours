import matplotlib.pyplot as plt
import numpy as np
import os, sys

from contours.config import KWARGS, GAUSS_ARGS

from contours.plot import init_barcode, plot_barcode
from contours.surface import USGSScalarFieldData, GaussianScalarFieldData, ScalarFieldFile
from contours.surface.sample import MetricSampleFile


class RunSample:
    def __init__(self, parser):
        parser.parse_args(namespace=self.__class__)
        self.plot_args = [self.show, self.save, self.folder, self.color, self.dpi]
    # TODO !!
    # def plot_args(self, *args):
    #     return [self.show, self.save, self.folder, self.color, self.dpi] + args
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
        self.plot_args = [self.show, self.save, self.folder, self.color, self.dpi]
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
    def plot_contours(self, sample, complex=None, subsample=None):
        plot_args = self.plot_args.copy()
        if self.lips:
            plot_args += [{'min'} if self.nomin else {'max'} if self.nomax else {}]
        if self.cover or self.union:
            if self.lips:
                sample.plot_lips_filtration(self.get_config(), self.get_tag(), *plot_args)
            else:
                sample.plot_cover_filtration(tag, *plot_args, **KWARGS[self.mode])
        elif subsample is not None:
            sample.plot_complex_filtration(complex, self.get_config(), self.get_tag(subsample), *plot_args)
        elif complex is not None:
            sample.plot_complex_filtration(complex, self.get_config(), self.get_tag(), *plot_args)
    def plot_complex(self, sample, complex, subsample=None):
        fig, ax = sample.init_plot()
        tag = self.get_tag()
        complex_plt = sample.plot_complex(ax, complex, self.color, **KWARGS[self.mode])
        if self.save:
            sample.save_plot(self.folder, self.dpi, tag)
        if self.show:
            print('close plot to exit')
            plt.show()
    def plot_cover(self, sample, subsample=None):
        print('TODO: plot_cover(sample{, subsample})')
