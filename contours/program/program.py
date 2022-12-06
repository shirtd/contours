import matplotlib.pyplot as plt
import numpy as np
import os, sys

from contours.config import KWARGS, GAUSS_ARGS

from contours.surface import USGSScalarFieldData, GaussianScalarFieldData, ScalarFieldFile
from contours.surface.sample import MetricSampleFile


class LoadArgs:
    def __init__(self, parser):
        parser.parse_args(namespace=self.__class__)
        self.plot_args = [self.show, self.save, self.folder, self.dpi]
    # GET OPERATIONS
    def get_surface(args, surf=None):
        if args.gauss:
            name, folder = 'surf', os.path.join('data', 'surf')
            surf = GaussianScalarFieldData(name, folder, args.resolution, args.downsample, **GAUSS_ARGS)
        elif os.path.splitext(args.file)[1] == '.asc':
            surf = USGSScalarFieldData(args.file, args.cuts, args.colors, args.pad, args.downsample)
        elif args.file is not None:
            surf = ScalarFieldFile(args.file, args.json)
        if surf is not None:
            args.folder = os.path.join(args.folder, surf.name)
            if args.save:
                surf.save
        return surf
    # TODO
    def get_barcode(self, surf):
        pass
    # DO OPERATIONS
    def do_sample(self, surf, sample=None):
        if self.greedy:
            sample = surf.greedy_sample(self.thresh, self.mult, self.seed)
        elif self.sample_file is not None:
            sample = MetricSampleFile(self.sample_file)
        if self.sample:
            sample = surf.sample(self.thresh, sample)
        return sample
    # PLOT OPERATIONS (no return?)
    def plot_contours(self, surf):
        surf.plot_contours(*self.plot_args)
    # TODO split get and plot barcode so that plot_barcode has no return
    # # should plot_barcode have no return?
    # # # return the barcode figure object?
    def plot_barcode(self, surf):
        surf.plot_barcode(*self.plot_args, **KWARGS['barcode'])
    def plot_surface(self, surf):
        fig, ax = surf.init_plot()
        surf_plt = surf.plot(ax, zorder=0)
        surf_plt['surface'].set_alpha(0.5)
        if args.save:
            surf.save_plot(args.folder, args.dpi)
        if args.show:
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
        if self.greedy or self.sample:
            if self.show:
                plt.pause(0.1)
            if self.write or input(f'save {sample.name} (y/*)? ') == 'y':
                sample.save()
        elif self.show:
            plt.show()
        plt.close(fig)


class MainArgs:
    def __init__(self, parser):
        parser.parse_args(namespace=self.__class__)
        self.plot_args = [self.show, self.save, self.folder, self.dpi]
    def get_tag(self, suffix=''):
        tag = f"{self.mode}{'' if self.noim else '-im'}"
        if self.lips:
            tag = f"{tag}-lips{'-max' if self.nomin else '-min' if self.nomax else ''}"
            if self.local:
                tag += '-local'
        return f"{tag}{'-color' if self.color else ''}{suffix}"
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
            if args.sub_file is not None:
                return {'min' : {**{'visible' : False}, **KWARGS['min'][self.mode]},
                        'max' : {**{'visible' : False}, **KWARGS['max'][self.mode]}}
            return {'min' : {**{'visible' : False}, **KWARGS['min'][self.mode]},
                    'max' : {**{'visible' : False}, **KWARGS['max'][self.mode]}}
        return {'sub' : {**{'visible' : False}, **KWARGS[self.mode]}}
    def get_complex(self, sample, complex=None):
        if self.rips or self.graph:
            complex = sample.get_rips(self.noim)
        elif self.delaunay:
            complex = sample.get_delaunay(self.alpha)
        elif self.voronoi:
            complex = sample.get_voronoi(self.alpha)
        return complex
    def do_cover(self, sample, tag, subsample=None):
        if self.cover or self.union:
            return sample.plot_lips_filtration(get_config(self), tag, *self.plot_args)
        return sample.plot_cover_filtration(tag, *self.plot_args, **KWARGS[self.mode])
    def do_contours(self, sample, complex, tag, subsample=None):
        plot_args = self.plot_args.copy()
        if self.lips:
            plot_args += [{'min'} if self.nomin else {'max'} if self.nomax else {}]
            if subsample is not None:
                plot_args += [subsample]
        return sample.plot_complex_filtration(complex, self.get_config(), tag, *plot_args)
    def do_barcode(self, complex, tag, subsample=None):
        plot_args = self.plot_args.copy()
        if args.nosmooth:
            tag += '-nosmooth'
            plot_args += [not self.nosmooth]
        if self.lips:
            if subsample is not None:
                return sample.plot_lips_sub_barcode(complex, subsample, *plot_args, **KWARGS['barcode'])
            return sample.plot_lips_barcode(complex, *plot_args, **KWARGS['barcode'])
        return sample.plot_barcode(complex, *plot_args, **KWARGS['barcode'])
    def plot_complex(self, sample, complex, tag):
        fig, ax = sample.init_plot()
        complex_plt = sample.plot_complex(ax, complex, self.color, **KWARGS[self.mode])

        if self.save:
            sample.save_plot(self.folder, self.dpi, tag)

        if self.show:
            print('close plot to exit')
            plt.show()
