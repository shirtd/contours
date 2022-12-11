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
    def plot_contours(self, surf, off_alpha=0.1):
        fig, ax = surf.init_plot()
        surf_plt = surf.plot(ax)
        surf_alpha = [off_alpha for _ in surf.colors]
        cont_alpha = surf_alpha.copy()
        surf_plt['surface'].set_alpha(surf_alpha)
        surf_plt['contours'].set_alpha(cont_alpha)
        if self.show:
            plt.pause(0.5)
        if self.save:
            surf.save_plot(self.folder, self.dpi, format_float(surf.cuts[0]))
        for i, t in enumerate(surf.cuts[1:]):
            cont_alpha[i], surf_alpha[i] = 1., 0.5
            surf_plt['contours'].set_alpha(cont_alpha)
            surf_plt['surface'].set_alpha(surf_alpha)
            if self.show:
                plt.pause(0.5)
            if self.save:
                self.save_plot(self.folder, self.dpi, format_float(t))
        plt.close(fig)
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
