import matplotlib.pyplot as plt
from scipy.spatial import KDTree
import numpy as np
import os, sys

from contours.config import COLOR, KWARGS, GAUSS_ARGS
from contours.config.args import parser

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


if __name__ == '__main__':
    args = LoadArgs(parser)

    surf = args.get_surface()
    if args.contours:
        args.plot_contours(surf)

    barcode_surf = None
    if args.barcode:
        # barcode_surf = args.get_barcode(surf)
        # barcode_surf = args.plot_barcode(surf, **KWARGS['barcode'])
        args.plot_barcode(surf)

    # fig, ax = surf.init_plot()
    # surf_plt = surf.plot(ax, zorder=0)
    # surf_plt['surface'].set_alpha(0.5)
    #
    # if sample is not None:
    #     if args.color:
    #         surf_plt['contours'].set_alpha(0.1)
    #         surf_plt['surface'].set_alpha(0.1)
    #         sample.plot(ax, plot_color=True, **KWARGS['subsample'])
    #         sample.plot(ax, zorder=10, s=10, facecolor='none', edgecolor='black', lw=0.3)
    #     else:
    #         sample.plot(ax, **KWARGS['sample'])
    #     if args.union or args.cover:
    #         sample.plot_cover(ax, **KWARGS['union' if args.union else 'cover'])
    #
    #
    #     if args.save:
    #         sample.save_plot(args.folder, args.dpi)
    #     if args.greedy or args.sample:
    #         if args.show:
    #             plt.pause(0.1)
    #         if args.write or input(f'save {sample.name} (y/*)? ') == 'y':
    #             sample.save()
    #     elif args.show:
    #         plt.show()
    # else:
    #     if args.save:
    #         surf.save_plot(args.folder, args.dpi)
    #     if args.show:
    #         plt.show()
