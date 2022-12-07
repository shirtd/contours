import matplotlib.pyplot as plt
import numpy as np
import os, sys

from contours.config import KWARGS, GAUSS_ARGS

from contours.plot import init_barcode, plot_barcode
from contours.surface import USGSScalarFieldData, GaussianScalarFieldData, ScalarFieldFile
from contours.surface.sample import MetricSampleFile


class RunSurface:
    def __init__(self, parser):
        parser.parse_args(namespace=self.__class__)
        self.plot_args = [self.show, self.save, self.folder, self.dpi]
    def get_surface(self, surf=None):
        if self.gauss:
            name, folder = 'surf', os.path.join('data', 'surf')
            surf = GaussianScalarFieldData(name, folder, self.resolution, self.downsample, **GAUSS_ARGS)
        elif os.path.splitext(self.file)[1] == '.asc':
            surf = USGSScalarFieldData(self.file, self.cuts, self.colors, self.pad, self.downsample)
        elif self.file is not None:
            surf = ScalarFieldFile(self.file, self.json)
        if surf is not None:
            self.folder = os.path.join(self.folder, surf.name)
            self.plot_args = [self.show, self.save, self.folder, self.dpi]
            if self.save:
                surf.save()
        return surf
    def do_sample(self, surf, sample=None):
        if self.greedy:
            sample = surf.greedy_sample(self.thresh, self.mult, self.seed)
        elif self.sample_file is not None:
            sample = MetricSampleFile(self.sample_file)
        if self.sample:
            sample = surf.sample(self.thresh, sample)
        if sample is not None:
            if self.show and not self.write:
                fig, ax = surf.init_plot()
                surf_plt = surf.plot(ax, **KWARGS['surf'])
                sample_plt = sample.plot(ax, **KWARGS['sample'])
                plt.pause(0.1)
            if self.write or input(f'save {sample.name} (y/*)? ') == 'y':
                sample.save()
        return sample
    def plot_barcode(self, surf, barcode, dim=1, tag="barcode", **kwargs):
        fig, ax = init_barcode()
        barode_plt = plot_barcode(ax, barcode[dim], surf.cuts, surf.colors, **kwargs)
        if self.save:
            surf.save_plot(self.folder, self.dpi, tag)
        if self.show:
            plt.show()
        plt.close(fig)
    def plot_contours(self, surf):
        surf.plot_contours(*self.plot_args)
    def plot_surface(self, surf):
        fig, ax = surf.init_plot()
        surf_plt = surf.plot(ax, zorder=0)
        surf_plt['surface'].set_alpha(0.5)
        if self.save:
            surf.save_plot(self.folder, self.dpi)
        if self.show:
            plt.show()
        plt.close(fig)
    def plot_sample(self, surf, sample):
        fig, ax = surf.init_plot()
        surf_plt = surf.plot(ax, zorder=0)
        surf_plt['surface'].set_alpha(0.5)
        if self.color:
            surf_plt['contours'].set_alpha(0.1)
            surf_plt['surface'].set_alpha(0.1)
            sample.plot(ax, plot_color=True, **KWARGS['subsample'])
            sample.plot(ax, zorder=10, s=10, facecolor='none', edgecolor='black', lw=0.3)
        else:
            sample.plot(ax, **KWARGS['sample'])
        if self.union or self.cover:
            sample.plot_cover(ax, **KWARGS['union' if self.union else 'cover'])
        if self.save:
            sample.save_plot(self.folder, self.dpi)
        if self.show:
            plt.show()
        plt.close(fig)

class RunSample:
    def __init__(self, parser):
        parser.parse_args(namespace=self.__class__)
        self.plot_args = [self.show, self.save, self.folder, self.color, self.dpi]
    # TODO
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
    # def plot_complex_filtration(self, sample, complex, config, tag=None, show=True, save=True, folder='figures', plot_colors=False, dpi=300, hide={}, subsample=None):
    #     fig, ax = sample.init_plot()
    #
    #     tag = f'{tag}-{len(subsample)}sub'
    #     if not (subsample is None or 'subsample' in hide):
    #         subsample.plot(ax, plot_color=plot_colors, **KWARGS['subsample'])
    #         if plot_colors:
    #             subsample.plot(ax, zorder=10, s=10, facecolor='none', edgecolor='black', lw=0.3)
    #     # do_color = {'min' : False if not 'max' in hide else plot_colors, 'max' : plot_colors, "sub" : plot_colors}
    #     do_color = {'min' : plot_colors, 'max' : plot_colors, "sub" : plot_colors}
    #     complex_plt = {k : sample.plot_complex(ax, complex, do_color[k], k, **v) for k,v in config.items() if not k in hide}
    #     for t in sample.get_levels():
    #         for k, plots in complex_plt.items():
    #             for s in complex(k):
    #                 if s.data[k] <= t and s in plots:
    #                     plots[s].set_visible(not config[k]['visible'])
    #         if self.show:
    #             plt.pause(0.5)
    #         if self.save:
    #             self.save_plot(self.folder, self.dpi, f"{tag}{format_float(t)}")
    #     plt.close(fig)
